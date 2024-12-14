from fastapi.testclient import TestClient
from sqlmodel import Session

from app.tests.utils.utils import create_random_team, random_lower_string, random_id
from app.crud.team import get_team
from app.core.config import settings

def test_get_teams_list(client: TestClient, db: Session) -> None:
    # Get teams list
    r = client.get(f"{settings.API_V1_STR}/teams/")
    assert r.status_code == 200
    count = r.json()["count"]

    # Create teams
    t1 = create_random_team(db)
    t2 = create_random_team(db)

    # Get teams list
    r = client.get(f"{settings.API_V1_STR}/teams/")
    assert r.status_code == 200
    assert r.json()["count"] == count + 2

    # Delete data created
    db.delete(t1)
    db.delete(t2)
    db.commit()


def test_get_team_by_name(client: TestClient, db: Session) -> None:
    # Try get unexistent team
    name = random_lower_string()
    r = client.get(f"{settings.API_V1_STR}/teams/{name}")
    assert r.status_code == 404
    assert r.json() == {"detail": f"Team {name} not found"}

    # Create team
    t = create_random_team(db)

    # Get existent team
    r = client.get(f"{settings.API_V1_STR}/teams/{t.name}")
    assert r.status_code == 200
    team = r.json()
    assert team["name"] == t.name
    assert team["country"] == t.country
    assert team["description"] == t.description

    # Delete data created
    db.delete(t)
    db.commit()


def test_delete_team(client: TestClient, normal_user_token_headers: dict[str, str],
                     superuser_token_headers: dict[str, str], db: Session) -> None:
    name = random_lower_string()

    # Try to delete team unauthorized
    r = client.delete(f"{settings.API_V1_STR}/teams/{name}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to delete team without being superuser
    r = client.delete(f"{settings.API_V1_STR}/teams/{name}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Try delete unexisting team
    r = client.delete(f"{settings.API_V1_STR}/teams/{name}", headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Team {name} not found"}

    # Create team
    t = create_random_team(db)

    # Delete existing team
    r = client.delete(f"{settings.API_V1_STR}/teams/{t.name}", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json() == {"id": t.id, "message": "Team deleted successfully"}


def test_update_team_name(client: TestClient, normal_user_token_headers: dict[str, str], 
                          superuser_token_headers: dict[str, str], db: Session) -> None:
    name = random_lower_string()

    # Try to update team unauthorized
    r = client.put(f"{settings.API_V1_STR}/teams/{name}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to update team without being superuser
    r = client.put(f"{settings.API_V1_STR}/teams/{name}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Try update unexisting team without enough data
    data = {"name": name}
    r = client.put(f"{settings.API_V1_STR}/teams/{name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Team {name} not found. Lack of information to create a new one"}

    # Update unexisting team with enough data
    data["country"] = random_lower_string()
    r = client.put(f"{settings.API_V1_STR}/teams/{name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    team = r.json()
    id = team["id"]
    assert team["name"] == name
    assert team["country"] == data["country"]
    assert team["description"] is None

    # Create team
    t = create_random_team(db)

    # Try update existing team with a name from another team
    data["name"] = t.name
    r = client.put(f"{settings.API_V1_STR}/teams/{name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 403
    assert r.json() == {"detail": f"A team named {t.name} already exists in the system"}
    
    # Update existing team (with the same team name): no errors
    data = {"name": name}
    r = client.put(f"{settings.API_V1_STR}/teams/{name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    team = r.json()
    assert team["id"] == id
    assert team["name"] == name

    # Update existing team with unused name
    data["name"] = random_lower_string()
    r = client.put(f"{settings.API_V1_STR}/teams/{name}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    team = r.json()
    assert team["id"] == id
    assert team["name"] == data["name"]

    # Delete data created
    db.delete(t)
    db.delete(get_team(db, id))
    db.commit()

def test_update_team_id(client: TestClient, normal_user_token_headers: dict[str, str], 
                        superuser_token_headers: dict[str, str], db: Session) -> None:
    id = random_id()

    # Try to update team unauthorized
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to update team without being superuser
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Try update unexisting team without enough data
    name = random_lower_string()
    data = {"name": name}
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Team with id {id} not found. Lack of information to create a new one"}

    # Update unexisting team with enough data
    data["country"] = random_lower_string()
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    team = r.json()
    assert team["id"] == id
    assert team["name"] == name
    assert team["country"] == data["country"]
    assert team["description"] is None

    # Create team
    t = create_random_team(db)

    # Try update existing team with a name from another team
    data["name"] = t.name
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 403
    assert r.json() == {"detail": f"A team named {t.name} already exists in the system"}
    
    # Update existing team (with the same team name): no errors
    data = {"name": name}
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    team = r.json()
    assert team["id"] == id
    assert team["name"] == name

    # Update existing team with unused name
    data["name"] = random_lower_string()
    r = client.put(f"{settings.API_V1_STR}/teams/?team_id={id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    team = r.json()
    assert team["id"] == id
    assert team["name"] == data["name"]

    # Delete data created
    db.delete(t)
    db.delete(get_team(db, id))
    db.commit()
