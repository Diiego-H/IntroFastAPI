""" Account management routes """
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from random import random, randint
from app.crud.user import get_user_by_email, create_user
from app.crud.account import *
from app.models import Account, AccountCreate, AccountCreateDB, AccountMoney, UserCreate

router = APIRouter()

@router.post("/", response_model=Account)
def create_account(session: SessionDep, account_in: AccountCreate) -> Account:
    """
    Create new account (for a user specified by username).
    """
    email = account_in.email
    user = get_user_by_email(session=session, email=email)
    if user is None:
        # If no user with this email, create one
        user_in = UserCreate(email=email, password=account_in.password)
        user = create_user(session=session, user_create=user_in)
    elif get_account(session, user.id):
        # Error if the user has an account
        raise HTTPException(status_code=400, detail=f"An account for {email} already exists")
    
    money = account_in.available_money
    if money is None:
        # Generate available_money (currently random: there is no way to specify it)
        money = round(random()+randint(100, 1000), 2)

    if money < 0:
        # Error if available money is negative
        raise HTTPException(status_code=401, detail=f"Available money cannot be negative")

    # Create account
    return add_account(session, AccountCreateDB(id=user.id, available_money=money))

@router.get("/money", response_model=AccountMoney)
def get_account_money(session: SessionDep, current_user: CurrentUser) -> AccountMoney:
    """
    Get account money.
    """
    # Check account for this user exists
    account = get_account(session, current_user.id)
    if account is None:
        raise HTTPException(status_code=401, detail=f"User {current_user.email} does not have an account")
    
    # Return account money
    return AccountMoney(money=get_money(session, current_user.id))
