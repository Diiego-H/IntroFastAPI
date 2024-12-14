from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import UserCreate
from app.tests.utils.utils import random_email, random_lower_string
from app.core.config import settings
from app.crud.account import get_account
from app.crud.user import get_user_by_email, create_user

def test_create_account(client: TestClient, db: Session) -> None:
    email = random_email()
    pwd = random_lower_string()

    # Create an account for an unexisting user (SUCCESS)
    data = {"email": email, "password": pwd}
    r = client.post(f"{settings.API_V1_STR}/account/", json=data)
    assert r.status_code == 200
    account = r.json()
    assert account["available_money"] >= 0

    # Check account identifier equals user's
    id1 = r.json()["id"]
    user1 = get_user_by_email(session=db, email=email)
    assert id1
    assert id1 == user1.id

    # Try to create another account for the same user
    r = client.post(f"{settings.API_V1_STR}/account/", json=data)
    assert r.status_code == 400
    assert r.json() == {"detail": f"An account for {email} already exists"}

    # Create new user
    user_in = UserCreate(email=random_email(), password=random_lower_string())
    user2 = create_user(session=db, user_create=user_in)

    # Try to create an account for this user with negative money
    data = {"email": user_in.email, "password": user_in.password, "available_money": -5}
    r = client.post(f"{settings.API_V1_STR}/account/", json=data)
    assert r.status_code == 401
    assert r.json() == {"detail": "Available money cannot be negative"}

    # Create an account for this user specifying money (SUCCESS)
    data["available_money"] = 5000
    r = client.post(f"{settings.API_V1_STR}/account/", json=data)
    assert r.status_code == 200
    account = r.json()
    assert account["available_money"] == data["available_money"]

    # Check account identifier equals user's
    id2 = r.json()["id"]
    assert id2
    assert id2 == user2.id

    # Delete data created
    db.delete(get_account(db,id1))
    db.delete(get_account(db,id2))
    db.delete(user1)
    db.delete(user2)
    db.commit()

def test_get_money(client: TestClient, normal_user_token_headers: dict[str, str],
                   superuser_token_headers: dict[str, str], db: Session) -> None:
    # Try to get current money unauthorized
    r = client.get(f"{settings.API_V1_STR}/account/money")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to get money for an inexistent user
    h = {"Authorization": f"Bearer {random_lower_string()}"}
    r = client.get(f"{settings.API_V1_STR}/account/money/", headers=h)
    assert r.status_code == 403
    assert r.json() == {"detail": "Could not validate credentials"}

    # Try to get money for a user without account
    r = client.get(f"{settings.API_V1_STR}/account/money/", headers=normal_user_token_headers)
    assert r.status_code == 401
    assert r.json() == {"detail": f"User {settings.EMAIL_TEST_USER} does not have an account"}

    # Get account of first superuser
    assert get_user_by_email(session=db, email=settings.FIRST_SUPERUSER) is not None
    first_account = get_account(db, get_user_by_email(session=db, email=settings.FIRST_SUPERUSER).id)

    # Get first superuser money
    r = client.get(f"{settings.API_V1_STR}/account/money", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json() == {"money": first_account.available_money}