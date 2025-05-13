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

class ResponseParsingError(ChatbotException):
    """Failed to parse LLM response"""
    pass

class DataRetrievalError(ChatbotException):
    """Failed to retrieve data from the database"""
    pass
class DataStorageError(ChatbotException):
    """Failed to store data in the database"""
    pass

class RateLimitingError(ChatbotException):  
    """Rate limit exceeded"""
    pass

class SummarizerError(ChatbotException):
    """Failed to summarize results"""
    pass

class UnexpectedError(ChatbotException):
    """Unexpected error in chatbot pipeline"""
    pass
