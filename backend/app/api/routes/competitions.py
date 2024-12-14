""" Competition management routes """
from fastapi import APIRouter, Depends, HTTPException

from app.crud.competition import *
from app.crud.team import get_team_by_name
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Competition,
    CompetitionOut,
    CompetitionCreateOut,
    CompetitionCreateAPI,
    CompetitionCreateDB,
    CompetitionMessage,
    CompetitionUpdate
)

router = APIRouter()

@router.get("/{competition_name}", response_model=CompetitionOut)
def read_competition(session: SessionDep, competition_name: str) -> Competition | None:
    """
    Get a competition by name.
    """
    competition = get_competition_by_name(session, competition_name)
    if competition is None:
        raise HTTPException(status_code=404, detail=f"Competition {competition_name} not found")
    return competition

@router.get("/", response_model=CompetitionOut)
def read_competition_by_id(session: SessionDep, competition_id: int) -> Competition | None:
    """
    Get a competition by id.
    """
    competition = get_competition(session, competition_id)
    if competition is None:
        raise HTTPException(status_code=404, detail=f"Competition with id {competition_id} not found")
    return competition

@router.post(
    "/", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=CompetitionCreateOut
)
def create_competition(session: SessionDep, competition_in: CompetitionCreateAPI) -> Competition:
    """
    Create new competition.
    """
    # Check competition does not exist
    if get_competition_by_name(session, competition_in.name) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"A competition named {competition_in.name} already exists in the system"
        )
    
    # Get teams for the competition (avoiding repetitions, checking all exist)
    teams = []
    for name in set(competition_in.teams):
        team = get_team_by_name(session, name)
        if team is None:
            raise HTTPException(status_code=401, detail=f"Team {name} not found")
        teams.append(team)

    # Update in object with teams found and create competition
    competition_in = CompetitionCreateDB(name=competition_in.name, category=competition_in.category,
                                         sport=competition_in.sport, teams=teams)
    return add_competition(session, competition_in)

@router.delete(
    "/{competition_name}", 
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CompetitionMessage
)
def delete_competition(session: SessionDep, competition_name: str) -> CompetitionMessage:
    """
    Delete a competition by name.
    """
    # Check competition exists
    competition = get_competition_by_name(session, competition_name)
    if competition is None:
        raise HTTPException(status_code=404, detail=f"Competition {competition_name} not found")
    
    # Remove competition
    remove_competition(session, competition)
    return CompetitionMessage(message="Competition deleted successfully", id=competition.id)

@router.put(
    "/{competition_name}", 
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CompetitionOut
)
def update_competition(session: SessionDep, competition_name: str, competition_in: CompetitionUpdate) -> Competition:
    """
    Update a competition (only name, category and sport).
    """
    # Check competition exists
    competition = get_competition_by_name(session, competition_name)
    if competition is None:
        raise HTTPException(status_code=404, detail=f"Competition {competition_name} not found")

    # Names cannot be repeated
    name = competition_in.name
    if (name is not None and name != competition_name):
        # Check whether competition with name for update exists
        if (get_competition_by_name(session, name) is not None):
            raise HTTPException(
                status_code=400,
                detail=f"A competition named {name} already exists in the system"
            )

    # Update competition
    return modify_competition(session, competition, competition_in)