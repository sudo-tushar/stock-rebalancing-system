from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config import obtain_session_factory
from services.schemas import AccountOut, AccountCreate
from services.account_service import get_accounts_with_portfolios, create_account_with_portfolio
from services.rebalance_service import rebalance_all_accounts
import time
from typing import List
import asyncio
from populate_dummy_data import populate

admin_router = APIRouter(prefix="/admin", tags=["admin"])

async def get_db():
    async_session = obtain_session_factory()
    async with async_session() as session:
        yield session

@admin_router.get("/accounts", response_model=List[AccountOut])
async def accounts_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    return await get_accounts_with_portfolios(db, offset, page_size)

@admin_router.post("/accounts", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account_endpoint(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_account_with_portfolio(db, account)

@admin_router.post("/populate-dummy-data", status_code=status.HTTP_202_ACCEPTED)
async def populate_dummy_data_endpoint():
    await populate()
    return {"status": "success", "message": "Dummy data populated."}

@admin_router.post("/rebalance-portfolios", status_code=status.HTTP_202_ACCEPTED)
async def rebalance_portfolios():
    start = time.perf_counter()
    result = await rebalance_all_accounts()
    end = time.perf_counter()
    execution_time = end - start
    return {
        "status": "success",
        "message": "Rebalance triggered for all accounts.",
        "total_accounts": result["total_accounts"],
        "updated_accounts": result["updated_accounts"],
        "execution_time_seconds": execution_time
    } 