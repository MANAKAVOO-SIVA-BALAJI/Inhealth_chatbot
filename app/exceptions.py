# app/exceptions.py
class ChatbotException(Exception):
    """Base exception for all chatbot errors"""
    pass

class IntentClassificationError(ChatbotException):
    """Failed to classify intent"""
    pass

class QueryGenerationError(ChatbotException):
    """Failed to generate GraphQL query"""
    pass

class GraphQLExecutionError(ChatbotException):
    """Failed to execute GraphQL query"""
    pass

class SummarizerError(ChatbotException):
    """Failed to summarize results"""
    pass

class UnexpectedError(ChatbotException):
    """Unexpected error in chatbot pipeline"""
    pass
