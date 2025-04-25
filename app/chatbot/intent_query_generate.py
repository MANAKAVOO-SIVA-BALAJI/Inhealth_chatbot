# # app/chatbot/intent_query_processor.py

# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from app.config import settings
# import structlog
# from datetime import datetime
# import re

# from pydantic import BaseModel

# logger = structlog.get_logger()
# class ChatbotOutput(BaseModel):
#     intent: str
#     query: str

# parser = PydanticOutputParser(pydantic_object=ChatbotOutput)

# class IntentQueryProcessor:
#     """Processes user messages to classify intent and generate corresponding GraphQL queries in one step."""
    
#     def __init__(self, llm=None):
#         """Initialize the processor with an LLM."""
#         self.llm = llm or ChatOpenAI(
#             model=settings.OPENAI_MODEL, #"gpt-4o-mini"
#             temperature=0,
#             openai_api_key=settings.OPENAI_API_KEY
#         )
        
#         # Role-based intent dictionary
#         self.intent_dict = {
#             "general_intents": [
#                 "greetings",
#                 "farewell",
#                 "thank_you",
#                 "others"
#             ],
#             "admin": {
#                 "live_data_intents": [
#                     "get_all_live_orders",
#                     "get_pending_orders_by_blood_group",
#                     "get_all_orders_by_status"
#                 ],
#                 "historical_data_intents": [
#                     "admin_order_trends_by_blood_group",
#                     "admin_orders_by_reason",
#                     "monthly_order_summary_by_company"
#                 ],
#                 "analysis_and_cost_intents": [
#                     "hospital_cost_summary",
#                     "blood_bank_cost_summary",
#                     "compare_blood_component_usage",
#                     "hospital_details",
#                     "blood_bank_details",
#                     "system_wide_cost_summary",
#                     "compare_hospital_costs",
#                     "top_performing_blood_banks",
#                     "monthly_billing_summary"
#                 ]
#             },
#             "blood_bank": {
#                 "live_data_intents": [
#                     "view_new_orders",
#                     "view_approved_orders",
#                     "view_pending_orders",
#                     "view_completed_orders",
#                     "track_order_status",
#                     "get_orders_by_patient_name"
#                 ],
#                 "historical_data_intents": [
#                     "blood_bank_past_orders",
#                     "monthly_blood_bank_order_summary",
#                     "blood_bank_order_trends"
#                 ],
#                 "analysis_and_cost_intents": [
#                     "blood_component_usage",
#                     "blood_bank_cost_summary",
#                     "blood_bank_billing_summary"
#                 ]
#             },
#             "hospital": {
#                 "live_data_intents": [
#                     "request_new_order",
#                     "get_my_recent_orders",
#                     "get_pending_orders",
#                     "get_approved_orders",
#                     "get_completed_orders",
#                     "track_order_status",
#                     "get_orders_by_blood_group",
#                     "get_orders_by_blood_component",
#                     "get_orders_by_reason",
#                     "get_orders_by_patient_name"
#                 ],
#                 "historical_data_intents": [
#                     "hospital_order_history",
#                     "order_trends_by_blood_group",
#                     "monthly_order_summary",
#                     "orders_by_reason"
#                 ],
#                 "analysis_and_cost_intents": [
#                     "hospital_cost_summary",
#                     "compare_blood_component_usage",
#                     "monthly_hospital_billing_summary"
#                 ]
#             }
#         }
        
#         INTENT_DICT = {
#             "general_intents": ["greetings", "farewell", "thank_you", "others"],
#             "admin": {
#                 "live_data_intents": ["get_all_live_orders", "get_pending_orders_by_blood_group", "get_all_orders_by_status"],
#                 "historical_data_intents": ["admin_order_trends_by_blood_group", "admin_orders_by_reason", "monthly_order_summary_by_company"],
#                 "analysis_and_cost_intents": [
#                     "hospital_cost_summary", "blood_bank_cost_summary", "compare_blood_component_usage", "hospital_details",
#                     "blood_bank_details", "system_wide_cost_summary", "compare_hospital_costs", "top_performing_blood_banks",
#                     "monthly_billing_summary"
#                 ]
#             },
#             "blood_bank": {
#                 "live_data_intents": ["view_new_orders", "view_approved_orders", "view_pending_orders", "view_completed_orders", "track_order_status", "get_orders_by_patient_name"],
#                 "historical_data_intents": ["blood_bank_past_orders", "monthly_blood_bank_order_summary", "blood_bank_order_trends"],
#                 "analysis_and_cost_intents": ["blood_component_usage", "blood_bank_cost_summary", "blood_bank_billing_summary"]
#             },
#             "hospital": {
#                 "live_data_intents": [
#                     "request_new_order", "get_my_recent_orders", "get_pending_orders", "get_approved_orders",
#                     "get_completed_orders", "track_order_status", "get_orders_by_blood_group", "get_orders_by_blood_component",
#                     "get_orders_by_reason", "get_orders_by_patient_name"
#                 ],
#                 "historical_data_intents": ["hospital_order_history", "order_trends_by_blood_group", "monthly_order_summary", "orders_by_reason"],
#                 "analysis_and_cost_intents": ["hospital_cost_summary", "compare_blood_component_usage", "monthly_hospital_billing_summary"]
#             }
#         }

