import json
import logging
import os

import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from backend.agent.sales_agent import run_sales_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mobile Store AI Telegram Assistant")

# Telegram Token from .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class ChatRequest(BaseModel):
    message: str
    customer_name: str
    customer_phone: str
    provider: Optional[str] = "local"

@app.get("/")
def read_root():
    return {"status": "online", "message": "FastAPI backend is running successfully"}

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        logger.info(
            "Chat request received for customer=%s phone=%s",
            request.customer_name,
            request.customer_phone,
        )
        response = run_sales_agent(
            user_message=request.message,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            provider=request.provider,
        )
        logger.info("Chat response generated successfully")
        return {"response": response}
    except Exception as e:
        logger.exception("Chat endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TELEGRAM WEBHOOK ====================

def send_telegram_message(chat_id: int, text: str):
    """Send a message to a Telegram chat"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram message sent to chat_id=%s", chat_id)
    except Exception as e:
        logger.exception("Error sending Telegram message to chat_id=%s", chat_id)

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram messages"""
    try:
        body = await request.json()
        logger.debug("Received Telegram payload: %s", json.dumps(body, ensure_ascii=False))

        if "message" not in body:
            logger.info("Telegram update ignored: no message field")
            return {"status": "ignored"}

        msg = body["message"]
        chat_id = msg["chat"]["id"]
        user_message = msg.get("text", "")

        customer_name = msg["from"].get("first_name", "عميل")
        if msg["from"].get("last_name"):
            customer_name += " " + msg["from"]["last_name"]

        customer_phone = str(chat_id)
        logger.info(
            "Telegram message received from chat_id=%s customer=%s text=%s",
            chat_id,
            customer_name,
            user_message,
        )

        ai_response = run_sales_agent(
            user_message=user_message,
            customer_name=customer_name,
            customer_phone=customer_phone,
            provider="local",
        )

        send_telegram_message(chat_id, ai_response)

        return {"status": "success"}

    except Exception as e:
        logger.exception("Telegram webhook error")
        return {"status": "error", "detail": str(e)}