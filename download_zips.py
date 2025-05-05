import os
import json
import requests
import time
import random
import re
from urllib.parse import quote
import zipfile
from datetime import datetime

# Configuration
json_file_path = r"C:\TEST\advancedsearch.json"
base_file_path = r"C:\TEST\downloads"
log_file_path = os.path.join(base_file_path, "zips_download_log.txt")

def log_failure(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def download_zip(creator, identifier, date, group_index):
    try:
        url = f"https://archive.org/compress/{quote(identifier)}"

        # Subdirectory group: 0001, 0002, ...
        group_folder_name = f"{group_index:04d}"
        group_dir = os.path.join(base_file_path, group_folder_name)
        
        # Sanitize creator
        sanitized_creator = re.sub(r'[^A-Za-z0-9]', '_', creator)

        # Subdirectory under group: creator name
        save_dir = os.path.join(group_dir, sanitized_creator)
        os.makedirs(save_dir, exist_ok=True)

        # File name and full path
        file_name = f"{date}_{identifier}.zip"
        save_path = os.path.join(save_dir, file_name)

        print(f"Downloading from: {url}")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Saved to: {save_path}")

            # Validate the zip file
            if not zipfile.is_zipfile(save_path):
                print(f"Invalid ZIP file: {save_path}")
                log_failure(f"Invalid ZIP file (not a zip): {save_path}")
            else:
                with zipfile.ZipFile(save_path, 'r') as zf:
                    bad_file = zf.testzip()
                    if bad_file:
                        print(f"Corrupted file in zip: {bad_file}")
                        log_failure(f"Corrupted entry in ZIP file: {save_path} -> {bad_file}")
        else:
            raise Exception(f"Download failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {identifier}: {str(e)}")
        log_failure(f"Exception: {url} -> {str(e)}")

def process_json_file():
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Strip JSONP wrapper (e.g., callback({...}))
        start = raw_content.find('(') + 1
        end = raw_content.rfind(')')
        json_str = raw_content[start:end]

        data = json.loads(json_str)

        docs = data.get("response", {}).get("docs", [])
        for index, item in enumerate(docs):
            creator = item.get('creator')
            identifier = item.get('identifier')
            date = item.get('date')
            # Split at 'T' to remove time and timezone
            date = date.split('T')[0]
            # Replace dashes with underscores
            date = date.replace('-', '_')
            
            if creator and identifier:
                # Group index: (index // 1000) + 1 ? 1-based group numbering
                group_index = (index // 1000) + 1
                download_zip(creator, identifier, date, group_index)

                wait_time = random.randint(10, 30)
                print(f"Waiting {wait_time} seconds before next download...")
                time.sleep(wait_time)
            else:
                print(f"Skipping invalid entry: {item}")
    except Exception as e:
        print(f"Failed to read or parse JSONP: {str(e)}")
        log_failure(f"JSON parsing error: {str(e)}")

if __name__ == "__main__":
    process_json_file()
