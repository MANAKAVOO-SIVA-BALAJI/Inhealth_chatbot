# # langgraph_flow.py

# from app.chatbot.intent_classifier import classify_intent
# from app.chatbot.query_generator import generate_query
# from app.chatbot.graphql_client import run_graphql_query
# from app.chatbot.summarizer import summarize_result
# from app.chatbot.schema_validator import get_hasura_schema, field_exists
# import os
# import json


# def store_data(updates):
#     file_path = "output_data.json"
#     if os.path.exists(file_path):
#         try:
#             with open(file_path, "r") as file:
#                 data = json.load(file)

#                 if not isinstance(data, list):
#                     data = [data]
#         except json.JSONDecodeError:
#             data = []
#     else:
#         data = []
    
#     data.insert(0,updates)

#     with open(file_path, "w") as file:
#         json.dump(data, file, indent=4)


# def chatbot_pipeline(user_message: str, role:str="admin",context: dict = None):
#     context = context or {"intent":"","query":"","raw_result":"","summary":""}
#     print(f"User message: {user_message}")

#     # 1. Classify user intent
#     intent = classify_intent(user_message, role=role)
#     print(f"Intent classified: {intent}")
#     context["intent"] = intent

#     if intent is None:
#         return {"error": "Unable to classify intent."}
 
#     if intent in ["others","farewell","greetings","thank_you"]:
#         print("summarize_result")
#         summary = summarize_result(intent=intent, role=role,message=user_message,result={})
#         context["summary"] = summary
#         return context
  

#     # 2. Generate GraphQL query
#     print("generate_query")
#     query_output = generate_query(intent=intent, message=user_message)
#     print(f"Generated query: {query_output['query']}")
#     graphql_query = query_output["query"]
#     context["query"] = graphql_query

#     # Optional: Validate query against Hasura schema
#     # schema = get_hasura_schema()
#     # validate_query(schema, graphql_query)  # Optional future implementation

#     # 3. Execute GraphQL query
#     result = run_graphql_query(graphql_query)
#     context["raw_result"] = result

#     # 4. Summarize result
#     print("summarize_result")
#     summary = summarize_result(intent=intent, role=role,message=user_message, result=result)
#     context["summary"] = summary

#     return context



# app/chatbot/langgraph_flow.py
# from app.exceptions import *
# import logging
# from app.chatbot.intent_classifier import classify_intent
# from app.chatbot.query_generator import generate_query
# from app.chatbot.graphql_client import run_graphql_query
# from app.chatbot.summarizer import summarize_result
# # from app.chatbot.schema_validator import get_hasura_schema, field_exists

# logger = logging.getLogger(__name__)
 
# def chatbot_pipeline(user_message: str, role:str="admin", context: dict = None):
#     try:
#         context = context or {"intent":"", "query":"", "raw_result":"", "summary":""}
#         logger.info("Processing user message", role=role, message_length=len(user_message))

#         # 1. Classify user intent
#         try:
#             intent = classify_intent(user_message, role=role)
#             logger.info("Intent classified", intent=intent)
#             context["intent"] = intent
#         except Exception as e:
#             logger.error("Intent classification failed", exc_info=True)
#             raise IntentClassificationError(f"Failed to classify intent: {str(e)}")

#         if intent in ["others", "farewell", "greetings", "thank_you"]:
#             try:
#                 summary = summarize_result(intent=intent, role=role, message=user_message, result={})
#                 context["summary"] = summary
#                 return context
#             except Exception as e:
#                 logger.error("Summarization failed for general intent", exc_info=True)
#                 raise SummarizerError(f"Failed to summarize general intent: {str(e)}")

#         # 2. Generate GraphQL query
#         try:
#             query_output = generate_query(intent=intent, message=user_message)
#             graphql_query = query_output["query"]
#             context["query"] = graphql_query
#             logger.info("Query generated", query_length=len(graphql_query))
#         except Exception as e:
#             logger.error("Query generation failed", exc_info=True)
#             raise QueryGenerationError(f"Failed to generate query: {str(e)}")

