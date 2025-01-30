from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import websockets
import json
import ssl

router = APIRouter()

# WebSocket URL format for Binance Ticker Stream
BINANCE_WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/{0}@ticker"

class TickerStream(BaseModel):
    symbol: str
    closePrice: str
    priceChange: str
    priceChangePercent: str
    weightedAvgPrice: str
    previousClosePrice: str
    closeQuantity: str
    bestBidPrice: str
    bestBidQuantity: str
    bestAskPrice: str
    bestAskQuantity: str
    openPrice: str
    highPrice: str
    lowPrice: str
    volume: str
    quoteVolume: str

@router.websocket("/ws/ticker/{symbol}")
async def get_ticker(websocket: WebSocket, symbol: str):
    await websocket.accept()

    try:
        await send_ticker_updates(websocket, symbol)
    except WebSocketDisconnect:
        print(f"Client disconnected: {symbol}")

async def send_ticker_updates(websocket: WebSocket, symbol: str):
    uri = BINANCE_WEBSOCKET_URL.format(symbol.lower())

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as ws_client:
        while True:
            message = await ws_client.recv()
            ticker_data = json.loads(message)

            ticker_stream = TickerStream(
                symbol=ticker_data["s"],
                closePrice=ticker_data["c"],
                priceChange=ticker_data["p"],
                priceChangePercent=ticker_data["P"],
                weightedAvgPrice=ticker_data["w"],
                previousClosePrice=ticker_data["x"],
                closeQuantity=ticker_data["Q"],
                bestBidPrice=ticker_data["b"],
                bestBidQuantity=ticker_data["B"],
                bestAskPrice=ticker_data["a"],
                bestAskQuantity=ticker_data["A"],
                openPrice=ticker_data["o"],
                highPrice=ticker_data["h"],
                lowPrice=ticker_data["l"],
                volume=ticker_data["v"],
                quoteVolume=ticker_data["q"]
            )

            # Send the full ticker data over WebSocket
            await websocket.send_json(ticker_stream.dict())
