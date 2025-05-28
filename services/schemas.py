from pydantic import BaseModel, Field
from typing import List, Optional

class PortfolioOut(BaseModel):
    id: int
    stock_symbol: str
    quantity: float
    class Config:
        orm_mode = True

class PortfolioCreate(BaseModel):
    stock_symbol: str
    quantity: float

class AccountOut(BaseModel):
    id: int
    wallet_balance: float
    portfolio: List[PortfolioOut]
    class Config:
        orm_mode = True

class AccountCreate(BaseModel):
    wallet_balance: float = 0
    portfolio: Optional[List[PortfolioCreate]] = None 