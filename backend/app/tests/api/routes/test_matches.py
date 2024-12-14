from fastapi.testclient import TestClient
from sqlmodel import Session
from app.tests.utils.utils import *
from app.core.config import settings

def test_get_matches_list(client: TestClient, db: Session) -> None:
    # Get matches list
    r = client.get(f"{settings.API_V1_STR}/matches/")
    assert r.status_code == 200
    count = len(r.json()["matches"])

    # Create match
    m = create_random_match(db)

    # Get matches list
    r = client.get(f"{settings.API_V1_STR}/matches/")
    assert r.status_code == 200
    matches = r.json()["matches"]
    assert len(matches) == count + 1

    # Find match added
    match = None
    for x in matches:
        if x["id"] == m.id:
            match = x
            break
    
    # Check some match data (the other can be checked by API docs)
    assert match is not None
    assert match["local"]["id"] == m.local_id
    assert match["visitor"]["id"] == m.visitor_id
    assert match["competition"]["name"] == m.competition.name
    assert match["price"] == m.price

    # Delete data created
    delete_match(db, m)
    

def test_get_match_by_id(client: TestClient, db: Session) -> None:
    # Try get unexistent match
    id = random_id()
    r = client.get(f"{settings.API_V1_STR}/matches/{id}")
    assert r.status_code == 404
    assert r.json() == {"detail": f"Match {id} not found"}

    # Create match
    m = create_random_match(db)

    # Get existent match
    r = client.get(f"{settings.API_V1_STR}/matches/{m.id}")
    assert r.status_code == 200
    match = r.json()
    assert match["date"] == m.date
    assert match["price"] == m.price
    assert match["number_of_seats"] == m.number_of_seats
    assert match["total_available_tickets"] == m.total_available_tickets
    assert match["competition_id"] == m.competition_id
    assert match["local_id"] == m.local_id
    assert match["visitor_id"] == m.visitor_id

    # Delete data created
    delete_match(db, m)