#     def parse_with_find(self,response: str):
#       intent_key = '"intent":'
#       query_key = '"query":'

#       intent_start = response.find(intent_key) + len(intent_key)
#       intent_end = response.find('"', intent_start + 2)
#       intent = response[intent_start:intent_end].strip().strip('"')

#       # Find query
#       query_start = response.find(query_key) + len(query_key)
#       query_raw = response[query_start:].strip()

#       if query_raw[0] == '"':
#           query_raw = query_raw[1:]  # remove starting quote
#       if query_raw[-1] == '}':
#           query_raw = query_raw[:-1]  # remove ending brace if it’s the last char

#       # Now handle escaping (if escaped query string)
#       if query_raw[-1] == '"':
#           query_raw = query_raw[:-1]

#       query = bytes(query_raw, "utf-8").decode("unicode_escape")
#       logger.info("Query parsed with find", intent=intent)
#       return {
#           "intent": intent,
#           "query": query
#       }

#     def parse_response(self, response: str):
#             intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', response)
#             query_match = re.search(r'"query"\s*:\s*"((?:[^"\\]|\\.)*)"', response, re.DOTALL)

#             if intent_match and query_match:
#                 intent = intent_match.group(1)
#                 query = query_match.group(1).encode().decode('unicode_escape')  # decode \n etc.
#                 return {"intent": intent, "query": query}
#             else:
#                 logger.error("Failed to extract intent or query using regex")
#                 return self.parse_with_find(response)
            
#                 # return {"intent":response.split(",")[0].split(":")[1], "query": response.split(",")[1].split(":")[1]}



#     def process(self, message: str, role: str = "admin") -> dict:
#         """
#         Process the user message to classify intent and generate a corresponding GraphQL query.
        
#         Args:
#             message: The user's message
#             role: The user's role (admin, hospital, blood_bank)
            
#         Returns:
#             Dictionary containing both the classified intent and generated GraphQL query
#         """
#         if not message.strip():
#             return {"intent": "others", "query": ""}
            
#         logger.info("Processing message", role=role, message_length=len(message))

#         # Gather all relevant intents
#         intent_list = self.intent_dict.get("general_intents", [])
        
#         if role in self.intent_dict:
#             for category in ["live_data_intents", "historical_data_intents", "analysis_and_cost_intents"]:
#                 intent_list.extend(self.intent_dict[role].get(category, []))

#         # Admins also get access to hospital and blood_bank intents
#         if role == "admin":
#             for r in ["hospital", "blood_bank"]:
#                 for category in ["live_data_intents", "historical_data_intents", "analysis_and_cost_intents"]:
#                     intent_list.extend(self.intent_dict[r].get(category, []))

#         # Build intent string
#         intent_str = ", ".join(intent_list)
        
#         # Current time for context
#         current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
#         # Create combined prompt
#         combined_prompt = ChatPromptTemplate.from_messages([
#         (
#             "system",
#             (
#               """
#             You are an AI assistant that classifies user messages into predefined intents and generates GraphQL queries.

#             ### PART 1: INTENT CLASSIFICATION

#             Context:
#             - The user belongs to the role: '{role}'.
#             - There are three user roles: 'admin', 'hospital', and 'blood_bank'.
#             - Each role has access to different data and intents:
#                 - Hospitals request blood and can query their order status.
#                 - Blood banks approve and fulfill blood orders, and can analyze demand.
#                 - Admins have central access to all orders and perform system-wide analysis.

#             Intent Categories:
#             - live_data_intents: Real-time order tracking and current state queries.
#             - historical_data_intents: Past order-related information.
#             - analysis_and_cost_intents: Trends, cost summaries, comparisons, and analytics.
#             - general_intents: Generic conversations like greetings or thanks.

#             Available Data Columns:
#             - Order Data (bloodorderview): age, blood_bank_name, blood_group, companyid, creation_date_and_time,
#               delivery_date_and_time, last_name, first_name, patient_id, order_line_items, reason, request_id, status
#             - Cost Data (costandbillingview): blood_component, company_id, company_name, month_year,
#               overall_blood_unit, total_cost, total_patient

#             Below is the list of all valid intents for the current context:
#             {intent_str}

#             ### PART 2: GRAPHQL QUERY GENERATION

#             GraphQL Schema Reference:

#             - costandbillingview
#               Fields:
#                 - blood_component
#                 - company_id
#                 - company_name is a bloodbank_name
#                 - month_year is formatted as "MM-YYYY"
#                 - overall_blood_unit is formatted as "integer units"
#                 - total_cost
#                 - total_patient

#             - bloodorderview
#               Fields:
#                 - age integer
#                 - blood_bank_name string
#                 - blood_group is one of[AB- ,O-, A+ ,B+ ,AB+ ,O+, A- ,B-]
#                 - companyid string
#                 - creation_date_and_time
#                 - delivery_date_and_time
#                 - last_name 
#                 - first_name
#                 - patient_id
#                 - order_line_items
#                 - reason string
#                 - request_id
#                 - status is one of ["PA", "AA", "PP", "BSP", "BP", "BBA", "BA", "CMP", "REJ", "CAL"]

