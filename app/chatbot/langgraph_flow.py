#app\chatbot\langgraph_flow.py

from app.exceptions import *
import structlog
from app.chatbot.graphql_client import run_graphql_query
from app.chatbot.summarizer import summarize_result , general_response
from app.chatbot.intent_query_generate import process_message
from app.chatbot.query_match import keyword_match

logger = structlog.get_logger()

from app.chatbot.utils import store_data

default_context = {"usermessage":"","intent": "", "querygenerated": "", "raw_result": "", "airesponse": "","history": [],"error": None}

def chatbot_pipeline( context: dict = default_context): 
    process_flow = [0,0,0,0]  # [intent_query_generation , keyword_match, graphql_execution, summarization]
    chat_record = {
    "usermessage": "",
    "airesponse": "",
    "intent": None,
    "querygenerated": None,
    "createdat": None
    }

    try:
        #context = context or {"usermessage":"","intent": "", "querygenerated": "", "raw_result": "", "airesponse": "","history": [],"error": None}
        # return context
        user_message = context.get("usermessage", "")
        if not user_message:
            return context
        logger.info("Processing user message", message_length=len(user_message))

        # 0. Combined intent and query generation
        try:
            query_output = process_message(user_message,context.get("history",[])) # {"intent": "", "query": ""}
            intent = query_output.get("intent", "others")
            graphql_query = query_output.get("query", "")
            context["intent"] =  intent 
            context["querygenerated"] = graphql_query
            logger.info("Query generated", query_length=len(graphql_query))
            process_flow[0] = 1
        except Exception as e:
            logger.error("Query generation failed", exc_info=False)
            
        # 1. Keyword matching [fallback]
        if (
            process_flow[0] == 0 or
            not (context.get("querygenerated") or "").strip() or
            context.get("intent") == "others"
        ):
            try:
                intent , query = keyword_match(user_message)
                if query is not None and intent != "others":
                    context["querygenerated"] = query
                    context["intent"] = intent
                    logger.info("Keyword matching successful", intent=intent, query_length=len(query))
                    process_flow[1] = 1
                else:
                    context["querygenerated"] = ""
                    context["intent"] = "others"
                    process_flow[1] = 0
                    logger.info("Keyword matching failed", intent=intent)

            except Exception as e:
                logger.error("Keyword matching failed", exc_info=False)

        if context['intent'] in ["greetings","others","farewell",'history'] or  len(context['querygenerated']) <= 1:
            result = general_response(context['intent'],message=user_message, history=context["history"])
            context["airesponse"]=result
            logger.info("General response generated")
            
            return context 

        # 2. Execute GraphQL query

        try:
            result = run_graphql_query(context["querygenerated"])
            context["raw_result"] = result
            logger.info("Query executed successfully", result_size=len(str(result)))
            process_flow[2] = 1
        except Exception as e:
            logger.error("GraphQL query execution failed", exc_info=False)
            # store_data(context)
            raise GraphQLExecutionError(f"Failed to execute GraphQL query: {str(e)}")
            return {"error": str(e), "error_type": type(e).__name__}            

        # 3. Summarize result
        
        try:
            summary = summarize_result(intent=context["intent"],  message=user_message, result=context["raw_result"], history=context["history"])
            context["airesponse"] = summary
            logger.debug("Results summarized successfully")
            process_flow[3] = 1
        except Exception as e:
            logger.error("Summarization failed", exc_info=False)
            context["error"] = str(e)
            context["error_type"] = type(e).__name__
            return context
            # return {"error": str(e), "error_type": type(e).__name__}
            
        return context
    except ChatbotException as e:
        logger.error("Chatbot error", error_type=type(e).__name__, error=str(e))
        context["error"] = str(e)
        context["error_type"] = type(e).__name__
        return context
        # return {"error": str(e), "error_type": type(e).__name__}
    except Exception as e:
        logger.error("Unexpected error in chatbot pipeline",error=str(e), exc_info=False)
        context["error"] = str(e)
        context["error_type"] = type(e).__name__
        return context
        # return {"error": "An unexpected error occurred. Please try again later.", "error_type": "UnexpectedError"}

