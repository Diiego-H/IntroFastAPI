""" Order related CRUD methods """
from sqlmodel import Session, select
from app.models import Order, OrderCreateDB
    
# Get orders by account_id
def get_orders_by_account_id(session: Session, id: int) -> list[Order]:
    return list(session.exec(select(Order).where(Order.account_id == id)))

# Get all orders
def get_all_orders(session: Session) -> list[Order]:
    return list(session.exec(select(Order)))

# Create order
def add_order(session: Session, order_create: OrderCreateDB) -> Order:
    order = Order.model_validate(order_create)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order