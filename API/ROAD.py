from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import catboost
import json

# Replace with your bot's token
BOT_TOKEN = ""
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Load your CatBoost model
MODEL_PATH = "/teamspace/studios/this_studio/ROADWATCH/API/catboost_model_98.cbm"  # Update with your actual model path
model = catboost.CatBoostClassifier()
model.load_model(MODEL_PATH)

app = FastAPI()

# Define the structure of incoming Telegram updates
class TelegramWebhook(BaseModel):
    update_id: int
    message: dict | None = None

@app.post("/webhook")
async def telegram_webhook(update: TelegramWebhook):
    """
    Handle incoming updates from Telegram.
    """
    if update.message:
        chat_id = update.message["chat"]["id"]
        text = update.message.get("text", "")
        
        # Use your CatBoost model to process the message
        prediction = process_message_with_model(text)

        # Customize the response based on the model's prediction
        response_text = f"Prediction: {prediction}. Thank you for messaging ahwalaltriq!"
        
        # Send a response back to the user
        await send_message(chat_id, response_text)
    
    return {"status": "ok"}

async def send_message(chat_id: int, text: str):
    """
    Send a message to a Telegram chat.
    """
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

def process_message_with_model(message: str) -> str:
    """
    Process the incoming message using your CatBoost model.
    """
    # Example: Prepare the message for prediction (customize as needed)
    input_data = [message]  # Replace with the appropriate feature extraction logic
    prediction = model.predict(input_data)
    return prediction[0]  # Assuming single prediction
