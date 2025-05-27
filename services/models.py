from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    wallet_balance = Column(Float, nullable=False)
    portfolio = relationship('Portfolio', back_populates='account', cascade='all, delete-orphan')

class Portfolio(Base):
    __tablename__ = 'portfolios'
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    stock_symbol = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=0)
    account = relationship('Account', back_populates='portfolio') 