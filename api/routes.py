
# api/routes.py
from fastapi import APIRouter, Request, Depends, HTTPException 
from fastapi import status
from fastapi.responses import JSONResponse
from app.chatbot.langgraph_flow import chatbot_pipeline
from api.schemas import ChatRequest, ChatResponse , FaqRequest, FaqResponse
from app.config import settings
from datetime import datetime
from app.chatbot.utils import store_data
import structlog
from app.chatbot.mutation_query import chat_message_mutation,chat_session_with_message_mutation ,chat_session_mutation
from app.chatbot.graphql_client import run_graphql_mutation
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import HumanMessage, SystemMessage
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from app.dependencies import get_llm
from app.chatbot.memory_operations import ChatMemory
from app.cache import cache
from app.faqs.faqs_rag import ensure_embedding_model , main
import os
logger = structlog.get_logger()
router = APIRouter()

memory = ChatMemory()

if not os.path.exists("./models/bge-base-en-v1.5"):
    logger.info("Local embedding model not found, please download the model to ./models/bge-base-en-v1.5")
    ensure_embedding_model("./models/bge-base-en-v1.5")
if not os.path.exists("./faiss_index"):
    logger.info("FAISS index not found, please create the FAISS index first")
    main()  
embedding = HuggingFaceEmbeddings(
    model_name="./models/bge-base-en-v1.5",
    model_kwargs={"device": "cpu"},  
    encode_kwargs={"normalize_embeddings": True}
)
vectorstore = FAISS.load_local("./faiss_index", embedding,allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

@router.get("/")
async def root():
    logger.debug("Connection to inhlth Chatbot API!!!")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Connected to inhlth Chatbot API!!!"}) #{"message": "Connected to Blood Bank Chatbot API!"}



@router.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    logger.debug(f"Processing chat request for role: {request.role}")
    mutation_query={}
    history = []
    if "session_id" in request.model_dump() and request.session_id is not None:
        history = memory.get_session_messages(request.session_id) #
          # Limit history length
        logger.debug(f"Chat history length: {len(history)}")
        # history = history
        # If session_id is provided, use it to store the message
        mutation_query=chat_message_mutation
        mutation_query["variables"]["sessionid"] = request.session_id 
        logger.debug(f"Using existing chat session")
    else:
        # If session_id is not provided, create a new session
        
        mutation_query=chat_session_with_message_mutation
        mutation_query["variables"]["userid"] = request.user_id
        logger.info(f"Creating new chat session")
        # logger.debug(f"History length: {len(history)}")

    # return {"response": "testing response"}
    context = {"usermessage":request.message,"intent": "", "querygenerated": "", "raw_result": "", "airesponse": "" ,"history": history,"error": None}
    try:
        result = chatbot_pipeline(context=context)
        logger.debug(f"Chatbot pipeline result: {list(result.keys())}")

        if "error" in result and result["error"] is not None:
            return ChatResponse(
                response="Sorry, there was an issue retrieving the data from our system. Please try again in a few minutes.",
                error=result["error"],
                error_type=result.get("error_type", "UnknownError")
        )
        
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
        mutation_query["variables"]["usermessage"] = request.message
        mutation_query["variables"]["intent"] = result["intent"]
        mutation_query["variables"]["querygenerated"] = result["querygenerated"]
        mutation_query["variables"]["airesponse"] = result["airesponse"].get("response", "")      
        mutation_query["variables"]["date"] = date_time 

        mutation_query_result = run_graphql_mutation(mutation=mutation_query["query"], variables=mutation_query["variables"])

        # print("mutation_query_result: ",mutation_query_result)
        if "errors" not in mutation_query_result:
            if "insert_chatsessions_one" in mutation_query_result:
                session_id = mutation_query_result["insert_chatsessions_one"]["id"]
                logger.info(f"Chat session created with Session ID: {session_id}")
            elif "insert_chatmessages_one" in mutation_query_result:
                session_id = mutation_query_result["insert_chatmessages_one"]["sessionid"]
                logger.info(f"Chat message stored with Session ID: {session_id}")
            # memory.add_session_id(request.session_id)
            memory.add_user_message(request.session_id, {"user_message": request.message,"intent":result["intent"],"airesponse":result["airesponse"].get("response", "")})

        else:
            logger.error(f"Error storing chat session({request.session_id}): {mutation_query_result['errors']}")
            return ChatResponse(
                response="Bad message request.",
                error=mutation_query_result["errors"],
                error_type="MutationError"
            )

    except Exception as e:
        logger.error(f"Error in chatbot pipeline: {str(e)}", exc_info=False)
        return ChatResponse(
            response="Sorry, I couldn't process your request at the moment. Please try again later.",
            error=str(e),
            error_type="PipelineError"
        )
    
    # Extract response from the result
    if "airesponse" in result and isinstance(result["airesponse"], dict):
        return ChatResponse(
            response=result["airesponse"].get("response", "")
            # suggested_actions=result["airesponse"].get("suggested_actions", [])
        )
    else:
        return ChatResponse(
            response="I processed your request but couldn't generate a proper response.",
            error="Invalid response format",
            error_type="FormatError"
        )

WEBSITE_SUMMARY_CONTENT = """
InHlth is a healthcare logistics platform transforming the blood supply chain. It ensures timely, secure blood access for patients by empowering hospitals, blood banks, and delivery agents through digital innovation.

Key features include:
* **Blood Request Management:** For Normal, Emergency, and Reserved needs.
* **Inventory & Stock Matching:** Real-time views, compatibility validation, FIFO logic to reduce waste.
* **Logistics & Delivery:** Automated notifications, real-time tracking, proof-of-delivery.
* **Billing & Cost Management:** Pre-defined unit costs, admin-only access for financial oversight.
* **Dashboards & Notifications:** Role-specific dashboards and critical alerts.

It supports Hospital, Blood Bank, Delivery Agent, and Platform Administrator roles.

InHlth is HIPAA/DISHA compliant, using end-to-end encryption, role-based access, and no patient PII collection.

Partnerships are welcome; schedule a demo at https://inhlth.com.
Contact support: support@inhlth.com or +91 (917)6133-373.

Overall, InHlth streamlines blood logistics, boosts emergency readiness, cuts waste, and provides vital financial insights.
"""


@router.post("/faqs", response_model=FaqResponse)
async def query_faq(request: FaqRequest):
    logger.debug(f"Processing FAQ query request")
    question = request.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    cache_key = f"{question}"
    cached_result = cache.get(cache_key)
    logger.debug(f"Cache key: {cache_key}")
    logger.debug(f"Cached result: {cached_result}")
    if cached_result:
        logger.info("Faqs cache hit")
        return FaqResponse(response=cached_result, suggested_actions=[])

    results = retriever.invoke(question)
    answers = [doc.page_content for doc in results] 
    llm = get_llm()

    system_prompt = """
    You are InHlth Assistant, a helpful and knowledgeable chatbot designed to answer questions about the InHlth healthcare logistics platform.

    **Crucial Interpretation Rule:**
    * When a user refers to "you" or "your" in their question, always interpret it as referring to "InHlth" or "InHlth's" services/platform. For example, if a user asks "What do you do?", understand it as "What does InHlth do?". If they ask "What are your features?", understand it as "What are InHlth's features?".

    **Instructions for Answering:**
    1.  **Primary Source (FAQs):** First, attempt to answer the user's question using the 'Relevant FAQ Context' provided.
    2.  **Fallback (Website Overview):**
        * If the 'Relevant FAQ Context' is empty, completely irrelevant, or insufficient to answer the user's question, then *immediately* refer to the 'InHlth Website Overview' to provide a general answer. This is especially for broad questions like 'what is InHlth?', 'what do you do?', or 'tell me about your services?'.
    3.  **No Available Answer:** If the question is about InHlth but cannot be answered by *either* the specific FAQs *or* the general overview, then politely state that you cannot find a relevant answer and suggest contacting InHlth support (email: support@inhlth.com, phone: +91 (917)6133-373).
    4.  **Demo Suggestion (Rarely):** Occasionally, after providing a response, you may add a subtle suggestion like: "For a live demonstration, remember to fill out the form at Schedule a Demo - Inhlth.com!" or "Curious to see InHlth in action? Schedule a Demo - Inhlth.com".
    5.  **No Personal Information:** Do not ask for or provide any personal or patient-identifiable information.
    6.  **Direct and Concise:** Provide direct answers without unnecessary conversational filler.
    7.  **No Invention:** Do NOT invent information or use outside knowledge.
    8.  **Friendly Tone:** Maintain a helpful and friendly tone.
    """

    human_prompt_template = """
    User Question:
    {user_message}

    Relevant FAQ Context:
    {retrieved_chunks}

    ---
    InHlth Website Overview (Use ONLY if Relevant FAQ Context is insufficient or irrelevant):
    {website_summary}
    ---

    Answer:
    """

    human_prompt = human_prompt_template.format(
        user_message=question,
        retrieved_chunks="\n".join(answers),
        website_summary=WEBSITE_SUMMARY_CONTENT 
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])
    
    logger.debug("Retrived Context: ",answers)
    cache.set(cache_key, response.content)
    print("Cache:",cache.cache)
    return FaqResponse(response=response.content,suggested_actions=[])

