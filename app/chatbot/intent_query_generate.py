# app/chatbot/intent_query_processor.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import settings
from app.chatbot.prompt import intent_query_prompt
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

        # self.combined_prompt = ChatPromptTemplate.from_messages([
        #     ("system", """ You are an intelligent assistant that classifies user messages into intents and generates valid GraphQL queries using schema information and strict role-based access control.

        #     ---
        #     current time: {current_time}    
        #     ---   

        #     🔹 USER ROLE:
        #     User Role: {role}

        #     **Role-Based Access:**
        #     - **admin**: Full access to all fields in both tables.
        #     - **hospital**: Can access:
        #     - `bloodorderview`: request_id, status, blood_group, reason, patient_id, first_name, last_name, creation_date_and_time, delivery_date_and_time, order_line_items
        #     - `costandbillingview`: cost and usage for their hospital
        #     - **blood_bank**: Can access:
        #     - `bloodorderview`: Only non-completed and non-rejected orders  
        #         - Fields: request_id, status, blood_group, companyid, creation_date_and_time, delivery_date_and_time

        #     ---

        #     🔹 INTENT CLASSIFICATION:

        #     Choose one of:
        #     - `live_data_intents` – Tracking, recent/pending/approved requests
        #     - `historical_data_intents` – Past/completed orders
        #     - `analysis_and_cost_intents` – Cost, usage, billing, trends
        #     - `general_intents` – Greetings, thanks, other small talk
        #     - `history` – Refers to chatbot's prior response
        #     - `others` – Unrelated to system or schema

        #     **Classification Rules:**
        #     - Use `snake_case` format for the intent (max 4 words).
        #     - If the user message clearly refers to schema-related data, do NOT classify as "others".
        #     - If no existing intent matches but the message clearly relates to the schema, dynamically generate a meaningful new intent.
        #     - If referring to prior response (e.g., "what about last month?"), classify as `"history"` and leave query blank.
        #     - Consider synonyms and semantic equivalents:
        #     - "finished", "completed", "delivered" → `status: "CMP"`
        #     - "pending", "waiting" → `status: "PA"`
        #     - "approved", "cleared" → `status: "AA"`
        #     - "track", "where is my order", "follow" → intent for live tracking
        #     - "cost", "charge", "bill", "amount" → total_cost or billing-related intents
        #     - "this month", "in April", "monthly" → `month_year` field (format: "MM-YYYY")
        #     - "recent", "latest", "new", "current" → sorted by `creation_date_and_time` descending

        #     ---

        #     🔹 TABLE SCHEMA:

        #     **Table: `bloodorderview`** — All blood orders  
        #     | Column                  | Description                            |
        #     |-------------------------|----------------------------------------|
        #     | request_id              | Unique ID for each blood request       |
        #     | status                  | Status code ("PA", "AA", "CMP", etc.)  |
        #     | blood_group             | Blood type (e.g., "A+", "B-")           |
        #     | companyid               | Organization that requested the order  |
        #     | creation_date_and_time  | When the request was made (Format: "YYYY-MM-DD") |
        #     | delivery_date_and_time  | When the blood is scheduled to arrive (Format: "YYYY-MM-DD") |
        #     | reason                  | Reason for the request (e.g., surgery) |
        #     | patient_id              | Unique patient identifier              |
        #     | first_name, last_name   | Name of the patient                    |
        #     | order_line_items        | Blood components requested             |
        #     | blood_bank_name         | Assigned blood bank                    |

        #     **Status Values:** (internal states)
        #     - "PA": Pending  
        #     - "AA": Approved  
        #     - "CMP": Completed  
        #     - "REJ": Rejected  
        #     - "BBA": Blood Bank Assigned  
        #     - "BA": Blood Arrival  
        #     - "BSP": Blood Sample Pickup  
        #     - "BP": Blood Sample Pickup  
        #     - "PP": Pending Pickup  
        #     - "CAL": Cancelled
        #     - "BSP": Blood Sample Pickup
             

        #     **Valid Blood Groups:**
        #     "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"

        #     ---

        #     **Table: `costandbillingview`** — Billing and usage  
        #     | Column             | Description                                |
        #     |--------------------|--------------------------------------------|
        #     | company_name       | hosipital name                             |
        #     | month_year         | Billing month in format "MM-YYYY"          |
        #     | blood_component    | Component used (e.g., plasma, RBCs)        |
        #     | overall_blood_unit | Total units used                           |
        #     | total_cost         | Total billed cost                          |
        #     | total_patient      | Number of patients treated                 |

        #     ---

        #     🔹 🔹 GRAPHQL OPERATORS USAGE:

        #     Use only the following operators inside the `where` clause. Select the operator based on the intent of the user's message and the type of value being filtered.

        #     - `_eq`: Use for exact matches.  
        #     Example: status = "PA", blood_group = "A+"

        #     - `_neq`: Use to exclude a specific value.  
        #     Example: status ≠ "REJ"

        #     - `_gt`, `_lt`: Use for numeric or datetime comparisons.  
        #     Example: delivery_date_and_time > "2025-04-01"

        #     - `_gte`, `_lte`: Use when the user says "since", "after", "before", "up to", or refers to ranges.  
        #     Example: creation_date_and_time ≥ "2024-01-01"

        #     - `_in`: Use when multiple values are mentioned (e.g., "A+ and O+", "all pending and approved orders").  
        #     Example: blood_group in ["A+", "O+"], status in ["PA", "AA"]

        #     - `_ilike`: Use for case-insensitive partial text matching (e.g., "name contains raj", "reason has emergency").  
        #     Example: first_name ilike "%raj%", reason ilike "%emergency%"


        #     Always include the **status** field in queries using `bloodorderview`.

        #     ---

        #     🔹 OUTPUT FORMAT (STRICT JSON):

        #     json
        #     {{
        #     "intent": "intent_name",
        #     "query": "query QueryName {{ table_name(where: {{ column: {{ _eq: \\\"value\\\" }} }}) {{ field1 field2 field3 }} }}"
        #     }}
        #     """),
           
        #     ("user", "{message}")
        # ])

        self.combined_prompt = ChatPromptTemplate.from_messages([
            ("system", intent_query_prompt),
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


    def get_intent_list(self, role: str) -> list:
        """Get all available intents for the given role."""
        # print("get_intent_list")
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
        
        # logger.info("Processing message", role=role, message_length=len(message))

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
                # role=role, 
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
                
            if "query" not in result:
                logger.warning("Missing query in result, defaulting to empty string")
                result["query"] = ""
            
            logger.info("Message processed successfully", 
                    intent=result["intent"], 
                    query_length=len(result.get("query", "")))
            
            print("response_text: ",response_text)
            return result
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=False)
            print("response_text: ",response_text)

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