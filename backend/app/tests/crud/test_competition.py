from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.crud.competition import *
from app.tests.utils.utils import *
from app.models.competition import *
from app.models.team import Team

def test_get_competition(db: Session) -> None:
    # Get inexistent competition (by name and id)
    assert get_competition_by_name(db, random_lower_string()) is None
    assert get_competition(db, random_id()) is None

    # Create competition (no teams)
    c = create_random_competition(db)

    # Get competition (by name and id)
    c1 = get_competition_by_name(db, c.name)
    c2 = get_competition(db, c.id)
    assert jsonable_encoder(c1) == jsonable_encoder(c)
    assert jsonable_encoder(c2) == jsonable_encoder(c)

    # Add team to competition
    t = create_random_team(db)
    c.teams.append(t)
    db.commit()
    db.refresh(c)

    # Get competition and inspect team
    c1 = get_competition_by_name(db, c.name)
    c2 = get_competition(db, c.id)
    assert c1.teams[0].id == t.id
    assert c2.teams[0].id == t.id

    # Delete data created
    db.delete(c1)
    db.delete(c2)
    db.delete(t)
    db.commit()

def test_add_competition(db: Session) -> None:
    # Create competition (no teams)
    name = random_lower_string()
    category = CategoryEnum.JUNIOR
    sport = SportEnum.BASKETBALL
    c1 = add_competition(db, CompetitionCreateDB(name=name, category=category, sport=sport))
 
    # Check attributes
    assert c1
    assert c1.name == name
    assert c1.category == category
    assert c1.sport == sport

    # Check persistence
    assert get_competition_by_name(db, name) is not None

    # Create competition (1 team)
    t = create_random_team(db)
    name = random_lower_string()
    c2 = add_competition(db, CompetitionCreateDB(name=name, category=category, sport=sport, teams=[t]))
    
    # Check teams attribute
    assert c2
    assert len(c2.teams) == 1
    assert c2.teams[0].id == t.id

    # Competition also registered in team
    db.refresh(t)
    t.competitions[0].name == name

    # Delete data created
    db.delete(t)
    db.delete(c1)
    db.delete(c2)
    db.commit()

def test_remove_competition(db: Session) -> None:
    # Create competition with one team
    t = create_random_team(db)
    c = create_random_competition(db)
    c.teams.append(t)
    db.commit()
    db.refresh(c)
    t_id = t.id
    c_id = c.id

    # Remove competition
    remove_competition(db, c)

    # Check competition removed
    assert get_competition(db, c_id) is None

    # Check persistence of team
    db.refresh(t)
    assert db.get(Team, t_id) is not None

    # Delete data created
    db.delete(t)
    db.commit()

def test_update_competition(db: Session) -> None:
    # Create competition (no teams)
    c = create_random_competition(db)

    # Update competition sport
    update = CompetitionUpdate(sport="Football")
    new_competition = modify_competition(db, c, update)

    # Check attributes
    assert new_competition
    assert new_competition.name == c.name
    assert new_competition.category == c.category
    assert new_competition.sport == SportEnum.FOOTBALL

    # Check persistence
    db.refresh(c)
    assert jsonable_encoder(new_competition) == jsonable_encoder(get_competition(db, c.id))

    # Delete data created
    db.delete(c)
    db.commit()
    