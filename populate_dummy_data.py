import asyncio
import random
from sqlalchemy import text, insert
from services.models import Base, Account, Portfolio
from config import obtain_engine, obtain_session_factory

DEFAULT_NUM_ACCOUNTS = 10000
STOCK_SYMBOLS = [
    "TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "BAJFINANCE", "HINDUNILVR", "ITC", "LT",
    "KOTAKBANK", "AXISBANK", "MARUTI", "ASIANPAINT", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", "POWERGRID", "HCLTECH",
    "WIPRO", "ADANIGREEN", "ADANIPORTS", "ADANIENT", "DIVISLAB"
]

async def create_tables():
    engine = obtain_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def populate(num_accounts=None):
    if num_accounts is None:
        num_accounts = DEFAULT_NUM_ACCOUNTS
    async_session = obtain_session_factory()
    async with async_session() as session:
        # Clear existing data
        await session.execute(text('DELETE FROM portfolios'))
        await session.execute(text('DELETE FROM accounts'))
        await session.commit()

        accounts = []
        for i in range(num_accounts):
            # Random wallet balance between 0 and 200,000
            wallet_balance = random.randint(0, 200_000)
            accounts.append(Account(wallet_balance=wallet_balance))
        session.add_all(accounts)
        await session.flush()  # Assign IDs

        portfolios = []
        for idx, account in enumerate(accounts):
            # Randomly decide how many stocks this account holds (0 to 25)
            num_stocks = random.randint(0, 25)
            # Pick random unique stock symbols for this account
            stock_symbols = random.sample(STOCK_SYMBOLS, k=min(num_stocks, len(STOCK_SYMBOLS)))
            for symbol in stock_symbols:
                # Random quantity between 1 and 1000
                quantity = random.randint(1, 1000)
                portfolios.append(Portfolio(account_id=account.id, stock_symbol=symbol, quantity=quantity))

        if portfolios:
            await session.execute(insert(Portfolio), [p.__dict__ for p in portfolios])
        await session.commit()
        print(f"Dummy data populated for {num_accounts} accounts.")

if __name__ == "__main__":
    asyncio.run(create_tables())
    asyncio.run(populate()) 