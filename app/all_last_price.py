from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import websockets
import json
import ssl

router = APIRouter()

# WebSocket URL format for Binance Ticker Stream (multiple symbols)
BINANCE_WEBSOCKET_URL = "wss://stream.binance.com:9443/stream?streams={}"

class TickerStream(BaseModel):
    symbol: str
    closePrice: str

@router.websocket("/ws/all-lastprice")
async def get_tickers(websocket: WebSocket):
    await websocket.accept()

    try:
        await send_ticker_updates(websocket)
    except WebSocketDisconnect:
        print(f"Client disconnected")

async def send_ticker_updates(websocket: WebSocket):
    # Create a list of symbols you want to stream ticker data for (Example: ['btcusdt', 'ethusdt', 'bnbusdt'])
    symbols = [
    "btcusdt", "ethusdt", "bnbusdt", "xrpusdt", "ltcusdt", "adausdt", "solusdt", "dotusdt", "dogeusdt", "maticusdt",
    "trxusdt", "shibusdt", "avaxusdt", "linkusdt", "xlmusdt", "filusdt", "lunausdt", "etusdt", "icpusdt", "nearusdt",
    "vetusdt", "thetausdt", "eosusdt", "aaveusdt", "sandusdt", "manausdt", "zilusdt", "qtumusdt", "batusdt", "enjusdt",
    "chzusdt", "dgbusdt", "dashusdt", "nanousdt", "zrxusdt", "wavesusdt", "ksmusdt", "bttusdt", "yfiusdt", "grtusdt"
]
    
    # Construct the WebSocket URL with multiple streams
    streams = '/'.join([f"{symbol}@ticker" for symbol in symbols])
    uri = BINANCE_WEBSOCKET_URL.format(streams)

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as ws_client:
        while True:
            message = await ws_client.recv()
            ticker_data = json.loads(message)

            # Extract the symbol and close price from the data
            stream_data = ticker_data["data"]
            ticker_stream = TickerStream(symbol=stream_data["s"], closePrice=stream_data["c"])

            # Send the ticker data for each symbol to the connected client
            await websocket.send_json(ticker_stream.dict())
