import json
import os
from datetime import datetime
import logging

import structlog
logger = structlog.get_logger()

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
        logging.error(f"Error storing data: {str(e)}", exc_info=True)