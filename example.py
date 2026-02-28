import sqlite3
import uuid
from datetime import datetime, timedelta
import random


def main():
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

    -- Model Information table (prices are per million tokens)
    CREATE TABLE IF NOT EXISTS model_information (
        model_id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        model_id_str TEXT NOT NULL UNIQUE,
        model_name TEXT NOT NULL,
        input_price_per_mtok REAL NOT NULL,
        output_price_per_mtok REAL NOT NULL,
        cache_read_price_per_mtok REAL NOT NULL DEFAULT 0,
        supports_thinking INTEGER DEFAULT 0,
        price_effective_date DATE NOT NULL,
        is_current INTEGER DEFAULT 1
    );

    -- API Versions table
    CREATE TABLE IF NOT EXISTS api_versions (
        api_version_id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
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
        cached_input_token_count INTEGER NOT NULL DEFAULT 0,
        thinking_token_count INTEGER NOT NULL DEFAULT 0,
        tool_definition_count INTEGER NOT NULL DEFAULT 0,
        tool_call_count INTEGER NOT NULL DEFAULT 0,
        model_id INTEGER,
        api_version_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_key_id) REFERENCES request_keys(request_key_id),
        FOREIGN KEY (model_id) REFERENCES model_information(model_id),
        FOREIGN KEY (api_version_id) REFERENCES api_versions(api_version_id)
    );
    ''')

    # Insert sample API keys (one per provider)
    cursor.executemany(
        "INSERT INTO request_keys (key_name, key_value) VALUES (?, ?)",
        [("Anthropic Key", "sk-ant-abc123def456"),
         ("OpenAI Key", "sk-proj-ghi789jkl012")])

    # Insert model information (prices per million tokens)
    #
    # Cache read pricing:
    #   Anthropic: 0.1x base input price
    #   OpenAI:    0.5x base input price
    cursor.executemany(
        """INSERT INTO model_information
        (provider, model_id_str, model_name, input_price_per_mtok, output_price_per_mtok,
         cache_read_price_per_mtok, supports_thinking, price_effective_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [("Anthropic", "anthropic/claude-opus-4-6",   "Claude Opus 4.6",   5.00, 25.00, 0.50,  1, "2025-01-01"),
         ("Anthropic", "anthropic/claude-sonnet-4-6", "Claude Sonnet 4.6", 3.00, 15.00, 0.30,  1, "2025-01-01"),
         ("Anthropic", "anthropic/claude-haiku-4-5",  "Claude Haiku 4.5",  1.00,  5.00, 0.10,  1, "2025-01-01"),
         ("OpenAI",    "openai/gpt-4o",               "GPT-4o",            2.50, 10.00, 1.25,  0, "2025-01-01"),
         ("OpenAI",    "openai/gpt-4o-mini",           "GPT-4o-mini",       0.15,  0.60, 0.075, 0, "2025-01-01"),
         ("OpenAI",    "openai/o3",                    "o3",                2.00,  8.00, 1.00,  1, "2025-01-01")])

    # Insert API versions
    cursor.executemany(
        "INSERT INTO api_versions (provider, api_version, release_date) VALUES (?, ?, ?)",
        [("Anthropic", "2024-10-22", "2024-10-22"),
         ("Anthropic", "2025-01-01", "2025-01-01"),
         ("OpenAI",    "v1",         "2023-11-01")])

    # Simulate token tracking data for 2025
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    current_date = start_date

    # Model IDs: 1=Opus, 2=Sonnet, 3=Haiku, 4=GPT-4o, 5=GPT-4o-mini, 6=o3
    anthropic_models = [1, 2, 3]
    openai_models = [4, 5, 6]
    thinking_models = {1, 2, 3, 6}  # Claude models + o3 support thinking tokens

    anthropic_versions = [1, 2]
    openai_version = 3

    while current_date <= end_date:
        for _ in range(random.randint(50, 200)):
            request_id = str(uuid.uuid4())

            # Randomly pick a provider
            if random.random() < 0.5:
                request_key_id = 1  # Anthropic
                model_id = random.choice(anthropic_models)
                api_version_id = random.choice(anthropic_versions)
            else:
                request_key_id = 2  # OpenAI
                model_id = random.choice(openai_models)
                api_version_id = openai_version

            input_token_count = random.randint(100, 2000)
            output_token_count = random.randint(50, 1000)

            # ~30% of requests benefit from prompt caching
            cached_input_token_count = 0
            if random.random() < 0.3:
                cached_input_token_count = random.randint(50, input_token_count)

            # Thinking/reasoning tokens for supported models (~40% of their requests)
            thinking_token_count = 0
            if model_id in thinking_models and random.random() < 0.4:
                thinking_token_count = random.randint(200, 2000)

            # ~60% of requests use tool use (tool defs inflate input tokens,
            # tool results come back as input tokens on subsequent turns)
            tool_definition_count = 0
            tool_call_count = 0
            if random.random() < 0.6:
                tool_definition_count = random.randint(1, 15)
                tool_call_count = random.randint(1, min(tool_definition_count, 5))

            timestamp = current_date + timedelta(seconds=random.randint(0, 86399))

            cursor.execute('''
            INSERT INTO token_tracking
            (request_id, request_key_id, input_token_count, output_token_count,
             cached_input_token_count, thinking_token_count,
             tool_definition_count, tool_call_count,
             model_id, api_version_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (request_id, request_key_id, input_token_count, output_token_count,
                  cached_input_token_count, thinking_token_count,
                  tool_definition_count, tool_call_count,
                  model_id, api_version_id, timestamp))

        current_date += timedelta(days=1)

    conn.commit()

    # --- Queries (all costs computed from per-million-token prices) ---

    top_5_requests = '''
    SELECT tt.request_id, mi.model_id_str,
           tt.input_token_count, tt.output_token_count,
           tt.cached_input_token_count, tt.thinking_token_count,
           tt.timestamp,
           (tt.input_token_count * mi.input_price_per_mtok / 1e6
            + tt.output_token_count * mi.output_price_per_mtok / 1e6
            + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
            + tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as total_cost
    FROM token_tracking tt
    JOIN model_information mi ON tt.model_id = mi.model_id
    ORDER BY total_cost DESC
    LIMIT 5
    '''

    total_cost_per_model = '''
    SELECT mi.model_id_str,
           SUM(tt.input_token_count * mi.input_price_per_mtok / 1e6
               + tt.output_token_count * mi.output_price_per_mtok / 1e6
               + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
               + tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as total_cost
    FROM token_tracking tt
    JOIN model_information mi ON tt.model_id = mi.model_id
    GROUP BY mi.model_id_str
    ORDER BY total_cost DESC
    '''

    total_cost_by_key = '''
    SELECT rk.key_name,
           SUM(tt.input_token_count * mi.input_price_per_mtok / 1e6
               + tt.output_token_count * mi.output_price_per_mtok / 1e6
               + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
               + tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as total_cost
    FROM token_tracking tt
    JOIN request_keys rk ON tt.request_key_id = rk.request_key_id
    JOIN model_information mi ON tt.model_id = mi.model_id
    GROUP BY rk.key_name
    ORDER BY total_cost DESC
    '''

    monthly_cost_by_key = '''
    SELECT rk.key_name,
           strftime('%Y-%m', tt.timestamp) as month,
           SUM(tt.input_token_count * mi.input_price_per_mtok / 1e6
               + tt.output_token_count * mi.output_price_per_mtok / 1e6
               + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
               + tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as monthly_cost
    FROM token_tracking tt
    JOIN request_keys rk ON tt.request_key_id = rk.request_key_id
    JOIN model_information mi ON tt.model_id = mi.model_id
    GROUP BY rk.key_name, month
    ORDER BY rk.key_name, month
    '''

    monthly_cost_for_all_keys = '''
    SELECT strftime('%Y-%m', tt.timestamp) as month,
           SUM(tt.input_token_count * mi.input_price_per_mtok / 1e6
               + tt.output_token_count * mi.output_price_per_mtok / 1e6
               + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
               + tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as total_monthly_cost
    FROM token_tracking tt
    JOIN model_information mi ON tt.model_id = mi.model_id
    GROUP BY month
    ORDER BY month
    '''

    monthly_usage_per_model_per_key = '''
    SELECT rk.key_name, mi.model_id_str,
           strftime('%Y-%m', tt.timestamp) as month,
           SUM(tt.input_token_count * mi.input_price_per_mtok / 1e6
               + tt.output_token_count * mi.output_price_per_mtok / 1e6
               + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
               + tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as monthly_cost
    FROM token_tracking tt
    JOIN request_keys rk ON tt.request_key_id = rk.request_key_id
    JOIN model_information mi ON tt.model_id = mi.model_id
    GROUP BY rk.key_name, mi.model_id_str, month
    ORDER BY rk.key_name, mi.model_id_str, month
    '''

    cache_savings = '''
    SELECT mi.model_id_str,
           SUM(tt.cached_input_token_count) as total_cached_tokens,
           SUM(tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6) as cache_cost,
           SUM(tt.cached_input_token_count * mi.input_price_per_mtok / 1e6) as would_have_cost,
           SUM(tt.cached_input_token_count * (mi.input_price_per_mtok - mi.cache_read_price_per_mtok) / 1e6) as savings
    FROM token_tracking tt
    JOIN model_information mi ON tt.model_id = mi.model_id
    WHERE tt.cached_input_token_count > 0
    GROUP BY mi.model_id_str
    ORDER BY savings DESC
    '''

    thinking_costs = '''
    SELECT mi.model_id_str,
           SUM(tt.thinking_token_count) as total_thinking_tokens,
           SUM(tt.thinking_token_count * mi.output_price_per_mtok / 1e6) as thinking_cost,
           SUM(tt.output_token_count * mi.output_price_per_mtok / 1e6) as output_cost
    FROM token_tracking tt
    JOIN model_information mi ON tt.model_id = mi.model_id
    WHERE tt.thinking_token_count > 0
    GROUP BY mi.model_id_str
    ORDER BY thinking_cost DESC
    '''

    tool_use_analysis = '''
    SELECT mi.model_id_str,
           COUNT(*) as total_requests,
           SUM(CASE WHEN tt.tool_call_count > 0 THEN 1 ELSE 0 END) as tool_use_requests,
           ROUND(100.0 * SUM(CASE WHEN tt.tool_call_count > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) as tool_use_pct,
           ROUND(AVG(CASE WHEN tt.tool_call_count > 0 THEN tt.tool_definition_count END), 1) as avg_tools_defined,
           ROUND(AVG(CASE WHEN tt.tool_call_count > 0 THEN tt.tool_call_count END), 1) as avg_tool_calls,
           ROUND(AVG(CASE WHEN tt.tool_call_count > 0
                      THEN tt.input_token_count * mi.input_price_per_mtok / 1e6
                           + tt.output_token_count * mi.output_price_per_mtok / 1e6
                           + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
                           + tt.thinking_token_count * mi.output_price_per_mtok / 1e6
                      END), 6) as avg_cost_with_tools,
           ROUND(AVG(CASE WHEN tt.tool_call_count = 0
                      THEN tt.input_token_count * mi.input_price_per_mtok / 1e6
                           + tt.output_token_count * mi.output_price_per_mtok / 1e6
                           + tt.cached_input_token_count * mi.cache_read_price_per_mtok / 1e6
                           + tt.thinking_token_count * mi.output_price_per_mtok / 1e6
                      END), 6) as avg_cost_without_tools
    FROM token_tracking tt
    JOIN model_information mi ON tt.model_id = mi.model_id
    GROUP BY mi.model_id_str
    ORDER BY mi.model_id_str
    '''

    queries = [
        ("Top 5 Most Expensive Invocations", top_5_requests),
        ("Total Cost Per Model", total_cost_per_model),
        ("Total Cost by API Key", total_cost_by_key),
        ("Monthly Cost by API Key", monthly_cost_by_key),
        ("Total Monthly Cost Across All Keys", monthly_cost_for_all_keys),
        ("Monthly Cost Breakdown by Model for Each API Key", monthly_usage_per_model_per_key),
        ("Cache Savings by Model", cache_savings),
        ("Thinking Token Costs by Model", thinking_costs),
        ("Tool Use Analysis by Model", tool_use_analysis),
    ]

    for title, query in queries:
        print(f"\n{title}:")
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            print(row)

    conn.close()


if __name__ == "__main__":
    main()
