""" Teams models """
from sqlmodel import Field, Relationship
from .base import SQLModel

class CompetitionTeamLink(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    competition_id: int | None = Field(default=None, foreign_key="competition.id", primary_key=True)
      
# NOTE: The attribute name is unique (2 different teams cannot have the same)

# Shared properties
class TeamBase(SQLModel):
    name: str
    country: str
    description: str | None = None
    
# Database model, database table inferred from class name
class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    competitions: list["Competition"] = Relationship(back_populates="teams", link_model=CompetitionTeamLink)

# Properties to return via API
class TeamOut(TeamBase):
    pass

# Teams list
class TeamsList(SQLModel):
    count: int
    data: list[Team]

# Team message, team code also required
class TeamMessage(SQLModel):
    message: str
    id: int

# Properties to receive via API on update, all are optional
class TeamUpdate(TeamBase):
    name: str | None = None
    country: str | None = None
    description: str | None = None