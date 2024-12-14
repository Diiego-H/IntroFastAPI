from fastapi.testclient import TestClient
from sqlmodel import Session
from app.tests.utils.utils import *
from app.core.config import settings
from app.models import Order

def test_get_orders_user(client: TestClient, db: Session) -> None:
    # Get orders of unexistent user
    email = random_email()
    r = client.get(f"{settings.API_V1_STR}/orders/{email}")
    assert r.status_code == 400
    assert r.json() == {"detail": f"User {email} not found"}

    # Add account
    a = create_random_account(db)

    # Get no orders of existent user
    r = client.get(f"{settings.API_V1_STR}/orders/{get_account_email(db, a)}")
    assert r.status_code == 200
    assert r.json() == []

    # Add order
    o = create_random_order(db)
    email = db.get(User, o.account_id).email

    # Get an order of existent user
    r = client.get(f"{settings.API_V1_STR}/orders/{email}")
    assert r.status_code == 200
    l = r.json()
    assert type(l) is list
    assert len(l) == 1
    assert l[0]["id"] == o.id

    # Delete data created
    delete_account(db, a)
    delete_order(db, o)


def test_get_all_orders(client: TestClient, db: Session) -> None:
    # Get all orders
    r = client.get(f"{settings.API_V1_STR}/orders/")
    assert r.status_code == 200
    l = r.json()
    assert type(l) is list
    count = len(l)

    # Add 2 orders
    o1 = create_random_order(db)
    o2 = create_random_order(db)

    # Get all orders
    r = client.get(f"{settings.API_V1_STR}/orders/")
    assert r.status_code == 200
    orders = r.json()
    assert type(orders) is list
    assert len(orders) == count + 2

    # Find first order added
    order = None
    for x in orders:
        if x["id"] == o1.id:
            order = x
            break

    # Check order data
    assert order is not None
    assert order["match_id"] == o1.match_id
    assert order["tickets_bought"] == o1.tickets_bought
    assert order["account_id"] == o1.account_id

    # Delete data created
    delete_order(db, o1)
    delete_order(db, o2)


def test_create_order_user(client: TestClient, normal_user_token_headers: dict[str, str], 
                           db: Session) -> None:
    # Try to create order unauthorized
    r = client.post(f"{settings.API_V1_STR}/orders/")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to get money for an inexistent user
    headers = {"Authorization": f"Bearer {random_lower_string()}"}
    r = client.post(f"{settings.API_V1_STR}/orders/", json={}, headers=headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "Could not validate credentials"}

    # Try to create order for a user without account
    data = {"match_id": random_id(), "num_tickets": 0}
    r = client.post(f"{settings.API_V1_STR}/orders/", json=data, headers=normal_user_token_headers)
    assert r.status_code == 401
    assert r.json() == {"detail": f"User {settings.EMAIL_TEST_USER} does not have an account"}

    # Create match
    m = create_random_match(db)
    tickets = 1
    m.total_available_tickets = tickets
    db.commit()
    db.refresh(m)
    money = m.price*10

    # Create account and get its access token
    login = {
        "username": random_email(),
        "password": random_lower_string()
    }
    a = create_account(db, login["username"], login["password"], money)
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login)
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Try to create order for an inexistent match
    r = client.post(f"{settings.API_V1_STR}/orders/", json=data, headers=headers)
    assert r.status_code == 402
    assert r.json() == {"detail": f"Match {data['match_id']} not found"}

    # Try to create order with non-positive number of tickets
    data["match_id"] = m.id
    r = client.post(f"{settings.API_V1_STR}/orders/", json=data, headers=headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "At least one ticket is required for an order"}
    data["num_tickets"] = 1000

    # Try to create order with less money in the account than needed
    r = client.post(f"{settings.API_V1_STR}/orders/", json=data, headers=headers)
    assert r.status_code == 404
    assert r.json() == {"detail": "The user does not have enough money"}

    # Try to create order for more tickets than available
    data["num_tickets"] = 5
    r = client.post(f"{settings.API_V1_STR}/orders/", json=data, headers=headers)
    assert r.status_code == 405
    assert r.json() == {
        "detail": "Wanted to order more tickets than the available amount for the match"
    }

    # Create order
    data["num_tickets"] = 1
    r = client.post(f"{settings.API_V1_STR}/orders/", json=data, headers=headers)
    assert r.status_code == 200
    order = r.json()
    assert order["match_id"] == m.id
    assert order["tickets_bought"] == data["num_tickets"]
    assert order["account_id"] == a.id
    
    # Check persistence
    o = db.get(Order, order["id"])
    assert o is not None

    # Check changes in account
    db.refresh(a)
    assert a.available_money == money - m.price*tickets
    assert len(a.orders) == 1

    # Check changes in match
    db.refresh(m)
    assert m.total_available_tickets == tickets - data["num_tickets"]
    assert len(m.orders) == 1

    # Delete data created
    delete_order(db, o)


