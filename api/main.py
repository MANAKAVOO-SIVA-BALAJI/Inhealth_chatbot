# main.py

from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Blood Bank Chatbot API")
app.include_router(router)


