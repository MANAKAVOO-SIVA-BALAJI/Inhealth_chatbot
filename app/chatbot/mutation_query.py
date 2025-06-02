from datetime import datetime

now = datetime.now()
date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
# print("Current date and time:", formatted)

chat_session_with_message_mutation ={
    "query":""" mutation chat_session_with_message_mutation(
  $airesponse: String!,
  $userid: String!,
  $date: timestamp!,
  $intent: String!,
  $querygenerated: String!,
  $usermessage: String!
) {
  insert_chatsessions_one(
    object: {
      userid: $userid,
      createdat: $date,
      chatmessages: {
        data: {
          airesponse: $airesponse,
          createdat: $date,
          intent: $intent,
          querygenerated: $querygenerated,
          usermessage: $usermessage
        }
      }
    }
  ) {
    id
  }
}
""",
    "variables": {
  "userid":"USR-IHI6SJSYB0",
  "date": date_time,
  "airesponse": "ai_response",
  "intent": "intent",
  "querygenerated": "query_generated",
  "usermessage": "user_message"}
,
"response": """ {
          "data": {
            "insert_chatsessions_one": {
              "id": "CSI-XFPIFCBPC7"
            }
          }
        } """

}


chat_message_mutation ={
    "query":""" mutation chat_message_mutation(
  $airesponse: String!,
  $date: timestamp!,
  $intent: String!,
  $querygenerated: String!,
  $sessionid: String!,
  $usermessage: String!
) {
  insert_chatmessages_one(object: {
    airesponse: $airesponse,
    createdat: $date, 
    intent: $intent, 
    querygenerated: $querygenerated, 
    sessionid: $sessionid, 
    usermessage: $usermessage}) {
    sessionid
  }
}
""",
    "variables": {
  "sessionid":"",
  "date": date_time,
  "airesponse": "ai_response",
  "intent": "intent",
  "querygenerated": "query_generated",
  "usermessage": "message from user"  
},
   
    "response": """ {
          "data": {
            "insert_chatmessages_one": {
              "sessionid": "CSI-XFPIFCBPC7"
            }
          }
        } """
}


chat_session_mutation = {
    "query": """
        mutation MyMutation($userid: String!, $date: timestamp!) {
  insert_chatsessions_one(object: {userid: $userid, createdat: $date}) {
    id
  }
}
    """,
    "variables": {
        "userid":"USR-IHI6SJSYB0",
        "date": date_time
            }
}


get_chat_session = {
#     "query":""" query MyQuery($session_id: String = "") {
#   chatsessions(where: {id: {_eq: $session_id}}) {
#     chatmessages {
#       airesponse
#       usermessage
#       intent
#     }
#   }
# } """,
#     "variables": {
#         "session_id":"CSI-QM7GIIM7HL"
#     }

}


get_chat_session_messages = {
    "query":""" query MyQuery($session_id: String = "") {
  chatmessages(where: {chatsession: {id: {_eq: $session_id}}}) {
      usermessage
      airesponse
      querygenerated
      intent
      }
    } """,

    "variables": {
      "session_id":"CSI-QM7GIIM7HL"
    }

}

