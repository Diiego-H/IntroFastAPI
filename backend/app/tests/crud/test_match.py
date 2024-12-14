from fastapi.encoders import jsonable_encoder
from pytest import raises
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from app.tests.utils.utils import *
from app.crud.match import *
from app.models.match import *

def test_get_matches(db: Session) -> None:
    # Get number of matches in database
    count = len(get_all_matches(db))

    # Create match
    m = create_random_match(db)

    # Get matches in database
    matches = get_all_matches(db)

    # Check data
    assert type(matches) is list
    assert len(matches) == count + 1
    assert type(matches[0]) is Match

    # Delete data created
    delete_match(db, m)


def test_get_match(db: Session) -> None:
    # Get inexistent match
    assert get_match_by_id(db, random_id()) is None

    # Create match
    m = create_random_match(db)

    # Get match
    match = get_match_by_id(db, m.id)
    assert match.competition_id is not None
    assert match.local_id is not None
    assert match.visitor_id is not None
    assert jsonable_encoder(m) == jsonable_encoder(match)
    
    # Delete data created
    delete_match(db, m)


def test_add_match(db: Session) -> None:
    # Add teams and competition
    t1 = create_random_team(db)
    t2 = create_random_team(db)
    c = create_random_competition(db)
    c.teams = [t1, t2]
    db.commit()
    db.refresh(c)

    # Try to create match with negative available tickets
    match_in = MatchCreateDB(date="10/06/2024", price=23.43, number_of_seats=100,
                             total_available_tickets=-30, competition=c,
                             local_team=t1, visitor_team=t2)
    with raises(IntegrityError):
        add_match(db, match_in)
    db.rollback()

    # Create match
    match_in.total_available_tickets = 50
    match = add_match(db, match_in)
    
    # Check attributes
    assert match.date == match_in.date
    assert match.price == match_in.price
    assert match.number_of_seats == match_in.number_of_seats
    assert match.total_available_tickets == match_in.total_available_tickets
    assert match.competition_id == c.id
    assert match.local_id == t1.id
    assert match.visitor_id == t2.id

    # Delete data created
    delete_match(db, match)


def test_remove_match(db: Session) -> None:
    # Create match
    m = create_random_match(db)
    c_id = m.competition_id
    local_id = m.local_id
    visitor_id = m.visitor_id

    # Remove match
    remove_match(db, m)

    # Check match removed
    assert db.get(Match, m.id) is None

    # Delete match does not remove competition (nor teams)
    assert db.get(Competition, m.competition_id) is not None

    # Delete data created
    db.delete(db.get(Competition, c_id))
    db.delete(db.get(Team, local_id))
    db.delete(db.get(Team, visitor_id))
    db.commit()


def test_update_match(db: Session) -> None:
    # Create match
    m = create_random_match(db)
    id = m.id

    # Update match date, price
    match_in = MatchUpdate(date="12/12/24", price=0)
    new_match = modify_match(db, m, match_in)

    # Check attributes
    db.refresh(m)
    assert m.id == id
    assert m.date == match_in.date
    assert m.price == match_in.price

    # Check return object
    assert jsonable_encoder(m) == jsonable_encoder(new_match)

    # Delete data created
    delete_match(db, m)
