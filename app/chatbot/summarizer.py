# app/chatbot/summarizer.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.chatbot.prompt import general_prompt, summary_prompt
from app.config import OPENAI_API_KEY
from datetime import datetime
import json
from app.chatbot.utils import format_chat_history
import structlog
import app.chatbot.utils as get_current_datetime
logger = structlog.get_logger()
current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

def response_parser(response: str) -> dict:
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


def summarize_result(intent: str, message: str = None,
                     result: dict = None, history: list = None) -> dict:
    # print("summarize_result called")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", summary_prompt),
        ("user", """\nIntent: {intent}\nConversation History: {history}\nUser Question: {message}\n Data Result: {result},\nCurrent time: {current_time}""")
    ])

    prompt = prompt_template.format(
        intent=intent,
        history=format_chat_history(history, columns=["usermessage", "airesponse"]),
        message=message,
        result=result,
        current_time= current_time #or get_current_datetime()
    )
    # print("Summarize response prompt", prompt)
    response = llm.invoke(prompt)
    parsed = response_parser(response.content)

    return parsed


def general_response(intent: str, message: str , history: list = None) -> dict:

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", general_prompt),
        ("user", """\nConversation History: {history}\nUser Question: {message} \nIntent: {intent} \nCurrent time:{current_time} """)
    ])

    prompt = prompt_template.format(
        intent=intent,
        history=format_chat_history(history, columns=["usermessage", "airesponse"]),
        message=message,
        current_time=current_time #get_current_datetime()
    )
    # print("General response prompt", prompt)
    response = llm.invoke(prompt)
    parsed = response_parser(response.content)

    return parsed

# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# # from langchain.memory import ConversationBufferMemory
# from app.chatbot.prompt import general_prompt , summary_prompt

# from app.config import OPENAI_API_KEY
# from datetime import datetime
# import json
# current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
# # from langchain.memory import ConversationBufferWindowMemory

# class Chat_Memory:
#     def __init__(self):
#         self.memory = {}  # Initialize memory as a dictionary
#         self.session_ids = set()  # Optional: Track active session IDs

#     def get_message(self, session_id: str = "default"):
#         return self.memory.get(session_id, [])

#     def add_user_message(self, session_id: str, message: str):
#         if session_id not in self.memory:
#             self.memory[session_id] = []
#         self.memory[session_id].append(message)
#         self.session_ids.add(session_id)

#     def get_session_messages(self, session_id: str):
#         # You can extend this to fetch from GraphQL or a database
#         return self.memory.get(session_id, ["data from graphql by session id"])

# memory = Chat_Memory()

# def response_parser(response: str) -> dict:
#     """{{
#         "response": "Your response here",
#         "suggested_actions": ["Action 1", "Action 2"]
#         }}
# """
    
#     try:
#         json_response = json.loads(response.strip())
#         return {
#             "response": json_response["response"],
#             "suggested_actions": json_response.get("suggested_actions", [])
#         }
#     except json.JSONDecodeError:
#         return {
#             "response": "Sorry, I couldn't parse the response.",
#             "suggested_actions": []
#         }

# def summarize_result(intent: str, role: str="admin",message:str=None,result: dict = None,session_id:str="default") -> str:

#     history = str(memory.get_message(session_id))
#     memory.add_user_message(session_id,{"role":'user',"question":message})

#     combined_response_prompt = ChatPromptTemplate.from_messages([
#         ("system", summary_prompt),
#         ("user","""Role: {role}\nIntent: {intent}\nConversation History: {history}\nUser Question: {message}""")
#     ])

#     prompt = combined_response_prompt.format(result=result, current_time=current_time,role=role,intent=intent,history=history,message=message)
#     response = llm.invoke(prompt)
#     json_response = json.loads(response.content.strip())
    
#     response_obj = {
#         "response": json_response["response"],
#         "suggested_actions": json_response.get("suggested_actions", [])
#     }
#     memory.add_user_message(session_id,{"role":"ai_response","response":response_obj["response"]})

#     return response_obj


# def general_response(intent:str,role:str='admin',message:str="hi",session_id:str="default")-> str:
#     history = str(memory.get_message(session_id))
#     memory.add_user_message(session_id,{"role":'user',"question":message})

#     response_prompt = ChatPromptTemplate.from_messages([
#         ("system", general_prompt),
#         ("user","""Role: {role}\nIntent: {intent}\nConversation History: {history}\nUser Question: {message}""")
#     ])
#     prompt = response_prompt.format(role=role,intent=intent,history=history,message=message)
#     response = llm.invoke(prompt)
#     try:
#         json_response = json.loads(response.content.strip())
#     except json.JSONDecodeError:
#         # Handle the case where the response is not valid JSON
#         json_response = {
#             "response": "Sorry, I couldn't parse the response.",
#             "suggested_actions": []
#         }
#     except Exception as e:
#         # Handle any other exceptions that may occur
#         print(f"An error occurred: {e}")
#         json_response = {
#             "response": "An error occurred while processing your request.",
#             "suggested_actions": []
#         }  
    
#     response_obj = {
#         "response": json_response["response"],
#         "suggested_actions": json_response.get("suggested_actions", [])
#     }
#     memory.add_user_message(session_id,{"role":"ai_response","response":response_obj["response"]})

#     return response_obj
     

# print(summarize_result("pending_orders","admin","Show me all pending orders."))
