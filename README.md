# AI Cost Tracking System

This repository contains a simple yet powerful AI cost tracking system designed to help you monitor and analyze the costs associated with using various AI models through API calls. The system includes a database schema, a Python simulation script, and SQL queries for cost analysis.

## Table of Contents

- [AI Cost Tracking System](#ai-cost-tracking-system)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
  - [Database Schema](#database-schema)
  - [Simulation Script](#simulation-script)
  - [Cost Analysis Queries](#cost-analysis-queries)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- Track token usage and costs for multiple AI models
- Manage multiple API keys
- Monitor costs across different API versions
- Generate simulated data for testing and development
- Analyze costs by API key, model, and time period

## Getting Started

To get started with this AI cost tracking system:

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

- `request_keys`: Stores information about API keys
- `model_information`: Contains details about AI models and their pricing
- `api_versions`: Tracks different API versions
- `token_tracking`: The main table for recording token usage and costs

## Simulation Script

The `example.py` file generates a year's worth of simulated data. It creates a SQLite database, populates it with sample data, and runs example queries. You can modify this script to generate different patterns of data or adapt it to work with other database systems.

To run the simulation:

```
python example.py
```

## Cost Analysis Queries

The repository includes several SQL queries for analyzing costs:

1. Total cost by API key
2. Monthly cost by API key
3. Total monthly cost across all keys
4. Monthly cost breakdown by model for each API key
5. Top 5 requests by cost
6. Total cost per model

## Contributing

Contributions to improve the AI cost tracking system are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request with a clear description of your changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.