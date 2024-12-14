import random
import string

from app.core.security import get_password_hash
from app.models.competition import Competition, CompetitionCreateDB, CategoryEnum, SportEnum
from app.models.team import Team
from app.models.match import Match, MatchCreateDB
from app.models.order import Account, AccountCreateDB, Order, OrderCreateDB
from app.models.user import UserCreate, User
import app.crud
from fastapi.testclient import TestClient
from app.core.config import settings
from sqlmodel import Session

def random_id() -> int:
    return random.randint(10000, 1000000)

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))

def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"

def random_date() -> str:
    d = "".join(random.choices("0 1 2".split()) + random.choices("1 2 3 4 5 6 7 8".split()))
    m = random.choice("1 2 3 4 5 6 7 8 9 10 11 12".split())
    y = "2024"
    return f"{d}/{m}/{y}"

def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

def create_random_competition(db: Session) -> Competition:
    competition_in = CompetitionCreateDB(name=random_lower_string(), category=CategoryEnum.SENIOR,
                                         sport=SportEnum.FUTSAL, teams=[])
    competition = Competition.model_validate(competition_in, update={"id" : random_id()})
    db.add(competition)
    db.commit()
    db.refresh(competition)
    return competition

def create_random_team(db: Session) -> Team:
    data = {"id": random_id(), "name": random_lower_string(), "country": random_lower_string()}
    team = Team.model_validate(data)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

def create_random_match(db: Session) -> Match:
    # Create teams and competition for match
    t1 = create_random_team(db)
    t2 = create_random_team(db)
    competition = create_random_competition(db)
    competition.teams = [t1, t2]
    db.commit()
    db.refresh(competition)

    # Create match
    seats = random.randint(30, 1000)
    match_in = MatchCreateDB(date=random_date(), number_of_seats=seats,
                             price=round(random.random()+random.randint(5, 100), 2),
                             total_available_tickets=seats, competition=competition,
                             local_team=t1, visitor_team=t2)
    match = Match.model_validate(match_in, update={"id": random_id()})
    db.add(match)
    db.commit()
    db.refresh(match)
    return match
    
def delete_match(db: Session, match: Match) -> None:
    # Delete objects in order of dependency to avoid errors due to foreign keys
    c_id = match.competition_id
    l_id = match.local_id
    v_id = match.visitor_id
    db.delete(match)
    db.delete(db.get(Competition, c_id))
    db.delete(db.get(Team, l_id))
    db.delete(db.get(Team, v_id))
    db.commit()

def create_account(db: Session, email: str, password: str, money: float) -> Account:
    # Create user
    u = app.crud.user.create_user(session=db, user_create=UserCreate(email=email, password=password))

    # Create account
    return app.crud.account.add_account(session=db, account_create=AccountCreateDB(id=u.id, available_money=money))

def create_random_user(db: Session) -> User:
    user_in = UserCreate(email=random_email(), password=random_lower_string())
    user = User.model_validate(user_in, update={"id": random_id(),
        "hashed_password": get_password_hash(user_in.password)}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_random_account(db: Session) -> Account:
    # Create user
    user = create_random_user(db)

    # Create account
    account_in = AccountCreateDB(id=user.id, available_money=random.randint(100,1000))
    account = Account.model_validate(account_in)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def delete_account(db: Session, account: Account) -> None:
    # Delete account first to avoid errors due to foreign key constraint
    id = account.id
    db.delete(account)
    db.delete(db.get(User, id))
    db.commit()

def get_account_email(db: Session, account: Account) -> str:
    return db.get(User, account.id).email

def create_random_order(db: Session) -> Order:
    # Create match and account
    m = create_random_match(db)
    a = create_random_account(db)

    # Order will be for 1 ticket, modify account & match accordingly
    m.total_available_tickets -= 1
    a.available_money = m.price
    db.commit()
    db.refresh(m)
    db.refresh(a)

    # Create order
    order_in = OrderCreateDB(match=m, tickets_bought=1, account=a)
    order = Order.model_validate(order_in)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def delete_order(db: Session, order: Order) -> None:
    # Changes are commited in delete_account & delete_match
    a_id = order.account_id
    m_id = order.match_id
    db.delete(order)
    delete_account(db, db.get(Account, a_id))
    delete_match(db, db.get(Match, m_id))