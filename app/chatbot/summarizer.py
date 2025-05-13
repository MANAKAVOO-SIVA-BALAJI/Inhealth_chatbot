# app/chatbot/summarizer.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
# from langchain.memory import ConversationBufferMemory
from app.chatbot.prompt import general_prompt , summary_prompt

from app.config import OPENAI_API_KEY
from datetime import datetime
import json
current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
from langchain.memory import ConversationBufferWindowMemory


memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True
)

# memory = ConversationBufferMemory(return_messages=True,k=5)

def response_parser(response: str) -> dict:
    """{{
        "response": "Your response here",
        "suggested_actions": ["Action 1", "Action 2"]
        }}
"""
    
    try:
        json_response = json.loads(response.strip())
        return {
            "response": json_response["response"],
            "suggested_actions": json_response.get("suggested_actions", [])
        }
    except json.JSONDecodeError:
        return {
            "response": "Sorry, I couldn't parse the response.",
            "suggested_actions": []
        }

def summarize_result(intent: str, role: str="admin",message:str=None,result: dict = None) -> str:
   
    memory.chat_memory.add_user_message(message=message)
    history = str(memory.load_memory_variables({})["chat_history"])

    # system_prompt = """
    #     As an AI assistant, your task is to answer user queries in a concise and accurate manner, using the data provided. Your responses should be informative, direct, and easy to understand, while keeping the conversation engaging.

    #     Guidelines:
    #     1. **Be concise**: Keep the response short and to the point, ensuring you only answer the user’s specific query.
    #     2. **Accuracy**: Provide the most accurate and truthful information based on the available data.
    #     3. **Avoid repetition**: Do not repeat the same answer or get stuck in loops. Each response should be unique and tailored to the specific question.
    #     4. **Engaging tone**: Keep the conversation friendly and informative without becoming overly detailed or going off-topic.
    #     5. **Provide relevant context**: Always ensure that your response is based on the relevant data provided.
    #     6. **Conversation History**:Also consider the  previous responses with a user question to answer the current user message.

    #     If the user asks a question, use the data to answer concisely. If the question is not directly answerable with the data,Try to give atleast relevant answer to the question , if the data and questions is totally irrelevant politely inform the user that their question cant answered right now.
    #     if the data don't have full answer to the question try to give partial answer if possible.
    #     ---
    #     Status Code and Reference Name in order:
    #           1. PA → Pending  
    #             - The order has been created and is waiting for approval by the blood bank.

    #           2. AA → Agent Assigned  
    #             - An agent has been assigned to process the order.

    #           3. PP → Pending Pickup  
    #             - The order is waiting to be picked up.

    #           4. BSP / BP → Blood Sample Pickup  
    #             - The blood sample has been picked up.

    #           5. BBA → Blood Bank Assigned  
    #             - A blood bank has been assigned to fulfill the request.

    #           6. BA → Blood Arrival  
    #             - The blood has arrived at the hospital or destination.

    #           7. CMP → Completed  
    #             - The order has been successfully completed.

    #           8. REJ → Rejected  
    #             - The order was rejected by the system or blood bank.

    #           9. CAL → Cancel  
    #             - The order was canceled by the hospital user.
        

    #     ### Context
    #     Relevant Data: {result}  
    #     Current Date and Time: {current_time}

    #     ### Examples of Output:

    #     1. User: "What was the status of the orders in March 2025?"
    #     LM: "In March 2025, there were 20 orders: 10 completed , 5 pending , and 5 rejected ."

    #     Suggested Actions:
    #     "View orders by blood group"
    #     "Check pending orders"

    #     2. User: "How many orders were placed by XYZ Blood Bank in April?"
    #     LM: "XYZ Blood Bank placed 12 orders in April, with 8 completed  and 4 pending."

    #     Suggested Actions:
    #     "Filter orders by blood group"
    #     "Find orders from another blood bank"

    #     3. User: "Can you show me the total cost of blood orders for April 2025?"
    #     LM: "The total cost of blood orders for April 2025 was $6,500."

    #     Suggested Actions:
    #     "View cost breakdown by blood component"
    #     "Check cost for another month"

    #     4. User: "What was the delivery status of orders in the last 7 days?"
    #     LM: "In the last 7 days, 5 orders were delivered, 2 are pending , and 1 was rejected ."

    #     Suggested Actions:
    #     "Track delivery time for pending orders"
    #     "View orders by blood group"

    #     5. User: "Can you list the most-used blood component last month?"
    #     LM: "The most-used blood component last month was O-positive blood, used in 15 orders."

    #     Suggested Actions:
    #     "Compare usage of different blood components"
    #     "Check cost by blood component"


    #     ---

    #     ### example Actions (If applicable):
    #     For **blood orders**:

    #         View order status: Use the request_id to get the status of a specific order.
    #         Filter orders by blood group or blood bank name: Filter by blood_group or blood_bank_name based on your query results.
    #         View pending , completed , rejected  orders: View orders filtered by status (e.g., PA for pending, CMP for completed, REJ for rejected).
    #         Find orders in a date range: Filter orders by creation_date_and_time or delivery_date_and_time within a specific range.
    #         View agent-assigned orders : View orders of blood bank assigned.
    #         Count orders by blood bank: Use blood_bank_name to count how many orders belong to each blood bank.
    #         Find canceled orders : Filter orders by status set to canceled.

    #     For **cost and billing**:

    #         View total cost and blood usage by company: Query company_name and overall_blood_unit from the costandbillingview table to view total cost and blood usage.
    #         Check cost by month: Filter by month_year to view costs for a specific month.
    #         List billing for companies by name and cost: Use company_name and total_cost to list billing details for companies.
    #         Find cost by blood component: Query blood_component and the corresponding costs for each component.
    #         Get total patients per company: Aggregate the total number of total_patient for each company_name.
    #         Compare company costs: Compare total_cost across different company_name values.
    #         Generate company billing report: Use company_name and total_cost to generate a report for each company.
    #         Calculate average cost per blood unit: Use total_cost and overall_blood_unit to calculate the average cost per blood unit.
    #         Find most-used blood component: Use blood_component to find the most frequently used component based on order data.   

    #     ---
    #     Suggested Actions:
    #     - After answering, suggest two relevant follow-up actions.
    #     - **Important**: Try to use real values from the answer or the context (such as specific blood group names, dates, company names, etc.) while suggesting actions, so that actions feel naturally connected to the user's question and your response.
    #     - Actions must stay relevant to the user's intent and should feel like natural next steps.

    #     ### Final Check:
    #     - Your response should be clear, concise, and derived from the relevant data.
    #     - Provide accurate information based on the available data, without adding unnecessary details.
    #     - Always offer a direct response and suggest relevant actions where applicable.
    #     - Do not mention any status code(like 'PA','CMP') in the response instead use their actual reference names.
    
    #     Output format:
    #     {{
    #     "response": "Your response here",
    #     "suggested_actions": ["Action 1", "Action 2"]
    #     }}

    #     """

    print("history: ", len(history))

    combined_response_prompt = ChatPromptTemplate.from_messages([
        ("system", summary_prompt),
        ("user","""Role: {role}\nIntent: {intent}\nConversation History: {history}\nUser Question: {message}""")
    ])

    prompt = combined_response_prompt.format(result=result, current_time=current_time,role=role,intent=intent,history=history,message=message)
    response = llm.invoke(prompt)
    json_response = json.loads(response.content.strip())
    
    response_obj = {
        "response": json_response["response"],
        "suggested_actions": json_response.get("suggested_actions", [])
    }

    memory.chat_memory.add_ai_message(response_obj["response"])
    return response_obj