#             Status Code and Reference Name in order:
#               1. PA → Pending  
#                 - The order has been created and is waiting for approval by the blood bank.

#               2. AA → Agent Assigned  
#                 - An agent has been assigned to process the order.

#               3. PP → Pending Pickup  
#                 - The order is waiting to be picked up.

#               4. BSP / BP → Blood Sample Pickup  
#                 - The blood sample has been picked up.

#               5. BBA → Blood Bank Assigned  
#                 - A blood bank has been assigned to fulfill the request.

#               6. BA → Blood Arrival  
#                 - The blood has arrived at the hospital or destination.

#               7. CMP → Completed  
#                 - The order has been successfully completed.

#               8. REJ → Rejected  
#                 - The order was rejected by the system or blood bank.

#               9. CAL → Cancel  
#                 - The order was canceled by the hospital user.


#             Current time: {current_time}

#             ### OUTPUT INSTRUCTIONS

#             Respond with a JSON object containing exactly two fields:
#             1. 'intent': The classified intent name (must be one from the list)
#             2. 'query': A valid GraphQL query that corresponds to the intent

#             GraphQL Query Guidelines:

#             - Identify the correct table/view name based on the intent and request
#             - Use appropriate filtering with where clauses when needed
#             - Apply appropriate filtering operators** such as `_eq`, `_gt`, `_lt`, `_in`, `_like`, etc
#             - Select only relevant fields as indicated by the user's request
#             - Apply proper ordering when applicable
#             - Replace status codes with their corresponding names
#             - If no filters are needed, fetch all records with a default limit of 10
#             - Do not include explanations, backticks, or the word 'graphql' in the query

#           Output Format Example:
#           {{
#             "intent": "intent_name",
#             "query": query YourQueryName {{
#               table_name(
#                 where: {{ column_name: {{ _operator: "value" }} }}
#                 order_by: {{ column_name: asc }}
#                 limit: 10
#               ) {{
#                 field1
#                 field2
#               }}
#             }}
#           }}

#             For general intents like greetings, thank_you, or farewell, return an empty string for the query field.
#             Always return valid JSON that can be parsed by Python's json.loads().
#    """
#             )
        
#         ),
#         ("user", "{message}")
#         ])

#         try:
#             # Format and invoke prompt
#             prompt = combined_prompt.format_messages(message=message,role=role, intent_str=intent_str, current_time=current_time)
#             response = self.llm.invoke(prompt)
#             response = response.content
#             # print("response:",response)
#             # Extract the response JSON
#             import json
#             try:
#                 result = json.loads(response.strip())
#                 logger.info(f"Message processed successfully", intent=result.get("intent"))
#                 return result
#             except json.JSONDecodeError:
#                 logger.error(f"Failed to parse response as JSON: {response.content}")
#                 result = self.parse_response(response)
#                 logger.info(f"Message Parsed Successfully using regex  ", intent=result.get("intent"))
#                 return result
               
#         except Exception as e:
#             logger.error(f"Error processing message: {str(e)}", exc_info=True)
#             return {"intent": "others", "query": ""}



# # Function for backward compatibility
# def process_message(message: str, role: str = "admin") -> dict:
#     processor = IntentQueryProcessor()
#     return processor.process(message, role)


# # Example usage
# # processor = IntentQueryProcessor()
# # result = processor.process("can you give me the orders that blood bank is not assigned", role="bloodbank")
# # print(f"Intent: {result['intent']}")
# # print(f"Query: {result['query']}")


# app/chatbot/intent_query_processor.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import settings
import structlog
from datetime import datetime
import json
import re

from pydantic import BaseModel

logger = structlog.get_logger()
class ChatbotOutput(BaseModel):
    intent: str
    query: str

