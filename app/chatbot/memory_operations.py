
from app.chatbot.graphql_client import run_graphql_query
from app.chatbot.mutation_query import get_chat_session_messages


class ChatMemory:
    def __init__(self):
        self.memory_dict = {}
        self.session_ids = set()
        self.session_ids.add("default")
        self.memory_dict["default"] = []

    def get_session_messages_hasura(self,session_id: str):
        # print("Fetching session messages from Hasura for session_id:", session_id)
        history = run_graphql_query(query=get_chat_session_messages["query"],variables={"session_id":session_id})
        print("history(from Hasura): ",len(history))
        
        if "chatmessages" in history:
            self.memory_dict[session_id] = history["chatmessages"]
            self.session_ids.add(session_id)
            return history["chatmessages"]
        elif "errors" in history:
            print("Error in GraphQL query:", history["errors"])
            return []
        return []

    def get_session_messages(self, session_id: str):
        if session_id in self.memory_dict:
            print("Fetching session messages from RAM memory for session_id:", session_id)
            return self.memory_dict.get(session_id, [])
        return self.get_session_messages_hasura(session_id=session_id)

    def add_user_message(self, session_id: str, message: dict):
        if session_id not in self.memory_dict:
            self.memory_dict[session_id] = []
            self.session_ids.add(session_id)
        self.memory_dict[session_id].append(message)
    
    def add_session_id(self, session_id: str):
        if session_id not in self.session_ids:
            self.session_ids.add(session_id)
            self.memory_dict[session_id] = []

        
# memory = ChatMemory()

