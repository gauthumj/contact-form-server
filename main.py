from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
import httpx
import uvicorn
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Gauthum's Logistics-Contact-Pipeline")

app.add_middleware(
    CORSMiddleware,
    # Allow both the production domain and local dev environment
    allow_origins=[
        "https://gauthumj.in",
        "https://www.gauthumj.in",
        "https://v0-gauthumj.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configuration
# Replace with your Discord/Telegram Webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise RuntimeError("Missing required environment variable: WEBHOOK_URL")
ALERT_WEBHOOK_URL = httpx.URL(WEBHOOK_URL)


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

@app.post("/api/contact")
async def handle_contact(request: ContactRequest):
    """
    Receives contact form data and forwards it to a private alert channel.
    Framed as a 'Logistics Transaction' for portfolio narrative.
    """
    
    # 1. Log the "Inbound Transaction"
    print(f"📦 Logistics Event: New Contact Inbound from {request.name}")

    # 2. Prepare the payload for the alert (Discord format example)
    alert_payload = {
        "embeds": [{
            "title": "🚀 New Portfolio Lead!",
            "color": 15548997,  # Burgundy/Rose color
            "fields": [
                {"name": "From", "value": f"{request.name} ({request.email})", "inline": False},
                {"name": "Message", "value": request.message, "inline": False}
            ],
            "footer": {"text": "System Health: Optimal | Source: Home Server Webhook"}
        }]
    }

    # 3. Dispatch the alert using an async HTTP client
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ALERT_WEBHOOK_URL, json=alert_payload)
            response.raise_for_status()
            
            return {
                "status": "Delivered to Home Server",
                "transaction_id": id(request),
                "message": "Data pipeline clear"
            }
        except httpx.HTTPStatusError as e:
            print(f"❌ Pipeline Blockage: {str(e)}")
            raise HTTPException(status_code=500, detail="Upstream delivery failed")

if __name__ == "__main__":
    # Run using: python server.py
    # Ensure you've installed requirements: pip install fastapi uvicorn httpx pydantic[email]
    uvicorn.run(app, host="0.0.0.0", port=4000)