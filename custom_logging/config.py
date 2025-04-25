# # # logging/config.py

# # import logging
# # import structlog
# # from app.config import settings

# # def configure_logging():
# #     logging.basicConfig(
# #         format="%(message)s",
# #         level=logging.INFO,
# #         handlers=[logging.StreamHandler()],
# #     )
# #     log_level = settings.LOG_LEVEL.upper()
# #     log_format = "json" #if not settings.APP_DEBUG else "plain"
# #     shared_processors = [
# #         structlog.processors.add_log_level,
# #         structlog.stdlib.add_logger_name,
# #         structlog.processors.TimeStamper(fmt="iso"),
# #         structlog.processors.StackInfoRenderer(),
# #         structlog.processors.format_exc_info,
# #     ]

# #     if log_format == "json":
# #         shared_processors.append(structlog.processors.JSONRenderer())
# #     else:
# #         shared_processors.append(structlog.dev.ConsoleRenderer()) 

# #     structlog.configure(
# #         processors=shared_processors,
# #         context_class=dict,
# #         logger_factory=structlog.stdlib.LoggerFactory(),
# #         wrapper_class=structlog.stdlib.BoundLogger,
# #         cache_logger_on_first_use=True,
# #     )


# import logging
# import sys
# import structlog
# from app.config import settings

# def configure_logging():
#     # Set up shared processors
#     shared_processors = [
#         structlog.processors.add_log_level,
#         structlog.stdlib.add_logger_name,
#         structlog.processors.TimeStamper(fmt="iso"),
#         structlog.processors.StackInfoRenderer(),
#         structlog.processors.format_exc_info,
#     ]
    
#     # Determine log format based on debug setting
#     log_level = settings.LOG_LEVEL.upper()
#     is_debug = settings.APP_DEBUG
    
#     if is_debug:
#         # Development logging: pretty, colorized console output
#         processors = [
#             *shared_processors,
#             structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
#         ]
        
#         structlog.configure(
#             processors=processors,
#             context_class=dict,
#             logger_factory=structlog.stdlib.LoggerFactory(),
#             wrapper_class=structlog.stdlib.BoundLogger,
#             cache_logger_on_first_use=True,
#         )
        
#         formatter = structlog.stdlib.ProcessorFormatter(
#             processor=structlog.dev.ConsoleRenderer(colors=True),
#         )
        
#         handler = logging.StreamHandler(sys.stdout)
#         handler.setFormatter(formatter)
        
#         root_logger = logging.getLogger()
#         root_logger.handlers = [handler]  # Replace existing handlers
#         root_logger.setLevel(getattr(logging, log_level, logging.INFO))
        
#     else:
#         # Production logging: JSON output
#         processors = [
#             *shared_processors,
#             structlog.processors.JSONRenderer(),
#         ]
        
#         structlog.configure(
#             processors=processors,
#             context_class=dict,
#             logger_factory=structlog.stdlib.LoggerFactory(),
#             wrapper_class=structlog.stdlib.BoundLogger,
#             cache_logger_on_first_use=True,
#         )
        
#         handler = logging.StreamHandler(sys.stdout)
#         handler.setFormatter(logging.Formatter("%(message)s"))
        
#         root_logger = logging.getLogger()
#         root_logger.handlers = [handler]  # Replace existing handlers
#         root_logger.setLevel(getattr(logging, log_level, logging.INFO))
#         logging.getLogger('gql').setLevel(logging.WARNING)
#         logging.getLogger('gql.transport.requests').setLevel(logging.WARNING)
#         logging.getLogger('requests').setLevel(logging.WARNING)
#         logging.getLogger('urllib3').setLevel(logging.WARNING)

import logging
import sys
import structlog
from app.config import settings

def configure_logging():
    # Set up shared processors
    shared_processors = [
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Determine log format based on debug setting
    log_level = settings.LOG_LEVEL.upper()
    is_debug = settings.APP_DEBUG
    
    if is_debug:
        # Development logging: pretty, colorized console output
        processors = [
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]
        
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
        )
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.handlers = [handler]  # Replace existing handlers
        root_logger.setLevel(getattr(logging, log_level, logging.INFO))
        
    else:
        # Production logging: JSON output
        processors = [
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ]
        
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        
        root_logger = logging.getLogger()
        root_logger.handlers = [handler]  # Replace existing handlers
        root_logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Suppress verbose logs from GraphQL libraries and HTTP requests
 # Set log levels for `gql` and related libraries
    logging.getLogger('gql').setLevel(logging.CRITICAL)  # Suppress gql logs
    logging.getLogger('gql.transport.requests').setLevel(logging.CRITICAL)  # Suppress gql transport logs
    logging.getLogger('requests').setLevel(logging.CRITICAL)  # Suppress requests logs
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)  # Suppress urllib3 logs

