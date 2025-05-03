import json
import os
import re
import logging
from datetime import datetime

# === Configuration ===
JSON_FILE_PATH = r'C:\TEST\scrape.json'
LOG_FILE_PATH = r'C:\TEST\scrapelogfile.log'

# === Set up logging ===
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_json_from_callback(text):
    """
    Extracts JSON content from a JavaScript-style callback function.
    Assumes format: callback({...});
    """
    try:
        match = re.search(r'^[^(]*\((.*)\)[^)]*$', text.strip(), re.DOTALL)
        if not match:
            raise ValueError("No valid JSON found in callback wrapper.")
        return match.group(1)
    except Exception as e:
        raise ValueError(f"Failed to extract JSON: {e}")

def format_size(bytes_total):
    """
    Converts byte total to human-readable sizes.
    """
    KB = bytes_total / 1024
    MB = KB / 1024
    GB = MB / 1024
    TB = GB / 1024
    return bytes_total, KB, MB, GB, TB

def main():
    try:
        # Step 1: Read file
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            raw_data = file.read()

        # Step 2: Extract JSON from callback
        json_str = extract_json_from_callback(raw_data)

        # Step 3: Parse JSON
        data = json.loads(json_str)

        # Step 4: Sum item_size in response.docs
        docs = data.get("response", {}).get("docs", [])
        total_size = 0
        for doc in docs:
            size = doc.get("item_size", 0)
            if isinstance(size, (int, float)):
                total_size += size

        # Step 5: Format sizes
        byte_val, kb, mb, gb, tb = format_size(total_size)

        # Step 6: Log and print results
        log_message = (
            f"Total item_size: {byte_val:.2f} bytes | "
            f"{kb:.2f} KB | {mb:.2f} MB | {gb:.2f} GB | {tb:.2f} TB"
        )
        print(log_message)
        logging.info(log_message)

        print("Processing completed successfully.")
        logging.info("Processing completed successfully.")

    except Exception as e:
        error_msg = f"Error occurred: {e}"
        print(error_msg)
        logging.error(error_msg)

if __name__ == '__main__':
    main()
