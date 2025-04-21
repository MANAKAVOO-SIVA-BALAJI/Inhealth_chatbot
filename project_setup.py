import os

project_structure = [
    "app/chatbot",
    "api",
    "tests"
]

files = [
    "app/__init__.py",
    "app/config.py",
    "app/chatbot/__init__.py",
    "app/chatbot/langgraph_flow.py",
    "app/chatbot/intent_classifier.py",
    "app/chatbot/query_generator.py",
    "app/chatbot/graphql_client.py",
    "app/chatbot/summarizer.py",
    "app/chatbot/utils.py",
    "api/__init__.py",
    "api/main.py",
    "api/routes.py",
    "api/schemas.py",
    "tests/test_intents.py",
    "tests/test_graphql.py",
    "tests/test_chat_flow.py",
    ".env",
    "requirements.txt",
    "README.md"
]

# Create directories
for path in project_structure:
    os.makedirs(path, exist_ok=True)

# Create empty files
for file_path in files:
    with open(file_path, 'w') as f:
        pass

print("✅ Project structure created successfully.")