class IntentQueryProcessor:
    """Processes user messages to classify intent and generate corresponding GraphQL queries in one step."""
    
    def __init__(self, llm=None):
        """Initialize the processor with an LLM."""
        self.llm = llm or ChatOpenAI(
            model=settings.OPENAI_MODEL, #"gpt-4o-mini"
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Role-based intent dictionary
        # self.intent_dict = {
        #     "general_intents": [
        #         "greetings",
        #         "farewell",
        #         "thank_you",
        #         "others"
        #     ],
        #     "admin": {
        #         "live_data_intents": [
        #             "get_all_live_orders",
        #             "get_pending_orders_by_blood_group",
        #             "get_all_orders_by_status"
        #         ],
        #         "historical_data_intents": [
        #             "admin_order_trends_by_blood_group",
        #             "admin_orders_by_reason",
        #             "monthly_order_summary_by_company"
        #         ],
        #         "analysis_and_cost_intents": [
        #             "hospital_cost_summary",
        #             "blood_bank_cost_summary",
        #             "compare_blood_component_usage",
        #             "hospital_details",
        #             "blood_bank_details",
        #             "system_wide_cost_summary",
        #             "compare_hospital_costs",
        #             "top_performing_blood_banks",
        #             "monthly_billing_summary"
        #         ]
        #     },
        #     "blood_bank": {
        #         "live_data_intents": [
        #             "view_new_orders",
        #             "view_approved_orders",
        #             "view_pending_orders",
        #             "view_completed_orders",
        #             "track_order_status",
        #             "get_orders_by_patient_name"
        #         ],
        #         "historical_data_intents": [
        #             "blood_bank_past_orders",
        #             "monthly_blood_bank_order_summary",
        #             "blood_bank_order_trends"
        #         ],
        #         "analysis_and_cost_intents": [
        #             "blood_component_usage",
        #             "blood_bank_cost_summary",
        #             "blood_bank_billing_summary"
        #         ]
        #     },
        #     "hospital": {
        #         "live_data_intents": [
        #             "request_new_order",
        #             "get_my_recent_orders",
        #             "get_pending_orders",
        #             "get_approved_orders",
        #             "get_completed_orders",
        #             "track_order_status",
        #             "get_orders_by_blood_group",
        #             "get_orders_by_blood_component",
        #             "get_orders_by_reason",
        #             "get_orders_by_patient_name"
        #         ],
        #         "historical_data_intents": [
        #             "hospital_order_history",
        #             "order_trends_by_blood_group",
        #             "monthly_order_summary",
        #             "orders_by_reason"
        #         ],
        #         "analysis_and_cost_intents": [
        #             "hospital_cost_summary",
        #             "compare_blood_component_usage",
        #             "monthly_hospital_billing_summary"
        #         ]
        #     }
        # }

        self.intent_dict = {
            "general_intents": [
                "greetings",
                "farewell",
                "thank_you",
                "others"
            ],
            "admin": {
                "live_data_intents": [
                    "get_all_live_orders",
                    "get_pending_orders_by_blood_group",
                    "get_all_orders_by_status"
                ],
                "historical_data_intents": [
                    "admin_order_trends_by_blood_group",
                    "admin_orders_by_reason",
                    "monthly_order_summary_by_company"
                ],
                "analysis_and_cost_intents": [
                    "hospital_cost_summary",
                    "blood_bank_cost_summary",
                    "compare_blood_component_usage",
                    "hospital_details",
                    "blood_bank_details",
                    "system_wide_cost_summary",
                    "compare_hospital_costs",
                    "top_performing_blood_banks",
                    "monthly_billing_summary"
                ]
            },
            "hospital": {
                "live_data_intents": [
                    "request_new_order",
                    "get_my_recent_orders",
                    "get_pending_orders",
                    "get_approved_orders",
                    "get_completed_orders",
                    "track_order_status",
                    "get_orders_by_blood_group",
                    "get_orders_by_blood_component",
                    "get_orders_by_reason",
                    "get_orders_by_patient_name"
                ],
                "historical_data_intents": [
                    "hospital_order_history",
                    "order_trends_by_blood_group",
                    "monthly_order_summary",
                    "orders_by_reason"
                ],
                "analysis_and_cost_intents": [
                    "hospital_cost_summary",
                    "compare_blood_component_usage",
                    "monthly_hospital_billing_summary"
                ]
            },
            "blood_bank": {
                "live_data_intents": [
                    "view_new_orders",
                    "view_approved_orders",
                    "view_pending_orders",
                    "track_order_status",
                    "get_orders_by_patient_name"
                ],
                "historical_data_intents": [
                    "blood_bank_past_orders",
                    "monthly_blood_bank_order_summary",
                    "blood_bank_order_trends"
                ],
                "analysis_and_cost_intents": [
                    "blood_component_usage",
                    "blood_bank_cost_summary",
                    "blood_bank_billing_summary"
                ]
            }
        }

    #     self.combined_prompt = ChatPromptTemplate.from_messages([
    #     ("system", """
    #     You are an Expert GRAPH DATABASE ENGINEER and ANALYST who classifies user messages into predefined **intents** and generates **valid GraphQL queries** based on a strict schema.

    #     Follow these steps for SUCCESSFUL execution:

    #     1. Carefully READ and UNDERSTAND the natural language prompt provided by the user, identifying KEY COMPONENTS such as requested entities, attributes, and relationships.

    #     2. CONVERT these components into a structured GRAPHQL query, paying close attention to SYNTAX and SEMANTICS that reflect the user’s intent.

    #     3. Before DISPLAYING the GRAPHQL  query, VERIFY its relevance by cross-referencing it with the original user input to ENSURE ACCURACY.
         
            
    #       ---

    #     ### PART 1: CONTEXT & ROLE

    #     - User Role: '{role}'
    #     - Possible Roles:
    #         - admin: Full access to all data and all intents. 
    #         - hospital: Can view only their own blood orders and cost.
    #         - blood_bank: Can view cost and not completed orders ,  analyze orders relevant to their blood bank.

    #     ---

    #     ### PART 2: INTENT CLASSIFICATION

    #     Intent Categories:
    #     - live_data_intents: Real-time order tracking
    #     - historical_data_intents: Past order information
    #     - analysis_and_cost_intents: Trends, cost, analytics
    #     - general_intents: Greetings, thanks, casual chat

    #     Valid intents for current user:
    #     {intent_str}

    #     ---

    #     ### PART 3: GRAPHQL SCHEMA

    #     #### Table: bloodorderview
    #     - age
    #     - blood_bank_name
    #     - blood_group ("AB-", "O-", "A+", "B+", "AB+", "O+", "A-", "B-")
    #     - companyid
    #     - creation_date_and_time
    #     - delivery_date_and_time
    #     - last_name
    #     - first_name
    #     - patient_id
    #     - order_line_items
    #     - reason
    #     - request_id
    #     - status ("PA", "AA", "PP", "BSP", "BP", "BBA", "BA", "CMP", "REJ", "CAL")

    #     #### Status Code Descriptions:
    #     - PA → Pending: The order has been created and is waiting for approval by the blood bank.
    #     - AA → Agent Assigned: An agent has been assigned to process the order.
    #     - PP → Pending Pickup: The order is waiting to be picked up.
    #     - BSP / BP → Blood Sample Pickup: The blood sample has been picked up.
    #     - BBA → Blood Bank Assigned: A blood bank has been assigned to fulfill the request.
    #     - BA → Blood Arrival: The blood has arrived at the hospital or destination.
    #     - CMP → Completed: The order has been successfully completed.
    #     - REJ → Rejected: The order was rejected by the system or blood bank.
    #     - CAL → Cancel: The order was canceled by the hospital user.

    #     #### Table: costandbillingview
    #     - blood_component
    #     - company_id
    #     - company_name
    #     - month_year ("MM-YYYY")
    #     - overall_blood_unit
    #     - total_cost
    #     - total_patient

    #     ONLY these fields are allowed. DO NOT use unlisted fields or invented ones.

    #     ---

    #     ### PART 4: OPERATORS

    #     - _eq, _neq
    #     - _gt, _lt, _gte, _lte
    #     - _ilike, _nilike
    #     - _in, _nin

    #     Examples:
    #     status: {{ _eq: "PA" }}
    #     blood_group: {{ _in: ["A+", "B+"] }}
    #     creation_date_and_time: {{ _gte: "2024-01-01" }}

    #     ---

    #     ### PART 5: OUTPUT FORMAT (STRICT JSON)

    #     Respond ONLY with this format:

    #     {{
    #     "intent": "intent_name",
    #     "query": "query QueryName {{ table_name(where: {{ column: {{ _eq: \\"value\\" }} }}, limit: 10) {{ field1 field2 }} }}"
    #     }}

    #     - JSON must be valid and parseable with json.loads()
    #     - Use escaped double quotes
    #     - No text outside JSON object
    #     - No aggregations or calculations
    #     - Use fields ONLY from listed schema
    #     - General intents must return empty string for query
    #     - If a field is used in any condition (WHERE clause), it MUST be included in the selected fields.


    #     General intent example:
    #     {{ "intent": general_intent_name, "query": "" }}

    #     ---

    #     ### FINAL CHECK BEFORE RESPONDING:

    #     1. Valid JSON with escaped quotes
    #     2. Only listed fields are used
    #     3. Valid GraphQL syntax and operators
    #     4. Proper role-based data logic
    #     5. No text or comments outside JSON
    #     6. Query name is included
    #     7. Any field used in filters is also present in selection set

    #     System time: {current_time} 
    #     """),
        
    #     ("user", "{message}")
    # ])

        self.combined_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an Expert GRAPH DATABASE ENGINEER and ANALYST who classifies user messages into predefined **intents** and generates **valid GraphQL queries** based on a strict schema.

    Follow these steps for SUCCESSFUL execution:

    1. Carefully READ and UNDERSTAND the natural language prompt provided by the user, identifying KEY COMPONENTS such as requested entities, attributes, and relationships.
    
    2. CONVERT these components into a structured **GraphQL query**, paying close attention to **syntax** and **semantics** that reflect the user’s intent. The query must:
       - Be based on the schema provided.
       - Accurately reflect the user's role-based access (i.e., **admin**, **hospital**, or **blood_bank**).
       - Fetch multiple tables/columns if necessary, adhering to the schema.

    3. If the user's query is not covered by existing predefined intents, classify the intent as a **new_related_intent** based on the schema's tables and columns. Generate a relevant GraphQL query based on the user's request and ensure the query is valid.

    4. Before DISPLAYING the GraphQL query, VERIFY its relevance by cross-referencing it with the original user input to ENSURE ACCURACY.

    ---
    ### PART 1: CONTEXT & ROLE

    - User Role: '{role}'
    - Possible Roles:
        - admin: Full access to all data and all intents. 
        - hospital: Can view only their own blood orders and cost.
        - blood_bank: Can view cost and not completed orders, analyze orders relevant to their blood bank.

    ---
    ### PART 2: INTENT CLASSIFICATION

    Intent Categories:
    - **live_data_intents**: Real-time order tracking
    - **historical_data_intents**: Past order information
    - **analysis_and_cost_intents**: Trends, cost, analytics
    - **general_intents**: Greetings, thanks, casual chat
    - **new_related_intents**: For intents that are not covered by existing predefined ones but can be mapped to the schema , then create a new intent name for it.

    Valid intents for current user:
    {intent_str}

    ---
    ### PART 3: GRAPHQL SCHEMA

    #### Table: bloodorderview
    - age
    - blood_bank_name
    - blood_group ("AB-", "O-", "A+", "B+", "AB+", "O+", "A-", "B-")
    - companyid
    - creation_date_and_time
    - delivery_date_and_time
    - last_name
    - first_name
    - patient_id
    - order_line_items
    - reason
    - request_id
    - status ("PA", "AA", "PP", "BSP", "BP", "BBA", "BA", "CMP", "REJ", "CAL") mandatory field

    #### Table: costandbillingview
    - blood_component
    - company_id
    - company_name
    - month_year ("MM-YYYY")
    - overall_blood_unit
    - total_cost
    - total_patient

    ONLY these fields are allowed. DO NOT use unlisted fields or invented ones.

    ---
    ### PART 4: OPERATORS

    - _eq, _neq
    - _gt, _lt, _gte, _lte
    - _ilike, _nilike
    - _in, _nin

    Examples:
    - status: {{ _eq: "PA" }}
    - blood_group: {{ _in: ["A+", "B+"] }}
    - creation_date_and_time: {{ _gte: "2024-01-01" }}

    ---
    ### PART 5: OUTPUT FORMAT (STRICT JSON)

    Respond ONLY with this format:

    {{
    "intent": "intent_name",
    "query": "query QueryName {{ table_name(where: {{ column: {{ _eq: \\"value\\" }} }}, limit: 10) {{ field1 field2 }} }}"
    }}

    - JSON must be valid and parseable with json.loads()
    - Use escaped double quotes
    - No text outside JSON object
    - No aggregations or calculations
    - Use fields ONLY from listed schema
    - General intents must return empty string for query
    - If a field is used in any condition (WHERE clause), it MUST be included in the selected fields.

    General intent example:
    {{ "intent": "greetings", "query": "" }}

    ---
    ### FINAL CHECK BEFORE RESPONDING:

    1. Valid JSON with escaped quotes
    2. Only listed fields are used
    3. Valid GraphQL syntax and operators
    4. Proper role-based data logic (admin, hospital, blood bank)
    5. No text or comments outside JSON
    6. Query name is included
    7. Any field used in filters is also present in selection set

    System time: {current_time}
    """),

    ("user", "{message}")
])



    def parse_response(self, response_text: str) -> dict:
        """
        Parse the LLM response to extract intent and query.
        Uses multiple strategies for improved reliability.
        
        Args:
            response_text: Raw response from the LLM
            
        Returns:
            Dictionary with intent and query fields
        """
        # First try: direct JSON parsing
        try:
            # Clean the response by removing any markdown code block markers
            cleaned_response = re.sub(r'```json\s*|```\s*', '', response_text.strip())
            result = json.loads(cleaned_response)
            if 'intent' in result and 'query' in result:
                logger.info("Response parsed as valid JSON")
                return result
        except json.JSONDecodeError:
            logger.info("JSON parsing failed, trying regex approach")
        
        # Second try: regex extraction - more robust pattern
        try:
            # Match patterns that look for intent and query, even across multiple lines
            intent_pattern = r'"intent"\s*:\s*"([^"]+)"'
            query_pattern = r'"query"\s*:\s*"((?:\\"|[^"])*)"'
            
            intent_match = re.search(intent_pattern, response_text)
            query_match = re.search(query_pattern, response_text, re.DOTALL)
            
            if intent_match and query_match:
                intent = intent_match.group(1)
                query = query_match.group(1)
                # Handle escaped characters properly
                query = query.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                logger.info("Response parsed using regex", intent=intent)
                return {"intent": intent, "query": query}
        except Exception as e:
            logger.error(f"Regex parsing failed: {str(e)}")
        
        # Third try: Line-by-line extraction
        try:
            lines = response_text.split('\n')
            intent = ""
            query = ""
            
            for line in lines:
                if '"intent"' in line and not intent:
                    intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', line)
                    if intent_match:
                        intent = intent_match.group(1)
                
                if '"query"' in line:
                    # Start capturing the query
                    query_start = line.find('"query"') + len('"query"')
                    query_part = line[query_start:].strip()
                    if query_part.startswith(':'):
                        query_part = query_part[1:].strip()
                    if query_part.startswith('"'):
                        query_part = query_part[1:]
                    query += query_part
                elif query and not line.strip().startswith('"intent"'):
                    # Continue capturing multi-line query
                    query += line.strip()
            
            # Clean up the query
            if query.endswith('"}'):
                query = query[:-2]
            elif query.endswith('"'):
                query = query[:-1]
            
            # Handle escaped quotes
            query = query.replace('\\"', '"').replace('\\n', '\n')
            
            if intent:
                logger.info("Response parsed with line-by-line extraction", intent=intent)
                return {"intent": intent, "query": query}
        except Exception as e:
            logger.error(f"Line-by-line parsing failed: {str(e)}")
        
        # Final fallback: simple string search
        try:
            if '"intent"' in response_text and '"query"' in response_text:
                parts = response_text.split('"intent":', 1)[1].split('"query":', 1)
                
                intent = parts[0].strip()
                if intent.startswith('"'):
                    intent = intent[1:]
                if '"' in intent:
                    intent = intent.split('"')[0]
                
                query = parts[1].strip()
                if query.startswith('"'):
                    query = query[1:]
                if '"' in query:
                    query = query.split('"')[0]
                
                logger.info("Response parsed with simple string search", intent=intent)
                return {"intent": intent, "query": query}
        except Exception as e:
            logger.error(f"Simple string search failed: {str(e)}")
        
        # If all parsing methods fail, return default
        logger.error("All parsing methods failed, returning default")
        return {"intent": "others", "query": ""}

    # def parse_response(self, response_text: str) -> dict:
    #     """
    #     Parse the LLM response to extract intent and query.
    #     Uses multiple strategies for improved reliability.
        
    #     Args:
    #         response_text: Raw response from the LLM
            
    #     Returns:
    #         Dictionary with intent and query fields
    #     """
    #     # First try: direct JSON parsing
    #     try:
    #         # Clean the response by removing any markdown code block markers
    #         cleaned_response = re.sub(r'^```json\s*|^```\s*|\s*```$', '', response_text.strip())
    #         result = json.loads(cleaned_response)
    #         if 'intent' in result and 'query' in result:
    #             logger.info("Response parsed as valid JSON")
    #             return result
    #     except json.JSONDecodeError:
    #         logger.info("JSON parsing failed, trying regex approach")
        
    #     # Second try: regex extraction
    #     try:
    #         intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', response_text)
    #         # Use a more robust regex for query that handles escaped quotes and newlines
    #         query_match = re.search(r'"query"\s*:\s*"((?:[^"\\]|\\["\\]|\\n|\\t)*)"', response_text, re.DOTALL)
            
    #         if intent_match and query_match:
    #             intent = intent_match.group(1)
    #             # Handle escaped characters in the query
    #             query = query_match.group(1).encode().decode('unicode_escape')
    #             logger.info("Response parsed using regex", intent=intent)
    #             return {"intent": intent, "query": query}
    #     except Exception as e:
    #         logger.error(f"Regex parsing failed: {str(e)}")
        
    #     # Last resort: basic string extraction
    #     try:
    #         # Find intent
    #         intent_key = '"intent":'
    #         query_key = '"query":'

    #         intent_start = response_text.find(intent_key) + len(intent_key)
    #         intent_end = response_text.find('"', intent_start + 2)
    #         intent = response_text[intent_start:intent_end].strip().strip('"')

    #         # Find query
    #         query_start = response_text.find(query_key) + len(query_key)
    #         query_raw = response_text[query_start:].strip()

    #         # Clean up the query string
    #         if query_raw.startswith('"'):
    #             query_raw = query_raw[1:]
    #         if query_raw.endswith('}'):
    #             query_raw = query_raw[:-1]
    #         if query_raw.endswith('"'):
    #             query_raw = query_raw[:-1]

    #         query = bytes(query_raw, "utf-8").decode("unicode_escape")
    #         logger.info("Response parsed with basic string extraction", intent=intent)
    #         return {"intent": intent, "query": query}
    #     except Exception as e:
    #         logger.error(f"All parsing methods failed: {str(e)}")
    #         return {"intent": "others", "query": ""}
    
    def get_intent_list(self, role: str) -> list:
        """Get all available intents for the given role."""
        print("get_intent_list")
        intent_list = self.intent_dict.get("general_intents", [])
        
        if role in self.intent_dict:
            for category in ["live_data_intents", "historical_data_intents", "analysis_and_cost_intents"]:
                intent_list.extend(self.intent_dict[role].get(category, []))

        # Admins also get access to hospital and blood_bank intents
        if role == "admin":
            for r in ["hospital", "blood_bank"]:
                for category in ["live_data_intents", "historical_data_intents", "analysis_and_cost_intents"]:
                    intent_list.extend(self.intent_dict[r].get(category, []))
                    
        return intent_list

    # def process(self, message: str, role: str = "admin") -> dict:
    #     """
    #     Process the user message to classify intent and generate a corresponding GraphQL query.
        
    #     Args:
    #         message: The user's message
    #         role: The user's role (admin, hospital, blood_bank)
            
    #     Returns:
    #         Dictionary containing both the classified intent and generated GraphQL query
    #     """
    #     if not message.strip():
    #         return {"intent": "others", "query": ""}
            
    #     logger.info("Processing message", role=role, message_length=len(message))

    #     # Get intents applicable for this role
    #     intent_list = self.get_intent_list(role)
    #     intent_str = ", ".join(intent_list)
        
    #     # Current time for context
    #     current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
    #     # Format and invoke prompt
    #     try:
    #         prompt = self.combined_prompt.format_messages(
    #             message=message,
    #             role=role, 
    #             intent_str=intent_str, 
    #             current_time=current_time
    #         )
            
    #         # Get response from LLM
    #         response = self.llm.invoke(prompt)
    #         response_text = response.content
            
    #         logger.debug("Raw LLM response", response=response_text[:200])
            
    #         # Try direct JSON parsing first
    #         try:
    #             # Remove code block markers if present
    #             clean_response = re.sub(r'^```json\s*|^```\s*|\s*```$', '', response_text.strip())
    #             result = json.loads(clean_response)
    #             logger.info("Successfully parsed response as JSON")
    #         except json.JSONDecodeError:
    #             # If direct parsing fails, use our fallback parser
    #             logger.warning("Failed to parse as JSON, using fallback parser")
    #             result = self.parse_response(response_text)
            
    #         # Validate the result
    #         if "intent" not in result or not result["intent"]:
    #             logger.warning("Missing intent in result, defaulting to 'others'")
    #             result["intent"] = "others"
                
    #         if "query" not in result:
    #             logger.warning("Missing query in result, defaulting to empty string")
    #             result["query"] = ""
            
    #         # Validate intent against allowed intents
    #         if result["intent"] not in intent_list and result["intent"] != "others":
    #             logger.warning(f"Invalid intent: {result['intent']}, defaulting to 'others'")
    #             result["intent"] = "others"
            
    #         # Check for common GraphQL syntax errors and log warnings
    #         query = result.get("query", "")
    #         if query and "_operator:" in query:
    #             logger.warning("Query contains invalid '_operator' syntax")
    #             # Try to fix the query by replacing _operator with _eq
    #             query = query.replace("_operator:", "_eq:")
    #             result["query"] = query
                
    #         logger.info("Message processed successfully", 
    #                 intent=result["intent"], 
    #                 query_length=len(result.get("query", "")))
    #         return result
                
    #     except Exception as e:
    #         logger.error(f"Error processing message: {str(e)}", exc_info=True)
    #         return {"intent": "others", "query": ""}

    def process(self, message: str, role: str = "admin") -> dict:
        """
        Process the user message to classify intent and generate a corresponding GraphQL query.
        
        Args:
            message: The user's message
            role: The user's role (admin, hospital, blood_bank)
            
        Returns:
            Dictionary containing both the classified intent and generated GraphQL query
        """
        if not message.strip():
            return {"intent": "others", "query": ""}
            
        logger.info("Processing message", role=role, message_length=len(message))

        # Define valid fields for each table
        valid_fields = {
            "bloodorderview": [
                "age", "blood_bank_name", "blood_group", "companyid", 
                "creation_date_and_time", "delivery_date_and_time", 
                "last_name", "first_name", "patient_id", 
                "order_line_items", "reason", "request_id", "status"
            ],
            "costandbillingview": [
                "blood_component", "company_id", "company_name", 
                "month_year", "overall_blood_unit", "total_cost", "total_patient"
            ]
        }
        
        # Invalid fields that are commonly mistakenly included
        invalid_fields = ["count", "total", "sum", "avg", "min", "max"]
        
        # Get intents applicable for this role
        intent_list = self.get_intent_list(role)
        intent_str = ", ".join(intent_list)
        
        # Current time for context
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        response_text=""
        # Format and invoke prompt
        try:
            prompt = self.combined_prompt.format_messages(
                message=message,
                role=role, 
                intent_str=intent_str, 
                current_time=current_time
            )
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            response_text = response.content
            
            logger.debug("Raw LLM response", response=response_text[:200])
            
            # Try direct JSON parsing first
            try:
                # Remove code block markers if present
                clean_response = re.sub(r'^```json\s*|^```\s*|\s*```$', '', response_text.strip())
                result = json.loads(clean_response)
                logger.info("Successfully parsed response as JSON")
            except json.JSONDecodeError:
                # If direct parsing fails, use our fallback parser
                logger.warning("Failed to parse as JSON, using fallback parser")
                result = self.parse_response(response_text)
            
            # Validate the result
            if "intent" not in result or not result["intent"]:
                logger.warning("Missing intent in result, defaulting to 'others'")
                result["intent"] = "others"
                
            if "query" not in result:
                logger.warning("Missing query in result, defaulting to empty string")
                result["query"] = ""
            
            # Validate intent against allowed intents
            if result["intent"] not in intent_list and result["intent"] != "others":
                logger.warning(f"Invalid intent: {result['intent']}, defaulting to 'others'")
                result["intent"] = "others"
            
            # Validate and fix GraphQL query
            # query = result.get("query", "")
            # if query:
            #     # Check for common syntax errors
            #     if "_operator:" in query:
            #         logger.warning("Query contains invalid '_operator' syntax")
            #         query = query.replace("_operator:", "_eq:")

                
            #     # Attempt to detect which table is being queried and validate fields
            #     for table, fields in valid_fields.items():
            #         if table in query:
            #             # Extract the field selection part
            #             field_selection_match = re.search(rf'{table}\([^)]*\)\s*{{([^}}]*?)}}', query)
            #             if field_selection_match:
            #                 field_selection = field_selection_match.group(1)
            #                 # Check for any fields that aren't in the valid fields list
            #                 for field in re.findall(r'\b(\w+)\b', field_selection):
            #                     if field.strip() and field.strip() not in fields:
            #                         logger.warning(f"Query contains invalid field for {table}: {field}")
            #                         # This is a simple warning; a more sophisticated approach could replace the field
                
            #     result["query"] = query
                
            logger.info("Message processed successfully", 
                    intent=result["intent"], 
                    query_length=len(result.get("query", "")))
            print(response_text)
            return result
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            print(response_text)

            return {"intent": "others", "query": ""}

        
# Function for backward compatibility
def process_message(message: str, role: str = "admin") -> dict:
    processor = IntentQueryProcessor()
    return processor.process(message, role)


# Example usage
# if __name__ == "__main__":
#     processor = IntentQueryProcessor()
#     result = processor.process("can you give me the orders that blood bank is not assigned", role="blood_bank")
#     print(f"Intent: {result['intent']}")
#     print(f"Query: {result['query']}")