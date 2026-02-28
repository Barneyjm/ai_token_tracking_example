# AI Cost Tracking System

A Python-based AI cost tracking system for monitoring and analyzing token usage and costs across multiple providers (Anthropic, OpenAI). Includes a database schema, simulation script, and SQL queries for cost analysis.

## Features

- **Multi-provider support** — track costs across Anthropic (Claude) and OpenAI (GPT, o-series) models
- **Modern token tracking** — input, output, cached input, thinking/reasoning, and tool use metadata
- **Prompt caching analysis** — measure savings from cached input tokens
- **Thinking token costs** — track extended thinking / reasoning token spend separately
- **Per-million-token pricing** — aligned with current industry-standard pricing units
- **Tool use analysis** — track tool definitions and calls per request, compare costs with/without tools
- **Cost analysis queries** — pre-built SQL for slicing costs by key, model, month, and more

## Getting Started

1. Clone this repository:
   ```
   git clone https://github.com/Barneyjm/ai_token_tracking_example.git
   cd ai_token_tracking_example
   ```

2. Ensure you have Python 3.x installed on your system.

3. Run the simulation script to create and populate the database:
   ```
   python example.py
   ```

4. Use the provided SQL queries or write your own to analyze the data.

## Database Schema

The system uses a SQLite database with the following tables:

- **`request_keys`** — API keys (one per provider in the sample data)
- **`model_information`** — Models with `provider/model-name` identifiers and per-million-token pricing (input, output, cache read)
- **`api_versions`** — API versions by provider
- **`token_tracking`** — Per-request token usage: input, output, cached input, thinking tokens, plus tool use metadata (definitions count, call count)

## Models Included

| Model ID                        | Display Name      | Input (per MTok) | Output (per MTok) | Cache Read (per MTok) |
|---------------------------------|-------------------|------------------:|-------------------:|----------------------:|
| `anthropic/claude-opus-4-6`     | Claude Opus 4.6   |            $5.00  |            $25.00  |                $0.50  |
| `anthropic/claude-sonnet-4-6`   | Claude Sonnet 4.6 |            $3.00  |            $15.00  |                $0.30  |
| `anthropic/claude-haiku-4-5`    | Claude Haiku 4.5  |            $1.00  |             $5.00  |                $0.10  |
| `openai/gpt-4o`                 | GPT-4o            |            $2.50  |            $10.00  |                $1.25  |
| `openai/gpt-4o-mini`            | GPT-4o-mini       |            $0.15  |             $0.60  |               $0.075  |
| `openai/o3`                     | o3                |            $2.00  |             $8.00  |                $1.00  |

## Simulation Script

The `example.py` script generates a year of simulated multi-provider data (2025). It creates a SQLite database, populates it with sample models and API keys, and runs example queries. You can modify it to generate different patterns or adapt it for other database systems.

```
python example.py
```

## Cost Analysis Queries

The repository includes 9 pre-built queries:

1. **Top 5 most expensive invocations** — highest-cost individual requests
2. **Total cost per model** — aggregate cost breakdown by provider and model
3. **Total cost by API key** — costs grouped by authentication key
4. **Monthly cost by API key** — time-series cost tracking per key
5. **Total monthly cost across all keys** — organization-wide monthly spending
6. **Monthly cost breakdown by model for each API key** — detailed 3-way breakdown
7. **Cache savings by model** — how much prompt caching saved vs. full-price input
8. **Thinking token costs by model** — extended thinking / reasoning token spend
9. **Tool use analysis by model** — % of requests using tools, avg tools defined/called, cost comparison with vs. without tools

## Contributing

Contributions are welcome! Please fork the repository, create a branch, and submit a pull request.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
