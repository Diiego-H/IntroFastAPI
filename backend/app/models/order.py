"""Order model"""
from pydantic import field_validator
from sqlmodel import Field, Relationship, Column
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlmodel import SQLModel, Field
from base64 import b64encode, b64decode
from .base import SQLModel
from .match import Match
from app.core.security import encrypt, decrypt
from typing import List


# Encrypted float type for available_money in database
class EncryptedFloat(TypeDecorator):
    impl = VARCHAR

    # float => base64 encoded string (encrypted)
    def process_bind_param(self, value, dialect):
        encrypted_value = encrypt(str(value).encode())
        return b64encode(encrypted_value).decode()

    # base64 encoded string => float (decrypted)
    def process_result_value(self, value, dialect):
        decrypted_value = decrypt(b64decode(value.encode()))
        return float(decrypted_value.decode())


""" User accounts model class """
class Account(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, foreign_key="user.id")
    available_money: float = Field(sa_column=Column(EncryptedFloat))
    orders: list["Order"] = Relationship(back_populates="account")

    @field_validator('available_money')
    def non_negative_money(cls, m):
        if m < 0:
            raise ValueError('Available money must be non-negative')
        return m
    
# Properties to receive via API
class AccountCreate(SQLModel):
    email: str
    password: str
    available_money: float | None = None

# Properties to receive in DB
class AccountCreateDB(SQLModel):
    id: int
    available_money: float

class AccountMoney(SQLModel):
    money: float

""" Orders model class """
class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    match_id: int | None = Field(default=None, foreign_key="match.id")
    match: Match = Relationship(back_populates="orders")

    tickets_bought: int

    account_id: int | None = Field(default=None, foreign_key="account.id")
    account: Account = Relationship(back_populates="orders")

# Properties to receive via API
class OrderCreateAPI(SQLModel):
    match_id: int
    num_tickets: int
    # Information about account not needed, email in endpoints identifies it

# Properties to receive in DB
class OrderCreateDB(SQLModel):
    match: Match
    tickets_bought: int
    account: Account

class OrderMessage(SQLModel):
    message: str

# Properties to receive via API for an entire purchase request
class PurchaseRequest(SQLModel):
    matches: List[OrderCreateAPI]

class PurchaseMessage(SQLModel):
    message: str
    orderIds: list
