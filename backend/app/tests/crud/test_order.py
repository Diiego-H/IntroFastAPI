from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
from app.crud.order import *
from app.tests.utils.utils import *

def test_get_all_orders(db: Session) -> None:
    # Get all orders
    orders = get_all_orders(db)
    assert type(orders) is list
    count = len(orders)

    # Create orders
    o1 = create_random_order(db)
    o2 = create_random_order(db)
    
    # Get all orders
    orders = get_all_orders(db)

    # Check data
    assert type(orders) is list
    assert len(orders) == count + 2
    assert type(orders[0]) is Order

    # Delete data created
    delete_order(db, o1)
    delete_order(db, o2)


def test_get_orders_account(db: Session) -> None:
    # Create account
    a = create_random_account(db)

    # No orders for this account
    assert get_orders_by_account_id(db, a.id) == []

    # Create order
    o = create_random_order(db)

    # One order for this account
    orders = get_orders_by_account_id(db, o.account_id)
    assert type(orders) is list
    assert len(orders) == 1
    assert jsonable_encoder(orders[0]) == jsonable_encoder(o)

    # Delete data created
    delete_account(db, a)
    delete_order(db, o)


def test_add_order(db: Session) -> None:
    # Create match and account
    m = create_random_match(db)
    assert len(m.orders) == 0
    a = create_random_account(db)
    assert len(a.orders) == 0

    # Create order
    order_in = OrderCreateDB(match=m, tickets_bought=m.total_available_tickets, account=a)
    o = add_order(db, order_in)

    # Check attributes
    assert type(o) is Order
    assert o.tickets_bought == order_in.tickets_bought
    assert o.match_id == m.id
    assert o.account_id == a.id

    # Check persistence in match and account
    assert len(m.orders) == 1
    assert len(a.orders) == 1

    # Delete data creted
    delete_order(db, o)
