import numpy as np
import re
from nltk import word_tokenize
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
import string
import json
import time

def text_preprocessing(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = word_tokenize(text)
    text = [lemmatizer.lemmatize(word) for word in text if word not in stop_words and word not in string.punctuation]
    text = ' '.join(text)
    return text

def keyword_match(user_question):
    # print("keyword_match")

    keywords = {
        "All_Orders": [
            "all", "orders", "every", "blood", "requests", "list", "get", "show", "display", "all orders",
            "placed", "all blood", "all requests", "many", "count", "overview", "complete list", "entire", "order history"
        ],
        "Order_Status": [
            "status", "check", "specific", "order", "id", "request", "get", "show", "display", "what happened",
            "track", "progress", "how is", "is it delivered", "update", "status of"
        ],
        "Pending_Orders": [
            "pending", "awaiting", "not approved", "waiting", "not yet approved", "still in process", "not processed"
        ],
        "Approved_Orders": [
            "approved", "confirmed", "validated", "greenlit", "accepted", "processed", "finalized"
        ],
        "Rejected_Orders": [
            "rejected", "declined", "not accepted", "denied", "cancelled", "refused", "dismissed"
        ],
        "Orders_By_Blood_Type": [
            "order", "sort", "blood", "type", "list", "group", "get", "show", "display",
            "grouped by blood type", "a positive", "b negative", "o+", "order by blood group"
        ],
        "Orders_By_BloodBank": [
            "order", "bank name", "blood", "bank", "group", "get", "show", "display", "list",
            "per bank", "bloodbank wise", "each blood bank", "individual blood banks"
        ],
        "Orders_By_Status_And_BloodBank": [
            "order", "status", "blood type", "blood", "bank name", "bank", "group",
            "status-wise per blood bank", "pending from", "approved orders from", "by bank and status"
        ],
        "Total_Orders_By_BloodBank": [
            "total", "order", "bank", "blood", "count", "find", "get", "show", "display", "summarise",
            "count per blood bank", "how many orders", "number of orders per", "summary"
        ],
        "Billing_Overview": [
            "bill", "cost", "amount", "blood", "bank", "money", "hospital", "overview", "find", "get", "show", "display",
            "total cost", "overall billing", "invoice", "how much spent", "payment summary"
        ],
        "Billing_By_Company": [
            "bill", "cost", "amount", "blood", "bank", "money", "hospital", "find", "company",
            "charges by hospital", "cost per company", "bills by organization"
        ],
        "Cost_By_Blood_Component": [
            "cost", "money", "expenses", "blood", "component", "group", "find", "hospital", "get", "show", "display",
            "platelets cost", "how much per unit", "red cells price", "breakdown by component"
        ],
        "Total_Patients_By_Company": [
            "total", "patient", "blood bank", "group", "find", "get", "show", "display",
            "served patients", "how many patients", "hospital-wise patients"
        ],
        "Blood_Usage_By_Company": [
            "blood", "units", "usage", "supply", "blood bank", "group", "find", "hospital",
            "used blood", "supply details", "how much each hospital used"
        ],
        "Recent_Orders": [
            "recent", "new", "latest", "current", "get", "show", "display", "order",
            "what's new", "last few orders", "today's orders", "latest requests"
        ],
        "greetings": [
            "hi", "hello", "good", "hey", "vanakam", "hi there", "greetings", "howdy", "morning", "good evening","good night","good day",
        ],
        "thank_you": [
            "bye", "see", "thanks", "you", "end", "thank you", "see you", "close", "exit", "that’s all"
        ],
        "others": [] 
}

    user_question = text_preprocessing(user_question)
    words = re.findall(r'\b\w+\b', user_question)
    
    scores = {}
    for query_type, key_words in keywords.items():
        scores[query_type] = sum(1 for word in words if word in key_words)
    
    best_query_type = max(scores.items(), key=lambda x: x[1])[0]
    
    if scores[best_query_type] < 1:
        best_query_type = "others"
    
    with open("queries.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    print("Best query type:", best_query_type)
    print("Query:", data.get(best_query_type,{}).get("query",None))
    return best_query_type ,data.get(best_query_type,{}).get("query",None)

    # return best_query_type



# import datetime
# print("Current time:", datetime.datetime.now().strftime("%H:%M:%S"))

# print(keyword_match("Can you show me the status of my order?")) 

# print("Current time:", datetime.datetime.now().strftime("%H:%M:%S"))

