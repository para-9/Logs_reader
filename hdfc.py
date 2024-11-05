import pandas as pd
import re
import json

# Patterns to match full lines for requests and responses
request_pattern = re.compile(r"(.*Complete Request :\s*{.*})")
response_pattern = re.compile(r"(.*REST service response :\s*{.*})")

# Function to extract a specific JSON field (e.g., TransactionID or StatusCode) from a log line
def extract_json_field(log_line, field):
    try:
        # Extract JSON part within braces `{...}`
        json_part = re.search(r'({.*})', log_line)
        if json_part:
            log_data = json.loads(json_part.group(1))
            return log_data.get(field, None)
    except json.JSONDecodeError:
        pass
    return None

# Initialize lists for storing the failed requests and responses
failed_requests = []
failed_responses = []

# Path to the log file
log_file_path = r'C:\Users\lenovo\logs_reader\HDFC_IDV_Failed_log_fuse.txt'

# Read and process the log file
with open(log_file_path, 'r') as file:
    current_request_line = None
    current_transaction_id = None

    for line in file:
        # Capture full REST request line
        if request_match := request_pattern.match(line):
            current_request_line = request_match.group(1)  # Entire line as-is
            current_transaction_id = extract_json_field(current_request_line, "TransactionID")

        # Capture REST response line if StatusCode is not 200 and matches the request TransactionID
        elif response_match := response_pattern.match(line):
            response_line = response_match.group(1)  # Entire line as-is
            status_code = extract_json_field(response_line, "StatusCode")
            transaction_id = extract_json_field(response_line, "TransactionID")

            # Ensure response status is failed and matches the TransactionID of the request
            if status_code and status_code != 200 and current_transaction_id == transaction_id:
                failed_requests.append(current_request_line)
                failed_responses.append(response_line)

                # Reset after pairing
                current_request_line = None
                current_transaction_id = None

# Combine requests and responses, storing each in separate rows in the desired order
failed_logs_combined = []
for req, resp in zip(failed_requests, failed_responses):
    failed_logs_combined.append(["Failed REST Request", req])
    failed_logs_combined.append(["Failed REST Response", resp])

# Convert to DataFrame and save as CSV
failed_logs_df = pd.DataFrame(failed_logs_combined, columns=["Log Type", "Log Details"])
output_file_path = 'C:/Users/lenovo/logs_reader/failed_logs.csv'
failed_logs_df.to_csv(output_file_path, index=False)

print(f"Extracted {len(failed_requests)} failed REST requests and responses, saved to {output_file_path}")
