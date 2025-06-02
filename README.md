# Live Data chatbot

# Blood Bank Chatbot API Documentation

##  Base URL
```

[http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)

````

## Run the Project

```bash
uvicorn api.main:app --reload
````

---

## 1️⃣ Test Connection

* **Endpoint**: `GET /api/v1/`
* **Full URL**: `http://127.0.0.1:8000/api/v1/`

### 🔐 Headers

```
X-API-KEY: 123456789
```

### 🧾 Body

```json
{}
```

### 📥 Response

#### Headers:

```
content-length: 52  
content-type: application/json  
date: Tue, 06 May 2025 11:51:59 GMT  
server: uvicorn  
x-ratelimit-limit: 60  
x-ratelimit-remaining: 55  
x-ratelimit-reset: 1746532379  
x-request-id: d07a9ea5-2ee6-4131-9c2e-17d7b5470e6a  
```

#### Body:

```json
{
  "message": "Connected to Blood Bank Chatbot API!"
}
```

---

## 2️⃣ Chat with Bot

* **Endpoint**: `POST /api/v1/chat`
* **Full URL**: `http://127.0.0.1:8000/api/v1/chat`

### 🔐 Headers

```
X-API-KEY: 123456789
```

### 🧾 Body

```json
{
  "message": "how many pending orders are there,",
  "role": "admin"
}
```

### 📥 Response

#### Headers:

```
content-length: 52  
content-type: application/json  
date: Tue, 06 May 2025 11:51:59 GMT  
server: uvicorn  
x-ratelimit-limit: 60  
x-ratelimit-remaining: 55  
x-ratelimit-reset: 1746532379  
x-request-id: d07a9ea5-2ee6-4131-9c2e-17d7b5470e6a  
```

#### Body:

```json
{
  "response": "There are currently 3 pending orders.",
  "suggested_actions": [
    "View pending (PA) orders",
    "Count orders by blood bank"
  ],
  "error": null,
  "error_type": null
}
```

---

## 🧮 Tables and Columns

### `bloodorderview`

* `age`
* `blood_bank_name`
* `blood_group`
* `companyid`
* `creation_date_and_time`
* `delivery_date_and_time`
* `last_name`
* `first_name`
* `patient_id`
* `order_line_items`
* `reason`
* `request_id`
* `status`

### `costandbillingview`

* `blood_component`
* `company_id`
* `company_name`
* `month_year`
* `overall_blood_unit`
* `total_cost`
* `total_patient`

---

## 🔍 Sample GraphQL Queries

| Name                                   | Description                   | Query                                                                                                                                     |
| -------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **All_Orders**                        | Get all blood orders          | `query { bloodorderview { request_id first_name last_name blood_group status blood_bank_name } }`                                         |
| **Order_Status**                      | Status by request ID          | `query { bloodorderview { request_id first_name status blood_group status blood_bank_name } }`                                            |
| **Pending_Orders**                    | Status: PA                    | `query { bloodorderview(where: {status: {_eq: "PA"}}) { request_id first_name last_name blood_group status blood_bank_name } }`           |
| **Approved_Orders**                   | Status: AA                    | `query { bloodorderview(where: {status: {_eq: "AA"}}) { request_id first_name last_name blood_group status blood_bank_name } }`           |
| **Rejected_Orders**                   | Status: REJ                   | `query { bloodorderview(where: {status: {_eq: "REJ"}}) { request_id first_name last_name blood_group status blood_bank_name } }`          |
| **Orders_By_Blood_Type**            | Orders by blood type          | `query { bloodorderview { request_id first_name last_name blood_group status blood_bank_name } }`                                         |
| **Orders_By_BloodBank**              | Orders by blood bank          | `query { bloodorderview { request_id first_name last_name blood_group status } }`                                                         |
| **Orders_By_Status_And_BloodBank** | Orders by status & blood bank | `query { bloodorderview { request_id first_name last_name blood_group status } }`                                                         |
| **Total_Orders_By_BloodBank**       | Total orders by bank          | `query { bloodorderview { request_id first_name last_name blood_group status } }`                                                         |
| **Billing_Overview**                  | Cost & patients overview      | `query { costandbillingview { company_name month overall_blood_unit total_cost total_patient } }`                                         |
| **Billing_By_Company**               | Billing per hospital          | `query { costandbillingview { company_name blood_component total_cost overall_blood_unit } }`                                             |
| **Cost_By_Blood_Component**         | Cost per component            | `query { costandbillingview { blood_component company_name total_cost } }`                                                                |
| **Total_Patients_By_Company**       | Total patients by company     | `query { costandbillingview { company_name total_patient } }`                                                                             |
| **Blood_Usage_By_Company**          | Blood usage stats             | `query { costandbillingview { company_name overall_blood_unit } }`                                                                        |
| **Recent_Orders**                     | Most recent 5 orders          | `query { bloodorderview(order_by: {request_id: desc}, limit: 5) { request_id first_name last_name blood_group status blood_bank_name } }` |
| **farewell**                           | End the conversation          | `"Thank you, let me know if there is anything else I can help you with."`                                                                 |
| **greetings**                          | Greet user                    | `{ "Hello! How can I help you today?" }`                                                                                                  |
| **others**                             | Unknown queries               | `""`                                                                                                                                      |

---

## 🐳 Docker Deployment

### 🔄 Apply `.env` changes

```bash
# Stop current container
docker stop bdd93f651d70c279227ee1eba968cba665356b53ab8f5cbfa9898ab931ef3e59

# Restart with updated env
docker run -d -p 8000:8000 --env-file .env my-fastapi-app
```

### 🔧 If you change app code

```bash
# Rebuild Docker image
docker build -t my-fastapi-app .

# Stop and remove old container
docker stop <container_id>
docker rm <container_id>

# Run new container
docker run -d -p 8000:8000 --env-file .env my-fastapi-app
```

---

## 🧠 Redis Setup

```bash
docker run -d -p 6379:6379 --name redis-server redis
```
