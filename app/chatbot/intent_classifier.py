
# app/chatbot/intent_classifier.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import settings
import logging

import structlog
logger = structlog.get_logger()
# logger = logging.getLogger(__name__)
 
class IntentClassifier:
    """Classifies user messages into predefined intents based on role."""
    
    def __init__(self, llm=None):
        """Initialize the intent classifier with an LLM."""
        self.llm = llm or ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Role-based intent dictionary
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
            "blood_bank": {
                "live_data_intents": [
                    "view_new_orders",
                    "view_approved_orders",
                    "view_pending_orders",
                    "view_completed_orders",
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
            }
        }

    def classify(self, message: str, role: str = "admin") -> str:
        """Classify the user's message into a predefined intent based on role."""
        if not message.strip():
            return "others"
            
        logger.info("Classifying intent", role=role, message_length=len(message))

        # Gather all relevant intents
        intent_list = self.intent_dict.get("general_intents", [])
        
        if role in self.intent_dict:
            for category in ["live_data_intents", "historical_data_intents", "analysis_and_cost_intents"]:
                intent_list.extend(self.intent_dict[role].get(category, []))

        # Admins also get access to hospital and blood_bank intents
        if role == "admin":
            for r in ["hospital", "blood_bank"]:
                for category in ["live_data_intents", "historical_data_intents", "analysis_and_cost_intents"]:
                    intent_list.extend(self.intent_dict[r].get(category, []))

        # Build prompt string
        intent_str = ", ".join(intent_list)
        logger.debug(f"Available intents: {intent_str}")

        # Create classification prompt
        intent_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are an AI assistant that classifies user messages into predefined intents.\n\n"
                f"Context:\n"
                f"- The user belongs to the role: '{role}'.\n"
                "- There are three user roles: 'admin', 'hospital', and 'blood_bank'.\n"
                "- Each role has access to different data and intents:\n"
                "    - Hospitals request blood and can query their order status.\n"
                "    - Blood banks approve and fulfill blood orders, and can analyze demand.\n"
                "    - Admins have central access to all orders and perform system-wide analysis.\n\n"
                "Intent Categories:\n"
                "- live_data_intents: Real-time order tracking and current state queries.\n"
                "- historical_data_intents: Past order-related information.\n"
                "- analysis_and_cost_intents: Trends, cost summaries, comparisons, and analytics.\n"
                "- general_intents: Generic conversations like greetings or thanks.\n\n"
                "Available Data Columns:\n"
                "- Order Data (bloodorderview): age, blood_bank_name, blood_group, companyid, creation_date_and_time,\n"
                "  delivery_date_and_time, last_name, first_name, patient_id, order_line_items, reason, request_id, status\n"
                "- Cost Data (costandbillingview): blood_component, company_id, company_name, month_year,\n"
                "  overall_blood_unit, total_cost, total_patient\n\n"
                "Below is the list of all valid intents for the current context:\n"
                f"{intent_str}\n\n"
                "Instructions:\n"
                "- Read the user's message carefully.\n"
                "- Understand the intent based on their role and message.\n"
                "- Match it to the **most relevant intent** from the list.\n"
                "- Return only the exact **intent name**. No extra words, quotes, or explanation.\n"
                "- If unsure, return 'others'.\n"
                "- If the user message is vague (e.g., just says 'order details'), choose the most relevant general intent like 'get_all_live_orders' or 'get_all_orders_by_status' based on the user's role.\n"
                "- Only return 'other' if the message is clearly unrelated (e.g., jokes, chit-chat, unknown queries).\n"

                "Examples of common phrases and their related intents:\n"
                "- 'blood order details' → get_all_orders_by_status (admin)\n"
                "- 'recent requests' → get_my_recent_orders (hospital)\n"
                "- 'pending orders' → view_pending_orders (blood_bank)\n"
                "- 'how much blood we used this month' → hospital_cost_summary\n"

            )
        ),
        ("user", message)
        ])

        try:
            # Format and invoke prompt
            prompt = intent_prompt.format_messages(message=message)
            response = self.llm.invoke(prompt)
            intent = response.content.strip()
            logger.info(f"Intent classified as: {intent}")
            return intent
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}", exc_info=True)
            return "others"

# Backward compatibility function
def classify_intent(message: str, role: str = "admin") -> str:
    classifier = IntentClassifier()
    return classifier.classify(message, role)
