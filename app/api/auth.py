from datetime import datetime, timedelta
from typing import Literal, Optional, List, Union
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    FastAPI,
    status,
    Response,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database import SessionLocal
from app.api import models


router = APIRouter()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Fake key for testing
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180


admin_allowed_roles = ["admin"]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: Optional[bool] = None
    role: Optional[str] = None
    clients_list_id: Optional[List[str]] = None


class UserInDB(User):
    hashed_password: str


class OAuth2PasswordCookie(OAuth2PasswordBearer):
    """OAuth2 password flow with token in a httpOnly cookie."""

    def __init__(self, *args, token_name: str = "jwt_token", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._token_name = token_name

    @property
    def token_name(self) -> str:
        """Get the name of the token's cookie."""
        return self._token_name

    async def __call__(self, request: Request) -> str:
        """Extract and return a JWT from the request cookies.
        Raises:
            HTTPException: 403 error if no token cookie is present.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = request.cookies.get(self._token_name)
        if not token:
            raise credentials_exception
        return token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordCookie(tokenUrl="/auth/token")

app = FastAPI()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    """Get User from database by username"""

    db = SessionLocal()
    user = db.query(models.Users).filter_by(username=username).first()
    if user is not None:
        user_dict = dict(user.__dict__)
        db.close()
        return UserInDB(**user_dict)
    db.close()


def authenticate_user(username: str, password: str) -> Union[UserInDB, Literal[False]]:
    """Return User if the username exists and the password is correct."""

    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Return the user from the token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:  # this error includes expired payload.exp
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the user is active and return the user."""

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def verify_is_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role not in admin_allowed_roles:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return current_user


@router.post("/token", response_model=User)
async def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
) -> UserInDB:
    """Login and return a JWT token in a cookie."""

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # httponly = True, secure = True for production, delete samesite for production
    response.set_cookie(
        key="jwt_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        httponly=True,
        samesite="Lax",
        secure=False,
    )
    return user


@router.post("/login", response_model=User)
async def login_active_user(
    response: Response, current_user: User = Depends(get_current_active_user)
) -> User:
    """Check cookie for authentication, refresh cookie's token if it's valid.
    This is also being used for refreshing access token on the frontend.
    """

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )

    # httponly = True, secure = True, delete samesite for production
    response.set_cookie(
        key="jwt_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        httponly=True,
        samesite="Lax",
        secure=False,
    )
    return current_user


@router.post("/logout")
async def logout_user(
    response: Response, current_user: User = Depends(get_current_active_user)
) -> dict[str, str]:
    """Sign out, set token to expired"""

    access_token_expires = timedelta(minutes=-15)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    # httponly = True, secure = True, delete samesite for production
    response.set_cookie(
        key="jwt_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        httponly=True,
        samesite="Lax",
        secure=False,
    )
    return {"message": "Successfully logged out"}
