""" Match related CRUD methods """
from sqlmodel import Session, select
from app.models import Match, MatchCreateDB, MatchUpdate
    
# Get all matches
def get_all_matches(session: Session) -> list[Match]:
    return list(session.exec(select(Match)))

# Get match by id
def get_match_by_id(session: Session, id: int) -> Match | None:
    return session.get(Match, id)

# Create match
def add_match(session: Session, match_create: MatchCreateDB) -> Match:
    match = Match.model_validate(match_create)
    session.add(match)
    session.commit()
    session.refresh(match)
    return match

# Remove match
def remove_match(session: Session, match: Match):
    session.delete(match)
    session.commit()

# Update match
def modify_match(session: Session, match: Match, match_in: MatchUpdate) -> Match:
    match_data = match_in.model_dump(exclude_unset=True, exclude_none=True)
    match.sqlmodel_update(match_data)
    session.add(match)
    session.commit()
    session.refresh(match)
    return match