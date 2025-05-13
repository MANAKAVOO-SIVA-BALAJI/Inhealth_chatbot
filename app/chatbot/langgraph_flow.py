#app\chatbot\langgraph_flow.py

from app.exceptions import *
import structlog
from app.chatbot.graphql_client import run_graphql_query
from app.chatbot.summarizer import summarize_result , general_response
from app.chatbot.intent_query_generate import process_message
from app.chatbot.query_match import keyword_match

logger = structlog.get_logger()

from app.chatbot.utils import store_data


def chatbot_pipeline(user_message: str, role: str = "admin", context: dict = None):
    process_flow = [0,0,0,0]  # [intent_query_generation , keyword_match, graphql_execution, summarization]

    try:
        context = context or {"question":"","intent": "", "query": "", "raw_result": "", "summary": ""}
        logger.debug("Processing user message", role=role, message_length=len(user_message))
        context["question"] = user_message

        # 0. Combined intent and query generation

        try:
            query_output = process_message(user_message, role=role)
            intent = query_output.get("intent", "others")
            graphql_query = query_output.get("query", "")
            context["intent"] =  intent 
            context["query"] = graphql_query
            logger.info("Query generated", query_length=len(graphql_query))
            process_flow[0] = 1
        except Exception as e:
            logger.error("Query generation failed", exc_info=False)
            # store_data(context)
            # return context
            # raise QueryGenerationError(f"Failed to generate query: {str(e)}")
            
        # 1. Keyword matching

        # if process_flow[0] == 0 or context["query"].strip() == "" or context["query"] is None or context["intent"] == "others":
        if (
            process_flow[0] == 0 or
            not (context.get("query") or "").strip() or
            context.get("intent") == "others"
        ):

            try:
                intent , query = keyword_match(user_message)
                if query is not None and intent != "others":
                    context["query"] = query
                    context["intent"] = intent
                    logger.info("Keyword matching successful", intent=intent, query_length=len(query))
                    process_flow[1] = 1
                else:
                    context["query"] = ""
                    context["intent"] = "others"
                    process_flow[1] = 0
                    logger.info("Keyword matching failed", intent=intent)

            except Exception as e:
                logger.error("Keyword matching failed", exc_info=False)
        

        if context['intent'] in ["greetings","others","farewell",'history'] or  len(context['query']) <= 1:
            result = general_response(context['intent'],role=role,message=user_message)
            context["summary"]=result
            logger.info("general response generated")

            store_data(context)
            
            return context 


        # 2. Execute GraphQL query

        try:
            result = run_graphql_query(context["query"])
            context["raw_result"] = result
            logger.info("Query executed successfully", result_size=len(str(result)))
            process_flow[2] = 1
        except Exception as e:
            logger.error("GraphQL query execution failed", exc_info=False)
            store_data(context)

            raise GraphQLExecutionError(f"Failed to execute GraphQL query: {str(e)}")

        # 3. Summarize result
        
        try:
            summary = summarize_result(intent=context["intent"], role=role, message=user_message, result=context["raw_result"])
            context["summary"] = summary
            logger.info("Results summarized successfully")
            process_flow[3] = 1
        except Exception as e:
            logger.error("Summarization failed", exc_info=False)
            store_data(context)

            raise SummarizerError(f"Failed to summarize results: {str(e)}")
        
        store_data(context)

        return context
    except ChatbotException as e:
        logger.error("Chatbot error", error_type=type(e).__name__, error=str(e))
        store_data(context)
        return {"error": str(e), "error_type": type(e).__name__}
    except Exception as e:
        logger.error("Unexpected error in chatbot pipeline", exc_info=False)
        store_data(context)
        return {"error": "An unexpected error occurred. Please try again later.", "error_type": "UnexpectedError"}
    
