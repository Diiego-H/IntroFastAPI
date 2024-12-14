""" Match models """
from sqlmodel import Field, Relationship, CheckConstraint
from .base import SQLModel
from .team import Team
from .competition import Competition

# Shared properties
class MatchBase(SQLModel):
    date: str
    price: float
    number_of_seats: int

class MatchDerived(MatchBase):
    total_available_tickets: int
    
# Database model, database table inferred from class name
class Match(MatchDerived, table=True):
    id: int | None = Field(default=None, primary_key=True)
    competition_id: int | None = Field(default=None, foreign_key="competition.id")
    competition: Competition = Relationship(back_populates="matches")

    local_id: int | None = Field(default=None, foreign_key="team.id")
    local_team: Team = Relationship(sa_relationship_kwargs={"foreign_keys": "Match.local_id"})
    
    visitor_id: int | None = Field(default=None, foreign_key="team.id")
    visitor_team: Team = Relationship(sa_relationship_kwargs={"foreign_keys": "Match.visitor_id"})

    orders: list["Order"] = Relationship(back_populates="match")

    # Non-negative available_tickets (for concurrency)
    __table_args__ = (
        CheckConstraint('total_available_tickets >= 0', name='check_tickets_gte_0'),
    )

class MatchOut(MatchDerived):
    competition_id: int
    local_id: int
    visitor_id: int

# Properties to receive via API on creation
class MatchCreate(MatchBase):
    total_available_tickets: int | None = None
    competition_id: int
    local_id: int
    visitor_id: int

# Properties to receive in DB on creation
class MatchCreateDB(MatchDerived):
    competition: Competition
    local_team: Team
    visitor_team: Team

# Match message
class MatchMessage(SQLModel):
    message: str
    id: int

# Properties to receive via API on update, all are optional
class MatchUpdate(SQLModel):
    date: str | None = None
    price: float | None = None
    total_available_tickets: int | None = None

# Properties to return for frontend
class MatchTeamJSON(SQLModel):
    id: int
    name: str
    country: str
class MatchCompetitionJSON(SQLModel):
    name: str
    category: str
    sport: str
class MatchJSON(SQLModel):
    id: int
    local: MatchTeamJSON
    visitor: MatchTeamJSON
    competition: MatchCompetitionJSON
    date: str
    price: float
    tickets: int
class MatchesList(SQLModel):
    matches: list[MatchJSON]