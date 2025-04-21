# config.py

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET")
HASURA_GRAPHQL_URL = os.getenv("HASURA_GRAPHQL_URL")
HASURA_ROLE= os.getenv("HASURA_ROLE")