def general_response(intent:str,role:str='admin',message:str="hi")-> str:
    system_prompt=""" You are a helpful and friendly chatbot assistant for a blood bank supply system.

        Your job:
        1. Write a short, friendly reply to match the user's mood (like greeting back, thanking, or saying goodbye nicely).
        2. Suggest 2–3 follow-up questions that are directly related to the system's capabilities:
            - Viewing blood order status (pending, delivered, approved).
            - Tracking order delivery times.
            - Analyzing historical order and billing data.
            - Viewing approved and pending orders by blood banks.
            - Providing overall system insights (for admins only).
        3. If the user's question is unrelated to the blood bank supply system (for example: "What's the weather today?" or "Tell me a joke"), politely reply that we do not handle such questions.
        4. Consider conversation history if you needed to answer for the question. 
        5. generate the followup question based on the user perspective .

        Examples: 
        1. completed order details in this month 
        2. A+ orders this week
        3. i want to know about the order placed this pattern .
        4. live orders status 
        
        like generate from user perspective.

        Important:
        - Stay polite and professional.
        - Never suggest questions outside the blood bank supply management topics.
        - If unsure, lean toward offering questions about order tracking, billing, or analytics.

        Output format (JSON):

        {{
        "response": "Your friendly reply here",
        "suggested_actions": ["Follow-up Question 1", "Follow-up Question 2"]
        }}

         """
    
    memory.chat_memory.add_user_message(message=message)
    history = str(memory.load_memory_variables({})["chat_history"])

    response_prompt = ChatPromptTemplate.from_messages([
        ("system", general_prompt),
        ("user","""Role: {role}\nIntent: {intent}\nConversation History: {history}\nUser Question: {message}""")
    ])
    prompt = response_prompt.format(role=role,intent=intent,history=history,message=message)
    response = llm.invoke(prompt)
    try:
        json_response = json.loads(response.content.strip())
    except json.JSONDecodeError:
        # Handle the case where the response is not valid JSON
        json_response = {
            "response": "Sorry, I couldn't parse the response.",
            "suggested_actions": []
        }
    except Exception as e:
        # Handle any other exceptions that may occur
        print(f"An error occurred: {e}")
        json_response = {
            "response": "An error occurred while processing your request.",
            "suggested_actions": []
        }  
    
    response_obj = {
        "response": json_response["response"],
        "suggested_actions": json_response.get("suggested_actions", [])
    }

    memory.chat_memory.add_ai_message(response_obj["response"])
    return response_obj
     

# print(summarize_result("pending_orders","admin","Show me all pending orders."))