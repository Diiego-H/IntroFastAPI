from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlmodel import Session
from app.crud.account import *
from app.tests.utils.utils import random_email, random_lower_string, random_id, create_random_account
from app.crud.user import create_user
from app.models import UserCreate
from pytest import raises

def test_add_get_account(db: Session) -> None:
    # Add user
    user_in = UserCreate(email=random_email(), password=random_lower_string())
    user = create_user(session=db, user_create=user_in)

    # Get inexistent account
    assert get_account(db, user.id) is None

    # Try to create account with negative money
    account_in = AccountCreateDB(id=user.id, available_money=-5)
    with raises(ValidationError):
        add_account(db, account_in)

    # Add account
    account_in.available_money = 30
    account = add_account(db, account_in)
    assert account
    assert account.id == user.id
    assert account.available_money == 30

    # Get existent account
    account_got = get_account(db, user.id)
    assert account_got

    # Check persistence
    assert jsonable_encoder(account) == jsonable_encoder(account_got)

    # Delete data created
    db.delete(account_got)
    db.delete(user)
    db.commit()

def test_get_money(db: Session) -> None:
    # Try to get money for inexistent account
    assert get_money(db, random_id()) is None

    # Create account
    a = create_random_account(db)

    # Get its money
    assert a.available_money == get_money(db, a.id)

    # Delete data created
    db.delete(a)
    db.commit()
