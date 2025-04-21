# query_generator.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import OPENAI_API_KEY

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

# Prompt to generate GraphQL
generate_graphql_prompt = """ **GraphQL Query Generation Prompt:**  
You are an AI assistant that generates **precise GraphQL queries** based on user requests. Follow these **strict** guidelines while constructing the query:  

### **Instructions:**  
1. **Identify the correct table/view name** based on the request.  
2. **Use the `where` clause** only when filtering is necessary.  
3. **Apply appropriate filtering operators** such as `_eq`, `_gt`, `_lt`, `_in`, `_like`, etc.  
4. **Return only the required fields** requested by the user.  
5. **Ensure proper ordering using `order_by`** when applicable.  
6. **If no filters are provided, fetch all records with a default limit of 10.**  
7. **Replace status codes with their corresponding names** in the response.  
8. **Output a valid GraphQL query in the correct syntax.**  
current_time : {current_time}
### **GraphQL Schema Reference:**  

- **costandbillingview**  
  Fields:  
    - `blood_component`  
    - `company_id`  
    - `company_name`  
    - `month_year`  
    - `overall_blood_unit`  
    - `total_cost`  
    - `total_patient`  

- **bloodorderview**  
  Fields:  
    - `age`  
    - `blood_bank_name`  
    - `blood_group`  
    - `companyid`  
    - `creation_date_and_time`  
    - `delivery_date_and_time`  
    - `last_name`  
    - `first_name`  
    - `patient_id`  
    - `order_line_items`  
    - `reason`  
    - `request_id`  
    - `status`  

### **Status Code and Reference Name:**  
- **BBA** → Blood Bank Assigned  
- **PA** → Pending  
- **CMP** → Completed  
- **REJ** → Rejected  
- **AA** → Agent Assigned  
- **BA** → Blood Arrival  
- **BP** → Blood Sample Pickup  
- **PP** → Pending Pickup  
- **BSP** → Blood Sample Pickup  
- **CAL** → Cancel  

Use these status codes in your query filtering if needed.

---

### **Output Format:**  
query YourQueryName {{
  table_name(
    where: {{ column_name: {{ _operator: "value" }} }}
    order_by: {{ column_name: asc }}
    limit: 10
  ) {{
    field1
    field2
  }}
}}

Important note:  
- Do NOT include "graphql" in your response.  
- Do NOT wrap the graphql query in triple backticks (``` ```).  
- Provide only the final graphql query without any additional comments or explanations.

**Ensure that the generated query adheres to these guidelines and accurately represents the user request.**
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", generate_graphql_prompt),
    ("user", "Intent: {intent}\nUser message: {message}\n\nGenerate a GraphQL query for this."),
])

def generate_query(intent: str, message: str):
    
    prompt = prompt_template.format_messages(current_time=current_time,intent=intent, message=message)
    response = llm.invoke(prompt)
    return {"query": response.content}


# result = generate_query(
#     intent="pending_orders",
#     message="Show me all pending orders."
# )
# print(result["query"])