#         # 3. Execute GraphQL query
#         try:
#             result = run_graphql_query(graphql_query)
#             context["raw_result"] = result
#             logger.info("Query executed successfully", result_size=len(str(result)))
#         except Exception as e:
#             logger.error("GraphQL query execution failed", exc_info=True)
#             raise GraphQLExecutionError(f"Failed to execute GraphQL query: {str(e)}")

#         # 4. Summarize result
#         try:
#             summary = summarize_result(intent=intent, role=role, message=user_message, result=result)
#             context["summary"] = summary
#             logger.info("Results summarized successfully")
#         except Exception as e:
#             logger.error("Summarization failed", exc_info=True)
#             raise SummarizerError(f"Failed to summarize results: {str(e)}")

#         return context
#     except ChatbotException as e:
#         logger.error("Chatbot error", error_type=type(e).__name__, error=str(e))
#         return {"error": str(e), "error_type": type(e).__name__}
#     except Exception as e:
#         logger.error("Unexpected error in chatbot pipeline", exc_info=True)
#         return {"error": "An unexpected error occurred. Please try again later.", "error_type": "UnexpectedError"}
    
# filepath: d:\Projects\langchain\app\chatbot\langgraph_flow.py
from app.exceptions import *
import structlog
from app.chatbot.intent_classifier import classify_intent
from app.chatbot.query_generator import generate_query
from app.chatbot.graphql_client import run_graphql_query
from app.chatbot.summarizer import summarize_result

logger = structlog.get_logger()

def chatbot_pipeline(user_message: str, role: str = "admin", context: dict = None):
    try:
        context = context or {"intent": "", "query": "", "raw_result": "", "summary": ""}
        logger.info("Processing user message", role=role, message_length=len(user_message))

        # 1. Classify user intent
        try:
            intent = classify_intent(user_message, role=role)
            logger.info("Intent classified", intent=intent)
            context["intent"] = intent
        except Exception as e:
            logger.error("Intent classification failed", exc_info=True)
            raise IntentClassificationError(f"Failed to classify intent: {str(e)}")


        if intent in ["others", "farewell", "greetings", "thank_you"]:
            try:
                summary = summarize_result(intent=intent, role=role, message=user_message, result={})
                context["summary"] = summary
                return context
            except Exception as e:
                logger.error("Summarization failed for general intent", exc_info=True)
                raise SummarizerError(f"Failed to summarize general intent: {str(e)}")

        # 2. Generate GraphQL query
        try:
            query_output = generate_query(intent=intent, message=user_message)
            graphql_query = query_output["query"]
            context["query"] = graphql_query
            logger.info("Query generated", query_length=len(graphql_query))
        except Exception as e:
            logger.error("Query generation failed", exc_info=True)
            raise QueryGenerationError(f"Failed to generate query: {str(e)}")

        # 3. Execute GraphQL query
        try:
            result = run_graphql_query(graphql_query)
            context["raw_result"] = result
            logger.info("Query executed successfully", result_size=len(str(result)))
        except Exception as e:
            logger.error("GraphQL query execution failed", exc_info=True)
            raise GraphQLExecutionError(f"Failed to execute GraphQL query: {str(e)}")

        # 4. Summarize result
        try:
            summary = summarize_result(intent=intent, role=role, message=user_message, result=result)
            context["summary"] = summary
            logger.info("Results summarized successfully")
        except Exception as e:
            logger.error("Summarization failed", exc_info=True)
            raise SummarizerError(f"Failed to summarize results: {str(e)}")

        return context
    except ChatbotException as e:
        logger.error("Chatbot error", error_type=type(e).__name__, error=str(e))
        return {"error": str(e), "error_type": type(e).__name__}
    except Exception as e:
        logger.error("Unexpected error in chatbot pipeline", exc_info=True)
        return {"error": "An unexpected error occurred. Please try again later.", "error_type": "UnexpectedError"}