def test_purchase_order(client: TestClient, normal_user_token_headers: dict[str, str], 
                           db: Session) -> None:
    # Try to purchase order unauthorized
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}

    # Try to get money for an inexistent user
    headers = {"Authorization": f"Bearer {random_lower_string()}"}
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json={}, headers=headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "Could not validate credentials"}

    # Try to purchase order for a user without account
    data = {"matches": [{"match_id": random_id(), "num_tickets": -2}, {"match_id": random_id(), "num_tickets": 5}]}
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=normal_user_token_headers)
    assert r.status_code == 401
    assert r.json() == {"detail": f"User {settings.EMAIL_TEST_USER} does not have an account"}

    # Create matches
    m1 = create_random_match(db)
    m2 = create_random_match(db)

    # Adapt data for limit cases
    money1 = m1.price * 1
    money2 = m2.price * 4
    
    # Set available money to not be enough to buy the first ticket
    # If the ticket is expensive enough, just subtract 1, otherwise make it its half
    money = money1-1 if money1 >= 1 else money1/2

    m1.total_available_tickets = 1
    m2.total_available_tickets = 4
    db.commit()
    db.refresh(m1)
    db.refresh(m2)

    # Create account & obtain its access token
    login = {
        "username": random_email(),
        "password": random_lower_string()
    }
    a = create_account(db, login["username"], login["password"], money)
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login)
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Try to purchase order for an inexistent match
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 402
    assert r.json() == {"detail": f"Match {data['matches'][0]['match_id']} not found"}

    # Try to purchase order with negative number of tickets
    data['matches'][0]['match_id'] = m1.id
    data['matches'][1]['match_id'] = m2.id
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 403
    assert r.json() == {"detail": f"At least one ticket is required for order in match {data['matches'][0]['match_id']}"}

    # Try to purchase order for more tickets than available in the first match
    data['matches'][0]['num_tickets'] = 2
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 403
    assert r.json() == {
        "detail": f"Not enough tickets for match with id {m1.id}"
    }

    # Try to purchase order for more tickets than available in the second match
    data["matches"][0]["num_tickets"] = 1
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 403
    assert r.json() == {
        "detail": f"Not enough tickets for match with id {m2.id}"
    }
    data["matches"][1]["num_tickets"] = 4

    # Try to purchase order with less money in the account than needed to acquire the first match's tickets
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Insufficient funds (You have: {a.available_money:.2f}€, Total cost: {(1 * m1.price + 4 * m2.price):.2f}€)"}

    # Try to purchase order with less money in the account than needed to acquire the first match's tickets
    # AND the second match's tickets
    # If the combination is expensive enough, just subtract 1
    if money1 + money2 >= 1:
        a.available_money = money1 + money2 - 1
    # If the combination costs less than 1, make the available money be half of the price
    else:
        a.available_money = (money1 + money2) / 2
    db.commit()
    db.refresh(a)

    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 404
    assert r.json() == {"detail": f"Insufficient funds (You have: {a.available_money:.2f}€, Total cost: {(1 * m1.price + 4 * m2.price):.2f}€)"}

    # Purchase order
    a.available_money = money1 + money2
    db.commit()
    db.refresh(a)
    r = client.post(f"{settings.API_V1_STR}/orders/purchase/", json=data, headers=headers)
    assert r.status_code == 200
    order = r.json()
    assert order["message"] == "Purchase Successful"

    # Check changes in account
    db.refresh(a)
    assert a.available_money == 0
    assert len(a.orders) == 2

    # Check changes in matches
    db.refresh(m1)
    db.refresh(m2)
    assert m1.total_available_tickets == 0
    assert m2.total_available_tickets == 0
    assert len(m1.orders) == 1
    assert len(m2.orders) == 1

    # Delete data created
    db.delete(db.get(Order, order["orderIds"][0]))
    delete_order(db, db.get(Order, order["orderIds"][1]))
