import asyncio
from typing import List, Dict
from config import acquire_redis
import json

PRIORITY_STOCKS_KEY = "priority_stocks"
PRIORITY_STOCKS_TTL = 60 * 5  # 5 minutes

async def fetch_priority_stocks_from_third_party() -> List[Dict]:
    # Mocked third-party API call
    await asyncio.sleep(0.1)  # Simulate network delay
    # Example: symbol and price
    stocks = [
        {"symbol": "TCS", "price": 3500},
        {"symbol": "INFY", "price": 1500},
        {"symbol": "RELIANCE", "price": 2800},
        {"symbol": "HDFCBANK", "price": 1700},
        {"symbol": "ICICIBANK", "price": 1100},
        {"symbol": "SBIN", "price": 800},
        {"symbol": "BAJFINANCE", "price": 7000},
        {"symbol": "HINDUNILVR", "price": 2600},
        {"symbol": "ITC", "price": 450},
        {"symbol": "LT", "price": 3400},
        {"symbol": "KOTAKBANK", "price": 1700},
        {"symbol": "AXISBANK", "price": 1100},
        {"symbol": "MARUTI", "price": 12000},
        {"symbol": "ASIANPAINT", "price": 3200},
        {"symbol": "SUNPHARMA", "price": 1400},
        {"symbol": "TITAN", "price": 3500},
        {"symbol": "ULTRACEMCO", "price": 9500},
        {"symbol": "NESTLEIND", "price": 24000},
        {"symbol": "POWERGRID", "price": 300},
        {"symbol": "HCLTECH", "price": 1400},
        {"symbol": "WIPRO", "price": 500},
        {"symbol": "ADANIGREEN", "price": 1100},
        {"symbol": "ADANIPORTS", "price": 1200},
        {"symbol": "ADANIENT", "price": 3000},
        {"symbol": "DIVISLAB", "price": 4200},
    ]
    return stocks

async def get_priority_stocks_with_prices() -> List[Dict]:
    redis = await acquire_redis()
    stocks_json = await redis.get(PRIORITY_STOCKS_KEY)
    if stocks_json:
        return json.loads(stocks_json)
    stocks = await fetch_priority_stocks_from_third_party()
    if stocks:
        await redis.set(PRIORITY_STOCKS_KEY, json.dumps(stocks), ex=PRIORITY_STOCKS_TTL)
    return stocks 