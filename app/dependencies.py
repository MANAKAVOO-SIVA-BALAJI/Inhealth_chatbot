# app/dependencies.py
from fastapi import Depends
from app.chatbot.graphql_client import GraphQLClient
from app.chatbot.intent_classifier import IntentClassifier
from app.chatbot.query_generator import QueryGenerator
from app.chatbot.summarizer import Summarizer
from app.config import settings
from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(
        model=settings.OPENAI_MODEL, 
        temperature=0, 
        openai_api_key=settings.OPENAI_API_KEY
    )

def get_graphql_client():
    return GraphQLClient(
        url=settings.HASURA_GRAPHQL_URL,
        admin_secret=settings.HASURA_ADMIN_SECRET,
        role=settings.HASURA_ROLE
    )

def get_intent_classifier(llm=Depends(get_llm)):
    return IntentClassifier(llm=llm)

def get_query_generator(llm=Depends(get_llm)):
    return QueryGenerator(llm=llm)

def get_summarizer(llm=Depends(get_llm)):
    return Summarizer(llm=llm)