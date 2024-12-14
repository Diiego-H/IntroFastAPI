""" Competition related CRUD methods """
from sqlmodel import Session, select

from app.models import Competition, CompetitionCreateDB, CompetitionUpdate

# Get competition by id
def get_competition(session: Session, id: int) -> Competition | None:
    return session.get(Competition, id)

# Get competition by name
def get_competition_by_name(session: Session, name: str) -> Competition | None:
    return session.exec(select(Competition).where(Competition.name == name)).first()

# Create competition
def add_competition(session: Session, competition_create: CompetitionCreateDB) -> Competition:
    competition = Competition.model_validate(competition_create)
    session.add(competition)
    session.commit()
    session.refresh(competition)
    return competition

# Remove competition
def remove_competition(session: Session, competition: Competition):
    session.delete(competition)
    session.commit()

# Update competition
def modify_competition(session: Session, competition: Competition, competition_in: CompetitionUpdate) -> Competition:
    competition_data = competition_in.model_dump(exclude_unset=True, exclude_none=True)
    competition.sqlmodel_update(competition_data)
    session.add(competition)
    session.commit()
    session.refresh(competition)
    return competition
