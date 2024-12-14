from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.tests.utils.utils import *
from app.crud.team import *
from app.models.team import *

def test_get_teams(db: Session) -> None:
    # Get number of teams in database
    count = len(get_all_teams(db))

    # Create teams
    t1 = create_random_team(db)
    t2 = create_random_team(db)

    # Get all teams in database
    teams = get_all_teams(db)

    # Check data
    assert type(teams) is list
    assert len(teams) == count + 2
    assert type(teams[0]) is Team

    # Delete data created
    db.delete(t1)
    db.delete(t2)
    db.commit()


def test_get_team(db: Session) -> None:
    # Get inexistent team (by name and id)
    assert get_team_by_name(db, random_lower_string()) is None
    assert get_team(db, random_id()) is None

    # Create team
    t = create_random_team(db)

    # Get team (by name and id)
    t1 = get_team_by_name(db, t.name)
    t2 = get_team(db, t.id)
    assert jsonable_encoder(t1) == jsonable_encoder(t)
    assert jsonable_encoder(t2) == jsonable_encoder(t)

    # Delete data created
    db.delete(t)
    db.commit()


def test_create_team(db: Session) -> None:
    # Create team with name
    name = random_lower_string()
    country = random_lower_string()
    t1 = create_team(db, TeamUpdate(name=name, country=country))

    # Check attributes
    assert t1.name == name
    assert t1.country == country
    assert t1.description is None
    assert t1.competitions == []

    # Check persistence
    assert jsonable_encoder(t1) == jsonable_encoder(get_team_by_name(db, name))

    # Create team with id
    id = random_id()
    team_in = TeamUpdate(name=random_lower_string(), country=random_lower_string(),
                         description=random_lower_string())
    t2 = create_team_id(db, id, team_in)

    # Check attributes
    assert t2.id == id
    assert t2.name == team_in.name
    assert t2.country == team_in.country
    assert t2.description == team_in.description
    assert t2.competitions == []

    # Check persistence
    assert jsonable_encoder(t2) == jsonable_encoder(get_team(db, id))

    # Delete data created
    db.delete(t1)
    db.delete(t2)
    db.commit()


def test_remove_team(db: Session) -> None:
    # Create team
    t = create_random_team(db)
    id = t.id
    
    # Remove team
    remove_team(db, t)

    # Check persistence
    assert get_team(db, id) is None


def test_update_team(db: Session) -> None:
    # Create team
    t = create_random_team(db)
    id = t.id

    # Update team's name, country and description
    team_in = TeamUpdate(name=random_lower_string(), country=random_lower_string(),
                         description=random_lower_string())

    # Update team
    new_team = modify_team(db, t, team_in)

    # Check attributes
    db.refresh(t)
    assert t.id == id
    assert t.name == team_in.name
    assert t.country == team_in.country
    assert t.description == team_in.description

    # Check return object
    assert jsonable_encoder(new_team) == jsonable_encoder(t)

    # Delete data created
    db.delete(t)
    db.commit()
    