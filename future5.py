import pandas as pd
import re

# Function to extract CarrierId and Error (both Failed Request and SOAP service response)
def extract_carrier_error(log_lines, processed_errors):
    try:
        # Join the multiline log into a single string for processing
        log_line = ''.join(log_lines)

        # Check if CarrierId exists in the log line  
        if "CarrierId" in log_line:
            print(f"Processing line: {log_line}")

            # Extract the CarrierId using regex
            carrier_id_match = re.search(r'CarrierId:(\d+)', log_line)
            if carrier_id_match:
                carrier_id = carrier_id_match.group(1)
                
                # Check if it's a Failed Request Error
                if "Complete Request" in log_line:
                    error_message = "Failed to complete request"
                    
                    # Ensure this error message is not duplicated
                    if carrier_id not in processed_errors or error_message not in processed_errors[carrier_id]:
                        # Add error to the processed errors dictionary
                        processed_errors.setdefault(carrier_id, []).append(error_message)
                        return carrier_id, error_message, log_line

                # Check if it's a SOAP response error and extract the Error field
                error_match = re.search(r'&lt;Error&gt;(.*?)&lt;/Error&gt;', log_line)
                if not error_match:  # Try with normal angle brackets
                    error_match = re.search(r'<Error>(.*?)</Error>', log_line)
                
                if error_match:
                    error_message = error_match.group(1).strip()
                    
                    # Ensure the error message is not duplicated and is not empty
                    if error_message and (carrier_id not in processed_errors or error_message not in processed_errors[carrier_id]):
                        # Add error to the processed errors dictionary
                        processed_errors.setdefault(carrier_id, []).append(error_message)
                        return carrier_id, error_message, log_line
    except Exception as e:
        print(f"Error processing log lines: {e}")
    
    # Return None if no relevant data found
    return None, None, None

# Path to your log file
log_file_path = r'C:\Users\lenovo\logs_reader\Future_Generali_Failed_Proposal_Log.log'

# Initialize a list to store failed logs where the error is not null
failed_logs = []

# Initialize a list to accumulate multiline logs
multi_line_log = []

# Dictionary to track errors already processed for each CarrierId
processed_errors = {}

# Read the log file line by line
with open(log_file_path, 'r') as file:
    for line in file:
        line = line.strip()  # Remove leading/trailing spaces

        # If the line starts a new log entry, process the accumulated log lines
        if "CarrierId" in line and multi_line_log:
            carrier_id, error_message, original_log = extract_carrier_error(multi_line_log, processed_errors)

            # Append the failed log if the error message is not null
            if error_message is not None:
                failed_logs.append({
                    "CarrierId": carrier_id,
                    "ErrorMessage": error_message,
                    "LogLine": original_log
                })
            # Reset the multiline log for the next log entry
            multi_line_log = []

        # Accumulate the current line into the multiline log
        multi_line_log.append(line)

    # Process the last accumulated log (if the log ends without starting a new one)
    if multi_line_log:
        carrier_id, error_message, original_log = extract_carrier_error(multi_line_log, processed_errors)
        if error_message is not None:
            failed_logs.append({
                "CarrierId": carrier_id,
                "ErrorMessage": error_message,
                "LogLine": original_log
            })

# Convert failed logs to a DataFrame
failed_logs_df = pd.DataFrame(failed_logs, columns=["CarrierId", "ErrorMessage", "LogLine"])

# Save the failed logs to a CSV file
output_file_path = 'C:/Users/lenovo/logs_reader/failed_soap_and_request_errors.csv'
failed_logs_df.to_csv(output_file_path, index=False)

print(f"Extracted {len(failed_logs)} failed logs and saved to {output_file_path}")