# schema_validator.py

import requests
from app.config import HASURA_GRAPHQL_URL, HASURA_ADMIN_SECRET , HASURA_ROLE

def get_hasura_schema():
    introspection_query = {
        "query": """
        query IntrospectionQuery {
          __schema {
            types {
              name
              kind
              fields {
                name
              }
            }
          }
        }
        """
    }


    headers={
            "Content-Type": "application/json",
            "x-hasura-admin-secret": HASURA_ADMIN_SECRET,
            "x-hasura-role" : HASURA_ROLE
        }

    response = requests.post(HASURA_GRAPHQL_URL, json=introspection_query, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["__schema"]


def field_exists(schema, type_name, field_name):
    for t in schema["types"]:
        if t["name"] == type_name and t["kind"] == "OBJECT":
            if t["fields"]:
                return any(f["name"] == field_name for f in t["fields"])
    return False


def validate_query_fields(query, schema):
    for field in query["fields"]:
        if not field_exists(schema, query["type"], field["name"]):
            return False
    return True

# schema = get_hasura_schema()
# print(field_exists(schema, "bloodorderview", "reest_id"))

