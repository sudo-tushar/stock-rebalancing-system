from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services.models import Account, Portfolio
from services.schemas import AccountCreate

async def get_accounts_with_portfolios(db: AsyncSession, offset: int, limit: int):
    result = await db.execute(
        select(Account).offset(offset).limit(limit)
    )
    accounts = result.scalars().unique().all()
    for account in accounts:
        await db.refresh(account)
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
    await db.refresh(account)
    return account 