""" Team management routes """
from fastapi import APIRouter, Depends, HTTPException

from app.crud.team import *
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Team,
    TeamsList,
    TeamOut,
    TeamMessage,
    TeamUpdate
)

router = APIRouter()

@router.get("/", response_model=TeamsList)
def read_teams(session: SessionDep) -> TeamsList:
    """
    Get teams list.
    """
    teams = get_all_teams(session)
    return TeamsList(count=len(teams), data=teams)

@router.get("/{team_name}", response_model=TeamOut)
def read_team_by_name(session: SessionDep, team_name: str) -> Team | None:
    """
    Get a team by name.
    """
    team = get_team_by_name(session, team_name)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_name} not found")
    return team

@router.delete(
    "/{team_name}", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=TeamMessage
)
def delete_team_by_name(session: SessionDep, team_name: str) -> TeamMessage:
    """
    Delete a team by name.
    """
    team = get_team_by_name(session, team_name)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_name} not found")
    remove_team(session, team)
    return TeamMessage(message="Team deleted successfully", id=team.id)

@router.put(
    "/{team_name}", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=Team
)
def update_team_by_name(session: SessionDep, team_name: str, team_in: TeamUpdate) -> Team:
    """
    Update a team by name.
    """
    # Check if name for update is used by a different team
    new_name = team_in.name
    if (new_name is not None and new_name != team_name):
        if get_team_by_name(session, new_name):
            raise HTTPException(status_code=403, detail=f"A team named {new_name} already exists in the system")
        
    # Check if there is a team in the database with this name
    team = get_team_by_name(session, team_name)
    if team is None:
        # Create new team (if possible)
        try:
            team = create_team(session, team_in)
        except:
            raise HTTPException(
                status_code=404, 
                detail=f"Team {team_name} not found. Lack of information to create a new one"
            )
    else:
        # Update team
        team = modify_team(session, team, team_in)
        
    return team

@router.put(
    "/", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=Team
)
def update_team_by_id(session: SessionDep, team_id: int, team_in: TeamUpdate) -> Team:
    """
    Update a team by id.
    """
    # Find team specified
    team = get_team(session, team_id)
    team_name = None if team is None else team.name

    # Check if name for update is used by a different team
    new_name = team_in.name
    if (new_name is not None and new_name != team_name):
        if get_team_by_name(session, new_name):
            raise HTTPException(status_code=403, detail=f"A team named {new_name} already exists in the system")
        
    # Check if there is a team in the database with this name
    if team is None:
        # Create new team (if possible)
        try:
            team = create_team_id(session, team_id, team_in)
        except:
            raise HTTPException(
                status_code=404, 
                detail=f"Team with id {team_id} not found. Lack of information to create a new one"
            )
    else:
        # Update team
        team = modify_team(session, team, team_in)
        
    return team