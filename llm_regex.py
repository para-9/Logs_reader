import os
import re
import json
import csv
import time
import google.generativeai as genai
from dotenv import load_dotenv
import google.api_core.exceptions

# Load environment variables for API key
load_dotenv()

# Configure Google Generative AI (Gemini Pro) with the API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get a structured response from LLM (Gemini Pro) to analyze logs
def get_llm_analysis(log_line):
    input_prompt = f"""
    Analyze the following log line from a REST API server log and determine if it indicates a failed API call.
    If it's a failed API call, extract the relevant information such as:
    - Endpoint or URL
    - Status Code
    - Error Message (if any)
    - Timestamp (if available)
    - Any other important details

    Log Line:
    {log_line}

    Respond with a structured JSON object indicating whether it's a failed log or not.
    """
    
    model = genai.GenerativeModel('gemini-pro')
    retries = 3  # Number of retries
    delay = 10   # Delay in seconds between retries
    
    for attempt in range(retries):
        try:
            response = model.generate_content(input_prompt)
            return response.text  # Return the successful response
        except google.api_core.exceptions.ResourceExhausted:
            print(f"Quota exceeded. Attempt {attempt + 1} of {retries}. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit on other types of exceptions
    
    print("Max retries exceeded or quota exhausted. Skipping LLM analysis.")
    return "{}"  # Return empty JSON if quota is exhausted

# Fallback function using regex to detect failed logs
def regex_fallback_analysis(log_line):
    # Define a regex pattern to detect failed REST API logs (e.g., status codes 4xx or 5xx)
    pattern = r"status code\s*=\s*(\d+)"
    match = re.search(pattern, log_line)

    if match:
        status_code = int(match.group(1))
        if status_code >= 400:
            return True  # It's a failed log
    return False  # Log is not failed or no status code detected

# Function to extract failed logs (status code other than 200) from log or text files using LLM
def extract_failed_logs_using_llm(file_path):
    failed_logs = []
    
    with open(file_path, "r") as log_file:
        for line in log_file:
            # First, try LLM to analyze the log
            llm_response = get_llm_analysis(line)
            
            # Try to parse the LLM response as JSON to see if it's a failed log
            try:
                log_info = json.loads(llm_response)
                if log_info.get("is_failed_log"):  # LLM indicates it's a failed log
                    failed_logs.append(line.strip())  # Append the original log line
            except json.JSONDecodeError:
                # If LLM analysis fails, use regex fallback
                print(f"LLM failed to analyze, falling back to regex for log line: {line}")
                if regex_fallback_analysis(line):
                    failed_logs.append(line.strip())  # Append the original log line
    
    return failed_logs

# Function to save extracted failed logs to a CSV file
def save_logs_to_csv(failed_logs, output_file):
    with open(output_file, "w", newline="") as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow(["Failed Log"])  # Header for CSV
        for log in failed_logs:
            log_writer.writerow([log])

# Main function to process log files and extract failed API responses using LLM
def process_log_files(file_path, output_csv):
    failed_logs = extract_failed_logs_using_llm(file_path)

    # Save all failed logs to a CSV file
    if failed_logs:
        save_logs_to_csv(failed_logs, output_csv)
        print(f"Failed logs have been saved to {output_csv}")
    else:
        print("No failed logs found.")

# Example usage
if __name__ == "__main__":
    input_file = r"C:\Users\lenovo\logs_reader\HDFC_IDV_Failed_log_fuse.txt"  # Path to the single log file
    output_csv = r"C:\Users\lenovo\logs_reader\failed_logs.csv"  # Output CSV file for failed logs

    # Process the single log file and extract failed logs into a CSV file
    process_log_files(input_file, output_csv)
