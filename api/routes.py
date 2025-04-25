# # routes.py

# from fastapi import APIRouter, Request
# from app.chatbot.langgraph_flow import chatbot_pipeline
# from pydantic import BaseModel
# import json
# import os

# class ChatRequest (BaseModel):
#     message: str
#     role: str
#     history: list

# router = APIRouter()

# def store_data(updates):
#     file_path = "output_data.json"
#     if os.path.exists(file_path):
#         try:
#             with open(file_path, "r") as file:
#                 data = json.load(file)

#                 if not isinstance(data, list):
#                     data = [data]
#         except json.JSONDecodeError:
#             data = []
#     else:
#         data = []
    
#     data.insert(0,updates)

#     with open(file_path, "w") as file:
#         json.dump(data, file, indent=4)


# @router.get("/")
# async def root():
#     return {"message": "Connected to Blood Bank Chatbot API!"}

# @router.post("/chat")
# async def chat_handler(request: Request):
#     body = await request.json()
#     user_message = body.get("message")
#     role = body.get("role", "admin")

#     if role not in ["hospital", "blood_bank","admin"]:
#         role = "admin"

#     result = chatbot_pipeline(user_message,role)
#     store_data(result)

#     return { "response": result}

   


# api/routes.py
from fastapi import APIRouter, Request, Depends, HTTPException 
from fastapi import status
from fastapi.responses import JSONResponse
from app.chatbot.langgraph_flow import chatbot_pipeline
from api.schemas import ChatRequest, ChatResponse
from app.config import settings
import logging
import json
import os
from datetime import datetime
from app.chatbot.utils import store_data
import structlog
# logger = logging.getLogger(__name__)
logger = structlog.get_logger()
router = APIRouter()

# def store_data(updates):
#     """Store conversation data for analysis"""
#     try:
#         file_path = "output_data.json"
#         if os.path.exists(file_path):
#             try:
#                 with open(file_path, "r") as file:
#                     data = json.load(file)
#                     if not isinstance(data, list):
#                         data = [data]
#             except json.JSONDecodeError:
#                 data = []
#         else:
#             data = []
        
#         # Add timestamp
#         updates["timestamp"] = datetime.now().isoformat()
#         data.insert(0, updates)
        
#         # Only keep the last 1000 records
#         if len(data) > 1000:
#             data = data[:1000]
        
#         with open(file_path, "w") as file:
#             json.dump(data, file, indent=4)
#     except Exception as e:
#         logger.error(f"Error storing conversation data: {str(e)}", exc_info=True)

@router.get("/")
async def root():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Connected to Blood Bank Chatbot API!!!"}) #{"message": "Connected to Blood Bank Chatbot API!"}

@router.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    logger.info(f"Processing chat request for role: {request.role}")
    
    # Process the chat request
    result = chatbot_pipeline(request.message, request.role.value)
    
    # Store the conversation data
    # store_data(result)
    
    # Format the response
    if "error" in result:
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request.",
            error=result["error"],
            error_type=result.get("error_type", "UnknownError")
        )
    
    # Extract response from the result
    if "summary" in result and isinstance(result["summary"], dict):
        return ChatResponse(
            response=result["summary"].get("response", ""),
            suggested_actions=result["summary"].get("suggested_actions", [])
        )
    else:
        return ChatResponse(
            response="I processed your request but couldn't generate a proper response.",
            error="Invalid response format",
            error_type="FormatError"
        )
    