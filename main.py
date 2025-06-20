import os
import json
from fastapi import FastAPI, Request
import httpx
import asyncio

app = FastAPI()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")

async def send_alert_to_telegram(message, image_url=None):
    async with httpx.AsyncClient() as client:
        if image_url:
            await client.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": CHANNEL, "photo": image_url, "caption": message}
            )
        else:
            await client.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": CHANNEL, "text": message}
            )

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.body()
    payload = json.loads(data.decode("utf-8"))

    type_ = payload.get("type")
    strike = payload.get("strike")
    entry = payload.get("entry")
    expiry = payload.get("expiry")

    msg = f"🔥 توصية {type_} على SPX 🔻\nStrike: {strike}\nEntry: {entry}\nExpiry: {expiry}"
    image_url = "https://i.ibb.co/tMmjQwq/spxoption.png"

    await send_alert_to_telegram(msg, image_url=image_url)

    return {"status": "ok"}
