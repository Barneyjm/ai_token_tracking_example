import sqlite3
import uuid
from datetime import datetime, timedelta
import random

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('ai_cost_tracking.db')
cursor = conn.cursor()

# Create tables
cursor.executescript('''
-- Request Keys table
CREATE TABLE IF NOT EXISTS request_keys (
    request_key_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL UNIQUE,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Information table
CREATE TABLE IF NOT EXISTS model_information (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_input_price REAL NOT NULL,
    model_output_price REAL NOT NULL,
    price_effective_date DATE NOT NULL,
    is_current INTEGER DEFAULT 1
);

-- API Versions table
CREATE TABLE IF NOT EXISTS api_versions (
    api_version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_version TEXT NOT NULL,
    release_date DATE NOT NULL
);

-- Token Tracking table
CREATE TABLE IF NOT EXISTS token_tracking (
    tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT NOT NULL,
    request_key_id INTEGER,
    input_token_count INTEGER NOT NULL,
    output_token_count INTEGER NOT NULL,
    model_id INTEGER,
    api_version_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_key_id) REFERENCES request_keys(request_key_id),
    FOREIGN KEY (model_id) REFERENCES model_information(model_id),
    FOREIGN KEY (api_version_id) REFERENCES api_versions(api_version_id)
);
''')

# Insert sample data
cursor.executemany("INSERT INTO request_keys (key_name, key_value) VALUES (?, ?)",
                   [("API Key 1", "sk-abcdef123456"),
                    ("API Key 2", "sk-ghijkl789012")])

cursor.executemany("INSERT INTO model_information (model_name, model_input_price, model_output_price, price_effective_date) VALUES (?, ?, ?, ?)",
                   [("GPT-3.5-Turbo", 0.0015, 0.002, "2023-01-01"),
                    ("GPT-4", 0.03, 0.06, "2023-01-01")])

cursor.executemany("INSERT INTO api_versions (api_version, release_date) VALUES (?, ?)",
                   [("v1", "2023-01-01"),
                    ("v2", "2023-06-01")])

# Simulate token tracking data
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
current_date = start_date

while current_date <= end_date:
    for _ in range(random.randint(50, 200)):  # Random number of requests per day
        request_id = str(uuid.uuid4())
        request_key_id = random.randint(1, 2)
        input_token_count = random.randint(100, 1000)
        output_token_count = random.randint(50, 500)
        model_id = random.randint(1, 2)
        api_version_id = random.randint(1, 2)
        timestamp = current_date + timedelta(seconds=random.randint(0, 86399))

        cursor.execute('''
        INSERT INTO token_tracking
        (request_id, request_key_id, input_token_count, output_token_count, model_id, api_version_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (request_id, request_key_id, input_token_count, output_token_count, model_id, api_version_id, timestamp))

    current_date += timedelta(days=1)

conn.commit()

# Example queries
top_5_requests = '''
SELECT tt.request_id, tt.input_token_count, tt.output_token_count, 
       mi.model_name, tt.timestamp,
       (tt.input_token_count * mi.model_input_price / 1000.0 + 
        tt.output_token_count * mi.model_output_price / 1000.0) as total_cost
FROM token_tracking tt
JOIN model_information mi ON tt.model_id = mi.model_id
ORDER BY total_cost DESC
LIMIT 5
'''

total_cost_per_model = '''
SELECT mi.model_name, 
       SUM(tt.input_token_count * mi.model_input_price / 1000.0 + 
           tt.output_token_count * mi.model_output_price / 1000.0) as total_cost
FROM token_tracking tt
JOIN model_information mi ON tt.model_id = mi.model_id
GROUP BY mi.model_name
'''

total_cost_by_key = '''
SELECT 
    rk.key_name,
    SUM(tt.input_token_count * mi.model_input_price / 1000.0 + 
        tt.output_token_count * mi.model_output_price / 1000.0) as total_cost
FROM token_tracking tt
JOIN request_keys rk ON tt.request_key_id = rk.request_key_id
JOIN model_information mi ON tt.model_id = mi.model_id
GROUP BY rk.key_name
ORDER BY total_cost DESC;'''

monthly_cost_by_key = '''
SELECT 
    rk.key_name,
    strftime('%Y-%m', tt.timestamp) as month,
    SUM(tt.input_token_count * mi.model_input_price / 1000.0 + 
        tt.output_token_count * mi.model_output_price / 1000.0) as monthly_cost
FROM token_tracking tt
JOIN request_keys rk ON tt.request_key_id = rk.request_key_id
JOIN model_information mi ON tt.model_id = mi.model_id
GROUP BY rk.key_name, month
ORDER BY rk.key_name, month;'''

monthly_cost_for_all_keys = '''
SELECT 
    strftime('%Y-%m', tt.timestamp) as month,
    SUM(tt.input_token_count * mi.model_input_price / 1000.0 + 
        tt.output_token_count * mi.model_output_price / 1000.0) as total_monthly_cost
FROM token_tracking tt
JOIN model_information mi ON tt.model_id = mi.model_id
GROUP BY month
ORDER BY month;'''

montly_usage_per_model_per_key = '''
SELECT 
    rk.key_name,
    mi.model_name,
    strftime('%Y-%m', tt.timestamp) as month,
    SUM(tt.input_token_count * mi.model_input_price / 1000.0 + 
        tt.output_token_count * mi.model_output_price / 1000.0) as monthly_cost
FROM token_tracking tt
JOIN request_keys rk ON tt.request_key_id = rk.request_key_id
JOIN model_information mi ON tt.model_id = mi.model_id
GROUP BY rk.key_name, mi.model_name, month
ORDER BY rk.key_name, mi.model_name, month;'''

queries = [
    ("Top 5 Most Expensive Invocations", top_5_requests),
    ("Total Cost Per Model", total_cost_per_model),
    ("Total cost by API key", total_cost_by_key),
    ("Monthly cost by API key", monthly_cost_by_key),
    ("Total monthly cost across all keys", monthly_cost_for_all_keys),
    ("Monthly cost breakdown by model for each API key", montly_usage_per_model_per_key)
]

for title, query in queries:
    print(f"\n{title}:")
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(row)

# Close the connection
conn.close()
