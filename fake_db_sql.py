from app.database import SessionLocal, engine
from app.api import models
from app.api.auth import get_password_hash


def reset_tables():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


def test():
    db = SessionLocal()
    # test add user and client and relationship
    user = models.Users(
        username="first_user",
        hashed_password=get_password_hash("123123"),
        first_name="first",
        last_name="last",
        email="EMAIL",
        role="admin",
        created_by=None,
    )
    user2 = models.Users(
        username="second_user",
        hashed_password=get_password_hash("123123"),
        first_name="first2",
        last_name="last2",
        email="EMAIL2",
        role="coach",
        created_by="first_user",
    )
    # print(user)
    db.add(user)
    db.add(user2)
    try:
        db.commit()
    except Exception as e:
        print(e.__dict__.keys())
        print(e.orig)
        # print(type(e))
    # db.commit()
    db.close()
    return


def initialize_fake_db():
    db = SessionLocal()
    fake_user_1 = models.Users(
        username="fake_user_1",
        hashed_password=get_password_hash("123123"),
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        role="admin",
        created_by="fake_user_1",
    )
    db.add(fake_user_1)
    fake_user_2 = models.Users(
        username="fake_user_2",
        hashed_password=get_password_hash("123123"),
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        role="admin",
        created_by="fake_user_2",
    )
    db.add(fake_user_1)
    db.add(fake_user_2)
    db.commit()

    client_1 = models.Clients(
        id=1,
        coach_username=None,
        first_name="Client",
        last_name="1",
        email="client 1 email",
        mobile_phone="+852 0001",
        sex="F",
        age=18,
        current_location="HK",
        created_by="fake_user_1",
    )
    client_2 = models.Clients(
        id=2,
        coach_username="fake_user_1",
        first_name="Client",
        last_name="2",
        email="client 2 email",
        mobile_phone="+852 0002",
        sex="F",
        age=18,
        current_location="HK",
        created_by="fake_user_1",
    )
    client_3 = models.Clients(
        id=3,
        coach_username="fake_user_1",
        first_name="Client",
        last_name="with locked log",
        email="client 3 email",
        mobile_phone="+852 0003",
        sex="F",
        age=18,
        current_location="HK",
        created_by="fake_user_1",
    )
    client_5 = models.Clients(
        id=5,
        coach_username="fake_user_1",
        first_name="Client",
        last_name="5",
        email="client 5 email",
        mobile_phone="+852 0005",
        sex="F",
        age=18,
        current_location="HK",
        created_by="fake_user_1",
    )
    client_7 = models.Clients(
        id=7,
        coach_username="fake_user_1",
        first_name="Client",
        last_name="7",
        email="client 7 email",
        mobile_phone="+852 0007",
        sex="F",
        age=18,
        current_location="HK",
        created_by="fake_user_1",
    )
    db.add(client_1)
    db.add(client_2)
    db.add(client_3)
    db.add(client_5)
    db.add(client_7)
    db.commit()

    log_1 = models.Coaching_logs(
        client_id=2,
        version="1.1",
        data={
            "ansDate": "2021-05-01T16:00:00.000Z",
            "ansSessionFormat": "Online",
            "ansMeetingVenue": "N/A",
            "ansQ1Introduction": "1 Q1",
            "ansQ2Dermatology": "1 Q2",
            "ansQ3Pharmacology": "1 Q3",
            "ansQ4Nutrition": "1 Q4",
            "ansQ5Stress": "1 Q5",
            "ansQ6Sleep": "1 Q6",
            "ansQ7Exercise": "1 Q7",
            "ansQ8Environment": "1 Q8",
            "ansQ9Others": "1 Q9",
        },
        created_by="fake_user_1",
        edited_by="fake_user_1",
    )
    log_2 = models.Coaching_logs(
        client_id=3,
        version="1.1",
        locked=True,
        data={
            "ansDate": "2021-05-05T16:00:00.000Z",
            "ansSessionFormat": "Online",
            "ansMeetingVenue": "N/A",
            "ansQ1Introduction": "2 Q1",
            "ansQ2Dermatology": "2 Q2",
            "ansQ3Pharmacology": "2 Q3",
            "ansQ4Nutrition": "2 Q4",
            "ansQ5Stress": "2 Q5",
            "ansQ6Sleep": "2 Q6",
            "ansQ7Exercise": "2 Q7",
            "ansQ8Environment": "2 Q8",
            "ansQ9Others": "2 Q9",
        },
        created_by="fake_user_1",
        edited_by="fake_user_1",
    )
    log_3 = models.Coaching_logs(
        client_id=3,
        version="1.1",
        data={
            "ansDate": "2021-05-11T16:00:00.000Z",
            "ansSessionFormat": "Online",
            "ansMeetingVenue": "N/A",
            "ansQ1Introduction": "3 Q1",
            "ansQ2Dermatology": "3 Q2",
            "ansQ3Pharmacology": "3 Q3",
            "ansQ4Nutrition": "3 Q4",
            "ansQ5Stress": "3 Q5",
            "ansQ6Sleep": "3 Q6",
            "ansQ7Exercise": "3 Q7",
            "ansQ8Environment": "3 Q8",
            "ansQ9Others": "3 Q9",
        },
        created_by="fake_user_1",
        edited_by="fake_user_1",
    )
    log_4 = models.Coaching_logs(
        client_id=5,
        version="1.1",
        data={
            "ansDate": "2021-05-15T16:00:00.000Z",
            "ansSessionFormat": "Online",
            "ansMeetingVenue": "N/A",
            "ansQ1Introduction": "4 Q1",
            "ansQ2Dermatology": "4 Q2",
            "ansQ3Pharmacology": "4 Q3",
            "ansQ4Nutrition": "4 Q4",
            "ansQ5Stress": "4 Q5",
            "ansQ6Sleep": "4 Q6",
            "ansQ7Exercise": "4 Q7",
            "ansQ8Environment": "4 Q8",
            "ansQ9Others": "4 Q9",
        },
        created_by="fake_user_1",
        edited_by="fake_user_1",
    )
    log_5 = models.Coaching_logs(
        client_id=7,
        version="1.1",
        data={
            "ansDate": "2021-05-20T16:00:00.000Z",
            "ansSessionFormat": "Face-to-face",
            "ansMeetingVenue": "Dream Impact",
            "ansQ1Introduction": "5 Q1",
            "ansQ2Dermatology": "5 Q2",
            "ansQ3Pharmacology": "5 Q3",
            "ansQ4Nutrition": "5 Q4",
            "ansQ5Stress": "5 Q5",
            "ansQ6Sleep": "5 Q6",
            "ansQ7Exercise": "5 Q7",
            "ansQ8Environment": "5 Q8",
            "ansQ9Others": "5 Q9",
        },
        created_by="fake_user_1",
        edited_by="fake_user_1",
    )
    db.add(log_1)
    db.add(log_2)
    db.add(log_3)
    db.add(log_4)
    db.add(log_5)
    db.commit()
    client_dq1 = models.Client_discovery_questionnaire(
        client_id=1, version="1.1", data=list([["Q1", "Q2"], ["A1", "A2"]])
    )
    client_dq2 = models.Client_discovery_questionnaire(
        client_id=2, version="1.1", data=list([["Q1", "Q2"], ["A1", "A2"]])
    )
    client_dq3 = models.Client_discovery_questionnaire(
        client_id=3, version="1.1", data=list([["Q1", "Q2"], ["A1", "A2"]])
    )
    client_dq5 = models.Client_discovery_questionnaire(
        client_id=5, version="1.1", data=list([["Q1", "Q2"], ["A1", "A2"]])
    )
    client_dq7 = models.Client_discovery_questionnaire(
        client_id=7, version="1.1", data=list([["Q1", "Q2"], ["A1", "A2"]])
    )
    db.add(client_dq1)
    db.add(client_dq2)
    db.add(client_dq3)
    db.add(client_dq5)
    db.add(client_dq7)
    db.commit()

    reim_1 = models.Coaching_log_reimbursement(
        coaching_log_id=1,
        reimbursed_to="fake_user_1",
    )

    reim_2 = models.Coaching_log_reimbursement(
        coaching_log_id=2,
        reimbursed_to="fake_user_1",
    )
    reim_3 = models.Coaching_log_reimbursement(
        coaching_log_id=3,
        reimbursed_to="fake_user_1",
    )
    reim_4 = models.Coaching_log_reimbursement(
        coaching_log_id=4,
        reimbursed_to="fake_user_1",
    )
    reim_5 = models.Coaching_log_reimbursement(
        coaching_log_id=5,
        reimbursed_to="fake_user_1",
    )
    db.add(reim_1)
    db.add(reim_2)
    db.add(reim_3)
    db.add(reim_4)
    db.add(reim_5)
    db.commit()

    db.close()
    return


if __name__ == "__main__":
    reset_tables()
    initialize_fake_db()
