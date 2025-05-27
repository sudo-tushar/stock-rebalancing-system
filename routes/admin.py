from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from config import obtain_session_factory
from services.rebalance_service import rebalance_all_accounts
import time

admin_router = APIRouter(prefix="/admin", tags=["admin"])

async def get_db():
    async_session = obtain_session_factory()
    async with async_session() as session:
        yield session

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