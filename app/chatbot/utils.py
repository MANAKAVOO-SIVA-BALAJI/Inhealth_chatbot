import json
import os
import datetime
import logging
from typing import List, Optional
import structlog
logger = structlog.get_logger()

def format_chat_history(messages: List[dict], columns: Optional[List[str]] = None) -> str:
    if not messages:
        return "No chat history found."
    
    formatted = []
    for idx, msg in enumerate(messages, 1):
        # If no columns specified, format all keys in message
        keys_to_format = columns if columns else list(msg.keys())
        
        # Filter out keys not present or with empty values
        keys_to_format = [k for k in keys_to_format if k in msg and msg[k] not in [None, ""]]
        
        if not keys_to_format:
            continue
        
        lines = [f"{idx}."]
        for key in keys_to_format:
            lines.append(f"- **{key.capitalize()}:** {msg[key]}")
        
        formatted.append("\n".join(lines))
    
    return "\n\n".join(formatted) if formatted else "No matching data found."

def get_current_datetime():
    logger.debug("Fetching current date and time")
    return datetime.datetime.now().strftime("Year: %Y, Month: %m, Day: %d, Time: %H:%M:%S")

def store_data(updates, file_path="output_data.json", max_records=1000):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    data = [data]
        else:
            data = []

        updates["timestamp"] = datetime.now().isoformat()
        data.insert(0, updates)

        if len(data) > max_records:
            data = data[:max_records]

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Error storing data: {str(e)}", exc_info=False)

# print(get_current_datetime())
