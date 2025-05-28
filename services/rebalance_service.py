from sqlalchemy import select, func, insert, update
from services.models import Account, Portfolio
from services.priority_stock_service import get_priority_stocks_with_prices
from config import obtain_session_factory
from constants import BATCH_SIZE, NUMBER_OF_STOCKS_TO_HOLD, CONCURRENT_BATCHES
import asyncio


async def rebalance_all_accounts():
    # Fetch total number of accounts in the DB
    async_session = obtain_session_factory()
    async with async_session() as session:
        total_accounts_result = await session.execute(select(func.count(Account.id)))
        total_accounts = total_accounts_result.scalar()

        # Fetch only accounts with < NUMBER_OF_STOCKS_TO_HOLD stocks, and only id and wallet_balance
        subq = (
            select(Portfolio.account_id, func.count(Portfolio.id).label("stock_count"))
            .group_by(Portfolio.account_id)
            .subquery()
        )
        stmt = (
            select(Account.id, Account.wallet_balance)
            .outerjoin(subq, Account.id == subq.c.account_id)
            .where((subq.c.stock_count == None) | (subq.c.stock_count < NUMBER_OF_STOCKS_TO_HOLD))
        )
        result = await session.execute(stmt)
        accounts = [Account(id=row.id, wallet_balance=row.wallet_balance) for row in result.all()]
    priority_stocks = await get_priority_stocks_with_prices()

    batches = [accounts[i:i+BATCH_SIZE] for i in range(0, len(accounts), BATCH_SIZE)]
    semaphore = asyncio.Semaphore(CONCURRENT_BATCHES)

    async def limited_process_batch(batch):
        async with semaphore:
            return await process_batch(batch)

    async def process_batch(batch):
        async_session = obtain_session_factory()
        async with async_session() as session:
            updated_count = 0
            new_portfolios = []
            account_ids = [acc.id for acc in batch]
            # Only fetch account_id and stock_symbol for portfolios
            result = await session.execute(
                select(Portfolio.account_id, Portfolio.stock_symbol)
                .where(Portfolio.account_id.in_(account_ids))
            )
            all_portfolios = result.all()
            portfolios_by_account = {}
            for account_id, stock_symbol in all_portfolios:
                portfolios_by_account.setdefault(account_id, set()).add(stock_symbol)
            updated_accounts_data = []
            for account in batch:
                held_stocks = portfolios_by_account.get(account.id, set())
                num_held = len(held_stocks)
                if num_held >= NUMBER_OF_STOCKS_TO_HOLD or account.wallet_balance <= 0:
                    continue
                num_to_buy = NUMBER_OF_STOCKS_TO_HOLD - num_held
                invest_per_stock = account.wallet_balance / num_to_buy
                bought = 0
                orig_balance = account.wallet_balance
                for stock in priority_stocks:
                    symbol = stock["symbol"]
                    price = stock["price"]
                    if symbol in held_stocks:
                        continue
                    if invest_per_stock <= 0 or account.wallet_balance < price:
                        continue
                    quantity = int(invest_per_stock // price)
                    if quantity <= 0:
                        continue
                    new_portfolios.append(Portfolio(account_id=account.id, stock_symbol=symbol, quantity=quantity))
                    account.wallet_balance -= quantity * price
                    bought += 1
                    if bought >= num_to_buy:
                        break
                if bought > 0:
                    updated_count += 1
                    if account.wallet_balance != orig_balance:
                        updated_accounts_data.append({"id": account.id, "wallet_balance": account.wallet_balance})
            if new_portfolios:
                await session.execute(insert(Portfolio), [p.__dict__ for p in new_portfolios])
            if updated_accounts_data:
                for acc in updated_accounts_data:
                    await session.execute(
                        update(Account).where(Account.id == acc["id"]).values(wallet_balance=acc["wallet_balance"])
                    )
            await session.commit()
            return updated_count

    results = await asyncio.gather(*(limited_process_batch(batch) for batch in batches))
    updated_accounts = sum(results)
    return {"total_accounts": total_accounts, "updated_accounts": updated_accounts} 