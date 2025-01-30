from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import websockets
import json
import ssl

router = APIRouter()

# WebSocket URL format for Binance Order Book Depth Stream
BINANCE_WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/{0}@depth"

class OrderBookStream(BaseModel):
    symbol: str
    bids: List[List[str]]
    asks: List[List[str]]

class SimplifiedOrderBook(BaseModel):
    symbol: str
    bids: List['Order']
    asks: List['Order']

class Order(BaseModel):
    price: float
    quantity: float

@router.websocket("/ws/order-book/{symbol}")
async def get_order_book(websocket: WebSocket, symbol: str):
    await websocket.accept()

    try:
        await send_order_book_updates(websocket, symbol)
    except WebSocketDisconnect:
        print(f"Client disconnected: {symbol}")

async def send_order_book_updates(websocket: WebSocket, symbol: str):
    uri = BINANCE_WEBSOCKET_URL.format(symbol.lower())

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as ws_client:
        while True:
            message = await ws_client.recv()
            order_book_data = json.loads(message)
            order_book_stream = OrderBookStream(
                symbol=order_book_data["s"],
                bids=order_book_data["b"],
                asks=order_book_data["a"]
            )

            simplified_order_book = SimplifiedOrderBook(
                symbol=order_book_stream.symbol,
                bids=map_to_orders(order_book_stream.bids),
                asks=map_to_orders(order_book_stream.asks)
            )

            await websocket.send_json(simplified_order_book.dict())

def map_to_orders(raw_data: List[List[str]]) -> List[Order]:
    orders = []
    for item in raw_data:
        if len(item) >= 2:
            try:
                price = float(item[0])
                quantity = float(item[1])
                orders.append(Order(price=price, quantity=quantity))
            except ValueError:
                continue
    return orders
