# routes.py

from fastapi import APIRouter, Request
from app.chatbot.langgraph_flow import chatbot_pipeline
from pydantic import BaseModel
import json
import os

class ChatRequest (BaseModel):
    message: str
    role: str
    history: list

router = APIRouter()

def store_data(updates):
    file_path = "output_data.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

                if not isinstance(data, list):
                    data = [data]
        except json.JSONDecodeError:
            data = []
    else:
        data = []
    
    data.insert(0,updates)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


@router.get("/")
async def root():
    return {"message": "Connected to Blood Bank Chatbot API!"}

@router.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    user_message = body.get("message")
    role = body.get("role", "admin")

    if role not in ["hospital", "blood_bank","admin"]:
        role = "admin"

    result = chatbot_pipeline(user_message,role)
    store_data(result)

    return { "response": result}

   


