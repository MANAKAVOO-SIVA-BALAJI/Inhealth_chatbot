# summarizer.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import OPENAI_API_KEY
from datetime import datetime
import json
current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)


def summarize_result(intent: str, role: str="admin",message:str=None,result: dict = None) -> str:
    system_prompt = """You are an AI assistant named Inhealth that provides helpful information and answers corresponding to user queries based on retrieved database data. Format your response as a short and natural chat reply.
            Context:
            Relevant Data: {result}
            Formatting Guidelines:
            Keep the response concise and precise.
            Directly answer the question without unnecessary details.
            Maintain a natural, conversational tone, like a chat message from the user.
            Use a clear and easy-to-understand format, including tables, charts, or visuals when appropriate.
            use a proper format in numbers and calculation when required with a flow.
            Avoid introductory phrases like "Based on the data" or "According to the information."
            If the data does not contain the answer, politely state that the information is unavailable rather than guessing.
 
            Mandandory: Make sure the suggested action should be related to the question and importantly that can be answer using the data.
            
            Show corresponding status name instead of status code in the response.
            For your reference status code and name:
             BBA-blood_bank_assinged , PA-pending, CMP -completed ,REJ-rejected ,AA-agent assigned , BA-blood arrival, BP-blood sample pickup,PP-pending pickup , BSP-blood sample pickup, CAL-Cancel
            Current date and time: {current_time}
            Actions for bloodorderview:

            Check order status (by request_id)
            Filter orders (by blood_group, blood_bank_name)
            View pending (PA)
            completed (CMP)
            rejected (REJ) orders
            Find orders in a date range
            Get agent-assigned (AA) orders
            Count orders by blood bank

            Actions for costandbillingview:

            View total cost & blood usage (by company_id)
            Check cost by month
            List company billing (company_name, total_cost)
            Find cost by blood component
            Get total patients per company
            Compare company costs
            Find most-used blood component
            Calculate avg. 
            cost per blood unit
            Generate company billing report
            
            suggest  relevant two actions only from the above actions 
            use direct values in actions based on the data provided.

            Output format:
            {{
            "response": "Your response here",
            "suggested_actions": ["Action 1", "Action 2"]
            }}
            
"""
    
    response_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user",f"""Role: {role}\nIntent: {intent}\nUser Question: {message}""")
    ]).format(result=result, current_time=current_time)
    prompt = response_prompt #.format_messages(intent=intent, result=result)
    response = llm.invoke(prompt)
    json_response = json.loads(response.content.strip())
    
    response_obj = {
        "response": json_response["response"],
        "suggested_actions": json_response.get("suggested_actions", [])
    }
    return response_obj


# print(summarize_result("pending_orders","admin","Show me all pending orders."))