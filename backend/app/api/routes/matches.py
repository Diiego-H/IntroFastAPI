""" Match management routes """
from fastapi import APIRouter, Depends, HTTPException

from app.crud.match import *
from app.crud.team import get_team
from app.crud.competition import get_competition
from app.api.deps import SessionDep, get_current_active_superuser
from app.models.match import *

router = APIRouter()

@router.get("/", response_model=MatchesList)
def read_matches(session: SessionDep) -> MatchesList:
    """
    Get matches list.
    """
    # Get list of matches with the information needed for frontend
    matches = []
    for match in get_all_matches(session):
        local = MatchTeamJSON(id=match.local_id, 
                              name=match.local_team.name, 
                              country=match.local_team.country)
        visitor = MatchTeamJSON(id=match.visitor_id, 
                                name=match.visitor_team.name, 
                                country=match.visitor_team.country)
        competition = MatchCompetitionJSON(name=match.competition.name,
                                           category=match.competition.category,
                                           sport=match.competition.sport)
        matches.append(MatchJSON(id=match.id, local=local, visitor=visitor, date=match.date,
                                 tickets=match.total_available_tickets, competition=competition,  
                                 price=match.price))
        
    return MatchesList(matches=matches)


# NOTE: Un match no té un nom que l'identifiqui, fem les operacions per ID.
@router.get("/{match_id}", response_model=MatchOut)
def read_match_by_id(session: SessionDep, match_id: int) -> Match | None:
    """
    Get a match by id.
    """
    match = get_match_by_id(session, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return match


@router.post(
    "/", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=MatchMessage
)
def create_match(session: SessionDep, match_in: MatchCreate) -> MatchMessage:
    """
    Create new match.
    """
    #TODO: CHECK DATE FORMAT!!

    # Price up to 2 decimal digits
    price = round(match_in.price, 2)

    # If the price is negative, raise an exception
    if price < 0:
        raise HTTPException(status_code=402, detail="Price cannot be negative")
    
    # If the number of seats is negative, raise an exception
    if match_in.number_of_seats < 0:
        raise HTTPException(status_code=403, detail="The number of seats cannot be negative")
    
    if match_in.total_available_tickets is None:
        # Number of seats by default
        match_in.total_available_tickets = match_in.number_of_seats
    elif match_in.total_available_tickets < 0:
        # Negative available tickets
        raise HTTPException(status_code=404, detail="Tickets available cannot be negative")
    elif match_in.total_available_tickets > match_in.number_of_seats:
        # Available tickets greater than number of seats
        raise HTTPException(status_code=405, detail="More available tickets than number of seats")
    
    local_id = match_in.local_id
    visitor_id = match_in.visitor_id

    # The local and visitor teams must be different
    if local_id == visitor_id:
        raise HTTPException(
            status_code=406, 
            detail="The local and visitor teams must be different"
        )

    # The local team must exist
    local = get_team(session, local_id)
    if local is None:
        raise HTTPException(status_code=407, detail=f"The local team does not exist")
    
    # The visitor team must exist
    visitor = get_team(session, visitor_id)
    if visitor is None:
        raise HTTPException(status_code=408, detail="The visitor team does not exist")
    
    # The competition must exist
    competition = get_competition(session, match_in.competition_id)
    if competition is None:
        raise HTTPException(status_code=409, detail="The competition does not exist")
    
    # Teams must be registered in competition
    registered_ids = set([team.id for team in competition.teams])
    if local_id not in registered_ids:
        raise HTTPException(
            status_code=410, 
            detail="The local team is not registered in the competition"
        )
    elif visitor_id not in registered_ids:
        raise HTTPException(
            status_code=411, 
            detail="The visitor team is not registered in the competition"
        )
    
    # Create match and return successful message
    match_in = MatchCreateDB(date=match_in.date, price=price, competition=competition,
                             number_of_seats=match_in.number_of_seats,
                             total_available_tickets=match_in.total_available_tickets, 
                             local_team=local, visitor_team=visitor)
    match = add_match(session, match_in)
    return MatchMessage(message="Match created successfully", id=match.id)


@router.delete(
    "/{match_id}", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=MatchMessage
)
def delete_match(session: SessionDep, match_id: int) -> MatchMessage:
    """
    Delete a match by id.
    """
    # Check match exists
    match = get_match_by_id(session, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    
    # Remove match and return message
    remove_match(session, match)
    return MatchMessage(message="Match deleted successfully", id=match_id)


@router.put(
    "/{match_id}", 
    dependencies=[Depends(get_current_active_superuser)], 
    response_model=MatchOut
)
def update_match(session: SessionDep, match_id: int, match_in: MatchUpdate) -> Match:
    """
    Update a match.
    """
    # TODO: CHECK DATE FORMAT!!

    # Check match exists
    match = get_match_by_id(session, match_id)
    if match is None:
        raise HTTPException(status_code=400, detail=f"Match {match_id} not found")
    
    # Price up to 2 decimals
    price = None if match_in.price is None else round(match_in.price, 2)

    # If the price is negative in the update data, raise an exception
    if price is not None and price < 0:
        raise HTTPException(status_code=402, detail="Price cannot be negative")

    # Check tickets availability
    available = match_in.total_available_tickets
    current = match.total_available_tickets
    if available is not None and available > current:
        raise HTTPException(
            status_code=403, 
            detail=f"Increased number of tickets (before: {current}), users may lose their seats"
        )
    elif available is not None and available < 0:
        raise HTTPException(status_code=404, detail="Tickets available cannot be negative")
        
    # Update match and return it
    match_in = MatchUpdate(date=match_in.date, price=price, 
                           total_available_tickets=available)
    return modify_match(session, match, match_in)
