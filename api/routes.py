
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

@router.get("/")
async def root():
    logger.info("Connected to Blood Bank Chatbot API!!!")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Connected to Blood Bank Chatbot API!!!"}) #{"message": "Connected to Blood Bank Chatbot API!"}

@router.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    logger.info(f"Processing chat request for role: {request.role}")
    print("user message:" , request.message)
    print("role: ",request.role)

    # return {"response": "testing response"}
    
    # Process the chat request
    result = chatbot_pipeline(request.message, request.role.value)
    
    # Format the response
    if "error" in result:
        return ChatResponse(
            response="Sorry, there was an issue retrieving the data from our system. Please try again in a few minutes.",
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
    