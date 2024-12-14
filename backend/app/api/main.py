""" Main API routes definition """
from fastapi import APIRouter

from app.api.routes import login, teams, users, utils, competitions, matches, account, orders

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])