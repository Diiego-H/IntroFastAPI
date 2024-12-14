""" Account related CRUD methods """
from sqlmodel import Session

from app.models import Account, AccountCreateDB
    
# Get account by id
def get_account(session: Session, id: int) -> Account | None:
    return session.get(Account, id)

# Create account
def add_account(session: Session, account_create: AccountCreateDB) -> Account:
    account = Account.model_validate(account_create)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

# Get money from an account, by id
def get_money(session: Session, id: int) -> float | None:
    account = get_account(session, id)
    return None if account is None else account.available_money
