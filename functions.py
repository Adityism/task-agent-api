import re
import time
from fuzzywuzzy import fuzz
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import json

# Load environment variables
print("Loading .env file...")
load_dotenv()
if not os.getenv('AIPROXY_TOKEN'):
    print("Error: AIPROXY_TOKEN not found in .env file")

def get_task_output(task):
    max_retries = 3
    retry_delay = 2  # seconds
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    print(f"Using AIPROXY_TOKEN: {os.getenv('AIPROXY_TOKEN')}")  # Debug token loading
    token = os.getenv('AIPROXY_TOKEN')
    if not token:
        print("Error: AIPROXY_TOKEN not found in environment variables")
        return "Error: Missing API token"
        
    print(f"Using token: {token[:10]}...")  # Show first 10 chars for security
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": task}]
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            if "quota" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return f"Error processing task: {str(e)}"

def count_days(dayname: str):
    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    dayvalue = -1
    day = None
    
    for d in days:
        if d in dayname.lower():
            dayvalue = days[d]
            day = d
            break
    
    try:
        with open("data/dates.txt", "r") as file:
            data = file.readlines()
            count = sum([1 for line in data if datetime.strptime(line.strip(), "%Y-%m-%d").weekday() == dayvalue])
            with open(f"data/{day}-count", "w") as f:
                f.write(str(count))
    except Exception as e:
        return f"Error counting days: {str(e)}"

def extract_dayname(task: str):
    match = re.search(r'count\s+(\w+)', task)
    if match:
        return match.group(1)
    return ""

def extract_package(task: str):
    match = re.search(r'install\s+(\w+)', task)
    if match:
        return match.group(1)
    return ""

def get_correct_pkgname(pkgname: str):
    with open("packages.txt", "r", encoding="utf-8") as file:
        data = file.read().strip()
        packages = [line.strip() for line in data.split(" ")]
        corrects = []
        for pkg in packages:
            if fuzz.ratio(pkgname, pkg) >= 90:
                corrects.append(pkg)
        if corrects:
            return corrects[-1]
        return ""
