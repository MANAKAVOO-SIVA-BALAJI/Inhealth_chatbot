# # graphql_client.py

# from gql import Client, gql # type: ignore
# from gql.transport.requests import RequestsHTTPTransport # type: ignore
# from app.config import HASURA_GRAPHQL_URL, HASURA_ADMIN_SECRET ,HASURA_ROLE

# transport = RequestsHTTPTransport(
#     url=HASURA_GRAPHQL_URL,
#     headers={
#             "Content-Type": "application/json",
#             "x-hasura-admin-secret": HASURA_ADMIN_SECRET,
#             "x-hasura-role" : HASURA_ROLE
#         },
#     verify=True,
#     retries=3,
# )

# # Setup client
# client = Client(transport=transport, fetch_schema_from_transport=True)

# def run_graphql_query(query: str, variables: dict = None):
#     gql_query = gql(query)
#     result = client.execute(gql_query, variable_values=variables or {})
#     return result

# app/chatbot/graphql_client.py
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from app.config import settings
from app.cache import cache
import logging
import structlog
logger = structlog.get_logger()

# logger = logging.getLogger(__name__)

class GraphQLClient:
    def __init__(self, url, admin_secret, role):
        self.transport = RequestsHTTPTransport(
            url=url,
            headers={
                "Content-Type": "application/json",
                "x-hasura-admin-secret": admin_secret,
                "x-hasura-role": role
            },
            verify=True,
            retries=3,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
    
    def run_query(self, query, variables=None):
        # Try to get from cache first
        cache_key = f"{query}_{str(variables)}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info("GraphQL cache hit")
            return cached_result
        
        # Cache miss, execute query
        logger.info("GraphQL cache miss, executing query")
        try:
            gql_query = gql(query)
            result = self.client.execute(gql_query, variable_values=variables or {})
            
            # Cache the result
            cache.set(result, cache_key)
            return result
        except Exception as e:
            logger.error(f"GraphQL query error: {str(e)}", exc_info=True)
            raise

# Backward compatibility
def run_graphql_query(query: str, variables: dict = None):
    client = GraphQLClient(
        url=settings.HASURA_GRAPHQL_URL,
        admin_secret=settings.HASURA_ADMIN_SECRET,
        role=settings.HASURA_ROLE
    )
    return client.run_query(query, variables)