def test_create_match(client: TestClient, normal_user_token_headers: dict[str, str],
                      superuser_token_headers: dict[str, str], db: Session) -> None:
    # Try to create match unauthorized
    r = client.post(f"{settings.API_V1_STR}/matches/")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to create match without being superuser
    r = client.post(f"{settings.API_V1_STR}/matches/", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    id = random_id()
    data = {"price": -1, "date": random_date(), "number_of_seats": -2,
            "total_available_tickets": -1, "local_id": id, "visitor_id": id,
            "competition_id": random_id()}

    # Try to create match with negative price
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 402
    assert r.json() == {"detail": "Price cannot be negative"}

    # Try to create match with negative number of seats
    data["price"] = 10
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "The number of seats cannot be negative"}

    # Try to have negative number of tickets available
    data["number_of_seats"] = 100
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": "Tickets available cannot be negative"}

    # Try to have more tickets than seats
    data["total_available_tickets"] = 200
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 405
    assert r.json() == {"detail": "More available tickets than number of seats"}

    # Try to have same local and visitor team
    data["total_available_tickets"] = 50
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 406
    assert r.json() == {"detail": "The local and visitor teams must be different"}

    # Try to have inexistent local team
    data["local_id"] = random_id()
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 407
    assert r.json() == {"detail": "The local team does not exist"}

    # Create teams
    t1 = create_random_team(db)
    t2 = create_random_team(db)
    data["local_id"] = t1.id

    # Try to have inexistent visitor team
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 408
    assert r.json() == {"detail": "The visitor team does not exist"}

    # Try to have inexistent competition
    data["visitor_id"] = t2.id
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 409
    assert r.json() == {"detail": "The competition does not exist"}

    # Create competition
    c = create_random_competition(db)
    data["competition_id"] = c.id

    # Local team not registered in competition
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 410
    assert r.json() == {"detail": "The local team is not registered in the competition"}

    # Register local team
    c.teams.append(t1)
    db.commit()
    db.refresh(c)

    # Visitor team not registered in competition
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 411
    assert r.json() == {"detail": "The visitor team is not registered in the competition"}

    # Register visitor team
    c.teams.append(t2)
    db.commit()
    db.refresh(c)

    # Create match
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "Match created successfully"
    match1 = db.get(Match, r.json()["id"])

    # Check match attributes
    assert match1.date == data["date"]
    assert match1.price == data["price"]
    assert match1.number_of_seats == data["number_of_seats"]
    assert match1.total_available_tickets == data["total_available_tickets"]
    assert match1.competition_id == data["competition_id"]
    assert match1.local_id == data["local_id"]
    assert match1.visitor_id == data["visitor_id"]

    # Create match without specifying number of available tickets
    del data["total_available_tickets"]
    r = client.post(f"{settings.API_V1_STR}/matches/", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "Match created successfully"
    match2 = db.get(Match, r.json()["id"])

    # Check available tickets equal number of seats (default)
    assert match2.number_of_seats == data["number_of_seats"]
    assert match2.number_of_seats == match2.total_available_tickets

    # Delete data created
    db.delete(t1)
    db.delete(t2)
    db.delete(c)
    db.delete(match1)
    db.delete(match2)
    db.commit()


def test_delete_match(client: TestClient, normal_user_token_headers: dict[str, str],
                      superuser_token_headers: dict[str, str], db: Session) -> None:
    id = random_id()

    # Try to delete match unauthorized
    r = client.delete(f"{settings.API_V1_STR}/matches/{id}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to delete match without being superuser
    r = client.delete(f"{settings.API_V1_STR}/matches/{id}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Delete unexisting match
    r = client.delete(f"{settings.API_V1_STR}/matches/{id}", headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Match {id} not found"}

    # Create match
    m = create_random_match(db)

    # Delete existing match
    r = client.delete(f"{settings.API_V1_STR}/matches/{m.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json() == {"id": m.id, "message": "Match deleted successfully"}
    
    # Check teams and competition persistence
    local = db.get(Team, m.local_id)
    visitor = db.get(Team, m.visitor_id)
    competition = db.get(Competition, m.competition_id)
    assert local is not None
    assert visitor is not None
    assert competition is not None

    # Delete data created
    db.delete(local)
    db.delete(visitor)
    db.delete(competition)
    db.commit()


def test_update_match(client: TestClient, normal_user_token_headers: dict[str, str],
                      superuser_token_headers: dict[str, str], db: Session) -> None:
    id = random_id()

    # Try to update match unauthorized
    r = client.put(f"{settings.API_V1_STR}/matches/{id}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to update match without being superuser
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", headers=normal_user_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "The user doesn't have enough privileges"}

    # Try to update unexistent match
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", json={}, headers=superuser_token_headers)
    assert r.status_code == 400
    assert r.json() == {"detail": f"Match {id} not found"}

    # Create match
    m = create_random_match(db)
    id = m.id

    # Update match
    tickets = 20
    data = {"date": "02/07/2025", "price": 200, "total_available_tickets": tickets}
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    match = r.json()
    for k,v in data.items():
        assert match[k] == v

    # Check persistence
    db.refresh(m)
    assert m.id == id
    assert m.date == data["date"]
    assert m.price == data["price"]
    assert m.total_available_tickets == tickets

    # Update with no data: no errors
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", json={}, headers=superuser_token_headers)
    assert r.status_code == 200

    # Try to update negative price
    data["price"] = -1
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", json=data, headers=superuser_token_headers)
    data["price"] = 200
    assert r.status_code == 402
    assert r.json() == {"detail": "Price cannot be negative"}

    # Try to update tickets with more than before
    data["total_available_tickets"] = 1000
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 403
    assert r.json() == {
        "detail": f"Increased number of tickets (before: {tickets}), users may lose their seats"
    }

    # Try to update negative amount of tickets
    data["total_available_tickets"] = -2
    r = client.put(f"{settings.API_V1_STR}/matches/{id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 404
    assert r.json() == {"detail": "Tickets available cannot be negative"}

    # Delete data created
    db.refresh(m)
    delete_match(db, m)
