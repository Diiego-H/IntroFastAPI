""" Team related CRUD methods """
from sqlmodel import Session, select

from app.models import Team, TeamUpdate

# Get all teams
def get_all_teams(session: Session) -> list[Team]:
    return list(session.exec(select(Team)))

# Get team by id
def get_team(session: Session, id: int) -> Team | None:
    return session.get(Team, id)

# Get team with given name
def get_team_by_name(session: Session, name: str) -> Team | None:
    return session.exec(select(Team).where(Team.name == name)).first()

# Remove team
def remove_team(session: Session, team: Team):
    session.delete(team)
    session.commit()

# Update team
def modify_team(session: Session, team: Team, team_in: TeamUpdate) -> Team:
    team_data = team_in.model_dump(exclude_unset=True, exclude_none=True)
    team.sqlmodel_update(team_data)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team

# Create team
def create_team(session: Session, team_in: TeamUpdate) -> Team:
    team = Team.model_validate(team_in)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team

# Create team with given id
def create_team_id(session: Session, team_id: int, team_in: TeamUpdate) -> Team:
    team = Team.model_validate(team_in, update={"id": team_id})
    session.add(team)
    session.commit()
    session.refresh(team)
    return team