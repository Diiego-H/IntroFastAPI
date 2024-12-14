""" Orders management routes """
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from app.crud.order import *
from app.crud.user import get_user_by_email
from app.crud.account import get_account
from app.crud.match import get_match_by_id
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Order,
    OrderCreateAPI,
    OrderCreateDB
)
from app.models.order import PurchaseMessage
from app.models.order import PurchaseRequest

router = APIRouter()

# NOTE: Si es volen les comandes de l'usuari s'ha de retornar una llista, no una de sola!
@router.get("/{username}", response_model=list[Order])
def read_orders_user(session: SessionDep, username: str) -> list[Order]:
    """
    Get orders of a user.
    """
    # Check user exists
    user = get_user_by_email(session=session, email=username)
    if user is None:
        raise HTTPException(status_code=400, detail=f"User {username} not found")
    
    # Find orders for this user
    return get_orders_by_account_id(session, user.id)

@router.get("/", response_model=list[Order])
def read_orders(session: SessionDep) -> list[Order]:
    """
    Get all orders.
    """
    # Find orders all orders
    return get_all_orders(session)

@router.post("/", response_model=Order)
def create_order_user(session: SessionDep, current_user: CurrentUser, order_in: OrderCreateAPI) -> Order:
    """
    Create an order for a user specified by authorization.
    """
    # Check account for this user exists
    account = get_account(session, current_user.id)
    if account is None:
        raise HTTPException(status_code=401, detail=f"User {current_user.email} does not have an account")
    
    # Check match exists
    match = get_match_by_id(session, order_in.match_id)
    if match is None:
        raise HTTPException(status_code=402, detail=f"Match {order_in.match_id} not found")
    
    # Check positive number of tickets
    num_tickets = order_in.num_tickets
    if num_tickets < 1:
        raise HTTPException(status_code=403, detail="At least one ticket is required for an order")
    
    # Required money to buy tickets
    money = num_tickets*match.price
    
    # Check user money
    available_money = account.available_money
    if available_money < money:
        raise HTTPException(status_code=404, detail="The user does not have enough money")
    
    # Check ticket availability
    available_tickets = match.total_available_tickets
    if num_tickets > available_tickets:
        raise HTTPException(
            status_code=405, 
            detail="Wanted to order more tickets than the available amount for the match"
        )
    
    # Transaction for avoiding race condition
    try:
        # Reload match and update its tickets
        match = get_match_by_id(session, order_in.match_id)
        match.total_available_tickets -= num_tickets

        # Reload account and update its money
        account = get_account(session, current_user.id)
        account.available_money -= money

        # Create and return Order (commit is made inside the add_order() function)
        return add_order(session, OrderCreateDB(match=match,tickets_bought=num_tickets,account=account))
    
    # Error due to available_tickets constraint
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=406,
            detail="Less available tickets than expected. Unable to complete the order"
        )
    
    # Error due to Account validation
    except ValidationError as e:
        session.rollback()
        raise HTTPException(
            status_code=407, 
            detail="Less available money than expected. Unable to complete the order"
        )

@router.post("/purchase/", response_model=PurchaseMessage)
def purchase_matches(session: SessionDep, current_user: CurrentUser, purchase_request: PurchaseRequest):
    """
    Purchase matches for user specified by authorization.
    """
    total_cost = 0
    orders_to_create = []

    # Check account for this user exists
    account = get_account(session, current_user.id)
    if account is None:
        raise HTTPException(status_code=401, detail=f"User {current_user.email} does not have an account")
    
    for item in purchase_request.matches:
        match = get_match_by_id(session, item.match_id)
        # Check match exists
        if match is None:
            session.rollback()
            raise HTTPException(status_code=402, detail=f"Match {item.match_id} not found")
        
        # Check positive number of tickets
        if item.num_tickets < 1:
            session.rollback()
            raise HTTPException(status_code=403, detail=f"At least one ticket is required for order in match {item.match_id}")

        # Check enough available tickets
        if item.num_tickets > match.total_available_tickets:
            session.rollback()
            raise HTTPException(status_code=403, detail=f"Not enough tickets for match with id {item.match_id}")
        
        total_cost += match.price * item.num_tickets
        match.total_available_tickets -= item.num_tickets
        orders_to_create.append(OrderCreateDB(match=match, tickets_bought=item.num_tickets, account=account))

    if total_cost > account.available_money:
        session.rollback()
        raise HTTPException(status_code=404, detail=f"Insufficient funds (You have: {account.available_money:.2f}€, Total cost: {total_cost:.2f}€)")
    
    account.available_money -= total_cost

    orders = []
    for order_create in orders_to_create:
        order = Order.model_validate(order_create)
        session.add(order)
        orders.append(order)

    session.commit()

    orderIds = []
    for order in orders:
        session.refresh(order)
        orderIds.append(order.id)
        
    return {"message": "Purchase Successful", "orderIds": orderIds}
