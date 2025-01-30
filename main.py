from app.order_book import router as order_book_router
from app.last_price import router as last_price_router
from app.ticker import router as ticker_router
from app.all_last_price import router as all_last_price_router

from fastapi import FastAPI

app = FastAPI()

# Include the WebSocket routes from different files
app.include_router(order_book_router)
app.include_router(last_price_router)
app.include_router(ticker_router)
app.include_router(all_last_price_router)