# graphql_client.py

from gql import Client, gql # type: ignore
from gql.transport.requests import RequestsHTTPTransport # type: ignore
from app.config import HASURA_GRAPHQL_URL, HASURA_ADMIN_SECRET ,HASURA_ROLE

transport = RequestsHTTPTransport(
    url=HASURA_GRAPHQL_URL,
    headers={
            "Content-Type": "application/json",
            "x-hasura-admin-secret": HASURA_ADMIN_SECRET,
            "x-hasura-role" : HASURA_ROLE
        },
    verify=True,
    retries=3,
)

# Setup client
client = Client(transport=transport, fetch_schema_from_transport=True)

def run_graphql_query(query: str, variables: dict = None):
    gql_query = gql(query)
    result = client.execute(gql_query, variable_values=variables or {})
    return result
