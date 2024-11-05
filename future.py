import csv
import re

# Initialize storage for failed SOAP service requests and responses
failed_soap_requests = []
failed_soap_responses = []

# Regular expressions to match requests and failed responses
request_pattern_start = re.compile(r".*Complete Request for CarrierId:\d+, ProductId:\d+.*<SOAP-ENV:Envelope.*")
request_pattern_end = re.compile(r".*</SOAP-ENV:Envelope>")
failed_response_pattern = re.compile(r".*SOAP service response for CarrierId:\d+, ProductId:\d+.*<s:Envelope.*(Fail|Error).*")

# Read the file once
with open('Future_Generali_Failed_Proposal_Log.log') as f:
    lines = f.readlines()

# Variables to keep track of the current failed request-response pair
current_failed_request = None
capturing_request = False
multiline_request = []

# Process each line
for line in lines:
    # Identify the start of a potential failed SOAP service request
    if request_pattern_start.match(line):
        capturing_request = True
        multiline_request = [line.strip()]  # Start storing the lines of the request

    # Continue capturing lines if within a multiline SOAP request
    elif capturing_request:
        multiline_request.append(line.strip())
        if request_pattern_end.search(line):  # End of SOAP request
            current_failed_request = " ".join(multiline_request)  # Concatenate all lines into one string
            capturing_request = False  # Reset capturing status

    # Check if the line is a failed SOAP service response associated with the request
    elif failed_response_pattern.match(line) and current_failed_request:
        # Capture the response line if it includes "Fail" or "Error"
        current_failed_response = line.strip()
        failed_soap_requests.append(current_failed_request)
        failed_soap_responses.append(current_failed_response)
        
        # Reset the request variable after pairing with the response
        current_failed_request = None

# Write results to a CSV file, with separate rows for requests and responses
with open('Failed_Proposal_Log_Output.csv', mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write header
    writer.writerow(["Log Type", "Log Details"])
    
    # Write each failed request-response pair to the CSV in separate rows
    for req, resp in zip(failed_soap_requests, failed_soap_responses):
        writer.writerow(["Failed SOAP Service Request", req])
        writer.writerow(["Failed SOAP Service Response", resp])

# Notify of completion
print("Log processing complete. Check 'Failed_Proposal_Log_Output.csv' for failed requests and responses.")
