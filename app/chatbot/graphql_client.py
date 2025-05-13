
# app/chatbot/graphql_client.py
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from app.config import settings
from app.cache import cache
import structlog

logger = structlog.get_logger()


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
            retries=2,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)
    
    def run_query(self, query, variables=None):
        # Try to get from cache first
        cache_key = f"{query}_{str(variables)}"
        # cached_result = cache.get(cache_key)
        
        # if cached_result:
        #     logger.info("GraphQL cache hit")
        #     return cached_result
        
        # Cache miss, execute query
        # Check log levels for debugging purposes
        # print(f"gql logger level: {logging.getLogger('gql').getEffectiveLevel()}")
        # print(f"gql.transport.requests logger level: {logging.getLogger('gql.transport.requests').getEffectiveLevel()}")
        # print(f"requests logger level: {logging.getLogger('requests').getEffectiveLevel()}")
        # print(f"urllib3 logger level: {logging.getLogger('urllib3').getEffectiveLevel()}")

        logger.info("GraphQL executing query.....", query=query, variables=variables)
        try:
            gql_query = gql(query)
            # print("gql query: ",gql_query)
            result = self.client.execute(gql_query, variable_values=variables or {})
            
            # Cache the result
            # cache.set(cache_key, result)  # This was backwards: cache.set(result, cache_key)
            return result
        except Exception as e:
            logger.error(f"GraphQL query error: {str(e)}", exc_info=False)
            raise

def run_graphql_query(query: str, variables: dict = None):
    logger.info("Running GraphQL query")
    try:
        client = GraphQLClient(
            url=settings.HASURA_GRAPHQL_URL,
            admin_secret=settings.HASURA_ADMIN_SECRET,
            role=settings.HASURA_ROLE
        )
        result = client.run_query(query, variables)  
        return result                               
    except Exception as e:
        logger.error(f"GraphQL query error: {str(e)}", exc_info=False)
        raise

