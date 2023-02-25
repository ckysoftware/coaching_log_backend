# Coaching Log Backend

## Local development

1. Initialize the fake postgres database

    ```bash
    python fake_db_sql.py
    ```

2. Start the server

    ```bash
    uvicorn main:app --reload
    ```

3. Access the Swagger Page

    * [http://localhost:8000/docs](https://localhost:8000/docs)

## Functions

1. Login with username and password, or session with cookies
2. Role-based access control
3. User and client
    1. Create
    2. Edit
    3. List
4. Assigning client to user (coach)
5. Coaching logs:
    1. Create
    2. Edit
    3. Lock
    4. List
6. Reimbursement of coaching sessions
7. Change password
8. Sign out
