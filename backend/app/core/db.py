""" Database configuration """
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import (
    AccountCreateDB, User, UserCreate, TeamUpdate, MatchCreateDB, CompetitionCreateDB, 
    CategoryEnum, SportEnum
)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if user is None:
        user_in = UserCreate(email=settings.FIRST_SUPERUSER, is_superuser=True,
                             password=settings.FIRST_SUPERUSER_PASSWORD, is_active=True)
        user = crud.user.create_user(session=session, user_create=user_in)
        crud.account.add_account(session, AccountCreateDB(id=user.id, available_money=99999))

    # Add football data
    local = crud.team.create_team(session, TeamUpdate(name="Arsenal", country="England", description="Best team"))
    visitor = crud.team.create_team(session, TeamUpdate(name="Liverpool", country="England", description="Worst team"))
    competition_in = CompetitionCreateDB(name="EFL championship", category=CategoryEnum.SENIOR,
                                         sport=SportEnum.FOOTBALL, teams=[local, visitor])
    c = crud.competition.add_competition(session, competition_in)
    match_in = MatchCreateDB(date="30/05/2024", price=100, number_of_seats=50000, competition=c,
                             total_available_tickets=50000, local_team=local, visitor_team=visitor)
    crud.match.add_match(session, match_in)
    match_in.date = "31/05/2024"
    match_in.visitor_team = local
    match_in.local_team = visitor
    crud.match.add_match(session, match_in)

    # Add volleyball data
    local = crud.team.create_team(session, TeamUpdate(name="Espanyol", country="Spain"))
    visitor = crud.team.create_team(session, TeamUpdate(name="Cubelles", country="Spain"))
    competition_in = CompetitionCreateDB(name="Catalan league", category=CategoryEnum.JUNIOR,
                                         sport=SportEnum.VOLLEYBALL, teams=[local, visitor])
    c = crud.competition.add_competition(session, competition_in)
    match_in = MatchCreateDB(date="01/06/2024", price=5, number_of_seats=200, competition=c,
                             total_available_tickets=200, local_team=local, visitor_team=visitor)
    crud.match.add_match(session, match_in)
    match_in.date = "02/06/2024"
    match_in.visitor_team = local
    match_in.local_team = visitor
    crud.match.add_match(session, match_in)

    # Add futsal data
    local = crud.team.create_team(session, TeamUpdate(name="Spain", country="Spain"))
    visitor = crud.team.create_team(session, TeamUpdate(name="Norway", country="Norway"))
    competition_in = CompetitionCreateDB(name="UEFA championship", category=CategoryEnum.SENIOR,
                                         sport=SportEnum.FUTSAL, teams=[local, visitor])
    c = crud.competition.add_competition(session, competition_in)
    match_in = MatchCreateDB(date="03/06/2024", price=50, number_of_seats=8000, competition=c,
                             total_available_tickets=8000, local_team=local, visitor_team=visitor)
    crud.match.add_match(session, match_in)
    match_in.date = "04/06/2024"
    match_in.visitor_team = local
    match_in.local_team = visitor
    crud.match.add_match(session, match_in)

    # Add basketball data
    local = crud.team.create_team(session, TeamUpdate(name="Denmark", country="Denmark"))
    visitor = crud.team.create_team(session, TeamUpdate(name="Italy", country="Italy"))
    competition_in = CompetitionCreateDB(name="Eurocup", category=CategoryEnum.SENIOR,
                                         sport=SportEnum.BASKETBALL, teams=[local, visitor])
    c = crud.competition.add_competition(session, competition_in)
    match_in = MatchCreateDB(date="04/06/2024", price=125, number_of_seats=10000, competition=c,
                             total_available_tickets=10000, local_team=local, visitor_team=visitor)
    crud.match.add_match(session, match_in)
    match_in.date = "05/06/2024"
    match_in.visitor_team = local
    match_in.local_team = visitor
    crud.match.add_match(session, match_in)
