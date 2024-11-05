import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# 1. Load and preprocess log data
def parse_log_file(log_file):
    pattern = r'(?P<timestamp>\S+ \S+) - (?P<endpoint>\S+) - (?P<status_code>\d+) - (?P<message>.+) - (?P<duration>\d+ms)'
    log_entries = []

    with open(log_file, 'r') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                log_entries.append(match.groupdict())

    return pd.DataFrame(log_entries)

log_data = parse_log_file('api_logs.txt')


# Convert duration to numerical
log_data['duration'] = log_data['duration'].str.replace('ms', '').astype(int)
log_data['status_code'] = log_data['status_code'].astype(int)

# Labeling: 1 = Failed, 0 = Success
log_data['label'] = log_data['status_code'].apply(lambda x: 1 if x >= 400 else 0)

# 2. Feature selection
X = log_data[['status_code', 'duration']]  # Add more features as needed
y = log_data['label']

# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Model training
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 5. Prediction
y_pred = model.predict(X_test)

# 6. Evaluation
print(classification_report(y_test, y_pred))

# 7. Save failed requests
log_data['prediction'] = model.predict(X)
failed_requests = log_data[log_data['prediction'] == 1]
failed_requests.to_csv('failed_requests.csv', index=False)
