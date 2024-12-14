""" Competition models """
from sqlmodel import Field, Relationship
from .base import SQLModel
from enum import Enum
from .team import Team, TeamOut, CompetitionTeamLink

class CategoryEnum(str, Enum):
    JUNIOR = "Junior"
    SENIOR = "Senior"

class SportEnum(str, Enum):
    FOOTBALL = "Football"
    VOLLEYBALL = "Volleyball"
    BASKETBALL = "Basketball"
    FUTSAL = "Futsal"

# NOTE: The attribute name is unique (2 different competitions cannot have the same)

# Shared properties
class CompetitionBase(SQLModel):
    name: str
    category: CategoryEnum
    sport: SportEnum
    
# Database model, database table inferred from class name
class Competition(CompetitionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    teams: list[Team] = Relationship(back_populates="competitions", link_model=CompetitionTeamLink)
    matches: list["Match"] = Relationship(back_populates="competition")

# Match properties to return (avoid cyclic dependency)
class CompetitionMatch(CompetitionBase):
    date: str
    price: float
    number_of_seats: int
    total_available_tickets: int
    competition_id: int
    local_id: int
    visitor_id: int

# Properties to return via API
class CompetitionOut(CompetitionBase):
    teams: list[TeamOut]
    matches: list[CompetitionMatch]

# Identifier returned when competition created
class CompetitionCreateOut(CompetitionOut):
    id: int

# Properties to receive via API on creation
class CompetitionCreateAPI(CompetitionBase):
    teams: list[str] = []

# Properties to receive in DB on creation
class CompetitionCreateDB(CompetitionBase):
    teams: list[Team] = []

# Competition message
class CompetitionMessage(SQLModel):
    message: str
    id: int

# Properties shared when updating, all are optional
class CompetitionUpdate(SQLModel):
    name: str | None = None
    category: CategoryEnum | None = None
    sport: SportEnum | None = None
