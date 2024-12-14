from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.utils import *
from app.models import CategoryEnum, SportEnum

def test_get_competition(client: TestClient, db: Session) -> None:
    # Get unexistent competition (by name)
    name = random_lower_string()
    r = client.get(f"{settings.API_V1_STR}/competitions/{name}")
    assert r.status_code == 404
    assert r.json() == {"detail": f"Competition {name} not found"}

    # Create competition (with no teams nor matches)
    c = create_random_competition(db)

    # Get existent competition (by name)
    r = client.get(f"{settings.API_V1_STR}/competitions/{c.name}")
    assert r.status_code == 200
    competition = r.json()
    assert competition["name"] == c.name
    assert competition["category"] == c.category
    assert competition["sport"] == c.sport

    # Check empty teams & matches
    assert competition["teams"] == []
    assert competition["matches"] == []

    # Get unexistent competition (by id)
    id = random_id()
    r = client.get(f"{settings.API_V1_STR}/competitions/?competition_id={id}")
    assert r.status_code == 404
    assert r.json() == {"detail": f"Competition with id {id} not found"}

    # Get existent competition (by id)
    r = client.get(f"{settings.API_V1_STR}/competitions/?competition_id={c.id}")
    assert r.status_code == 200
    competition = r.json()
    assert competition["name"] == c.name

    # Delete data created
    db.delete(c)
    db.commit()


def test_create_competition(client: TestClient, normal_user_token_headers: dict[str, str], 
                            superuser_token_headers: dict[str, str], db: Session) -> None:
    # Try to create competition unauthorized
    r = client.post(f"{settings.API_V1_STR}/competitions/")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to create competition without being superuser
    r = client.post(f"{settings.API_V1_STR}/competitions/", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Create competition (with no teams nor matches)
    c = create_random_competition(db)

    # Try to create competition with existing name
    data = {"name": c.name, "category": c.category, "sport": c.sport, "teams": []}
    r = client.post(f"{settings.API_V1_STR}/competitions/", json=data, headers=superuser_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": f"A competition named {c.name} already exists in the system"}

    # Create competition with new name without teams
    data["name"] = random_lower_string()
    r = client.post(f"{settings.API_V1_STR}/competitions/", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    json1 = r.json()
    assert json1["name"] == data["name"]
    assert json1["teams"] == []
    assert json1["matches"] == []

    # Try to create competition with new name but unexisting team
    data["name"] = random_lower_string()
    team_name = random_lower_string()
    data["teams"].append(team_name)
    r = client.post(f"{settings.API_V1_STR}/competitions/", json=data, headers=superuser_token_headers)
    assert r.status_code == 401
    assert r.json() == {"detail": f"Team {team_name} not found"}

    # Create team (without competitions)
    t = create_random_team(db)
    assert t.competitions == []

    # Create competition with new name, existing team
    data["name"] = random_lower_string()
    data["teams"][0] = t.name
    r = client.post(f"{settings.API_V1_STR}/competitions/", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    json2 = r.json()
    assert json2["name"] == data["name"]
    assert json2["teams"][0]["name"] == t.name
    
    # Check team competitions changed
    db.refresh(t)
    assert t.competitions[0].id == json2["id"]

    # Try to create competition with unexistent category (ENUM works)
    data["name"] = random_lower_string()
    data["category"] = random_lower_string()
    r = client.post(f"{settings.API_V1_STR}/competitions/", json=data, headers=superuser_token_headers)
    assert r.status_code == 422

    # Delete data created
    db.delete(c)
    db.delete(db.get(Competition, json1["id"]))
    db.delete(t)
    db.delete(db.get(Competition, json2["id"]))
    db.commit()


def test_delete_competition(client: TestClient, normal_user_token_headers: dict[str, str], 
                            superuser_token_headers: dict[str, str], db: Session) -> None:
    name = random_lower_string()

    # Try to delete competition unauthorized
    r = client.delete(f"{settings.API_V1_STR}/competitions/{name}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to delete competition without being superuser
    r = client.delete(f"{settings.API_V1_STR}/competitions/{name}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Delete unexisting competition
    r = client.delete(f"{settings.API_V1_STR}/competitions/{name}", headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Competition {name} not found"}

    # Create competition (with no teams nor matches)
    c = create_random_competition(db)

    # Delete existing competition
    r = client.delete(f"{settings.API_V1_STR}/competitions/{c.name}", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json() == {"id": c.id, "message": "Competition deleted successfully"}

    # Create team and competition with it
    t = create_random_team(db)
    c = create_random_competition(db)
    c.teams.append(t)
    db.commit()
    db.refresh(c)

    # Check team persistence after deleting competition
    r = client.delete(f"{settings.API_V1_STR}/competitions/{c.name}", headers=superuser_token_headers)
    assert r.status_code == 200
    t = db.get(Team, t.id)
    assert t is not None
    
    # Delete data created
    db.delete(t)
    db.commit()


def test_update_competition(client: TestClient, normal_user_token_headers: dict[str, str], 
                            superuser_token_headers: dict[str, str], db: Session) -> None:
    name = random_lower_string()

    # Try to update competition unauthorized
    r = client.put(f"{settings.API_V1_STR}/competitions/{name}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to update competition without being superuser
    r = client.put(f"{settings.API_V1_STR}/competitions/{name}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Update unexistent competition
    r = client.put(f"{settings.API_V1_STR}/competitions/{name}", json={}, headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Competition {name} not found"}

    # Create competitions
    c1 = create_random_competition(db)
    c2 = create_random_competition(db)

    # Update competition with the same name
    data = {"name": c1.name}
    r = client.put(f"{settings.API_V1_STR}/competitions/{c1.name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200

    # Try to update one competition with the other's name
    data["name"] = c2.name
    r = client.put(f"{settings.API_V1_STR}/competitions/{c1.name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": f"A competition named {c2.name} already exists in the system"}

    # Update attributes
    name = random_lower_string()
    data = {"name": name, "category": "Junior", "sport": "Football"}
    r = client.put(f"{settings.API_V1_STR}/competitions/{c1.name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    competition = r.json()
    assert competition["name"] == name
    assert competition["category"] == CategoryEnum.JUNIOR
    assert competition["sport"] == SportEnum.FOOTBALL
    
    # Check persistence
    db.refresh(c1)
    assert c1.name == name

    # Try to create competition with unexistent sport (ENUM works)
    data["sport"] = random_lower_string()
    r = client.put(f"{settings.API_V1_STR}/competitions/{name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 422

    # Delete data created
    db.delete(c1)
    db.delete(c2)
    db.commit()