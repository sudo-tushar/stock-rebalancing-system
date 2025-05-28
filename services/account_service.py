from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from services.models import Account, Portfolio
from services.schemas import AccountCreate

async def get_accounts_with_portfolios(db: AsyncSession, offset: int, limit: int):
    result = await db.execute(
        select(Account).options(selectinload(Account.portfolio)).offset(offset).limit(limit)
    )
    accounts = result.scalars().unique().all()
    return accounts

async def create_account_with_portfolio(db: AsyncSession, account_data: AccountCreate):
    account = Account(wallet_balance=account_data.wallet_balance)
    db.add(account)
    await db.flush()  # Assigns account.id
    portfolios = []
    if account_data.portfolio:
        for p in account_data.portfolio:
            portfolio = Portfolio(account_id=account.id, stock_symbol=p.stock_symbol, quantity=p.quantity)
            db.add(portfolio)
            portfolios.append(portfolio)
    await db.commit()
    # Eagerly load portfolio before returning
    result = await db.execute(
        select(Account).options(selectinload(Account.portfolio)).where(Account.id == account.id)
    )
    account_with_portfolio = result.scalars().unique().one()
    return account_with_portfolio 