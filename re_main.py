import pandas as pd
import re
import json

# Function to extract status code from a log line containing JSON response
def extract_status_code(log_line):
    try:
        # Extract the JSON part of the log line using regex
        json_part = re.search(r'({.*})', log_line)
        if json_part:
            log_data = json.loads(json_part.group(1))
            # Check if StatusCode is in the log data
            if 'StatusCode' in log_data:
                return int(log_data['StatusCode'])
    except json.JSONDecodeError:
        pass
    return None

# Path to your log file
log_file_path = r'C:\Users\lenovo\logs_reader\HDFC_IDV_Failed_log_fuse.txt'

# Initialize a list to store failed logs
failed_logs = []

# Read the log file line by line
with open(log_file_path, 'r') as file:
    for line in file:
        # Extract the status code
        StatusCode = extract_status_code(line)
        # Append the failed log if the StatusCode is not 200
        if StatusCode is not None and StatusCode != 200:
            failed_logs.append(line.strip())

# Convert failed logs to a DataFrame
failed_logs_df = pd.DataFrame(failed_logs, columns=["Failed Logs"])

# Save the failed logs to a CSV file
output_file_path = 'C:/Users/lenovo/logs_reader/failed_logs.csv'
failed_logs_df.to_csv(output_file_path, index=False)

print(f"Extracted {len(failed_logs)} failed logs and saved to {output_file_path}")
