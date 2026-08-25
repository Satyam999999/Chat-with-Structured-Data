# Chat with Structured Data

A natural-language interface for querying tabular data via SQL, powered by Groq LLMs and Streamlit.

## Components

1. **Dataset & Schema**: A mock e-commerce dataset (`generate_data.py`) consisting of `Customers`, `Products`, and `Orders` tables.
2. **ETL Pipeline**: (`etl.py`) Cleans the messy CSV data (handling nulls, fixing types, deduplication) and loads it into a normalized SQLite database (`retail.db`).
3. **NL-to-SQL Engine**: (`nl2sql.py`) Takes natural language questions, uses Groq's LLM to generate SQL based on the schema, safely executes read-only queries, and handles errors with retry logic.
4. **Evaluation**: (`eval.py`) A test suite that runs predefined questions through the engine and verifies logic.
5. **Dashboard**: (`app.py`) A Streamlit web interface to interact with the data, displaying SQL queries, tables, and auto-generated charts.

## Database Schema (3NF)

- **Customers**: `customer_id` (PK), `name`, `email`, `registration_date`
- **Products**: `product_id` (PK), `name`, `category`, `price`
- **Orders**: `order_id` (PK), `customer_id` (FK), `product_id` (FK), `order_date`, `quantity`, `total_amount`

## Setup & Running Locally

1. Create a virtual environment and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your Groq API Key (or input it directly in the Streamlit sidebar later):
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```
3. Generate the data and run the ETL pipeline:
   ```bash
   python generate_data.py
   python etl.py
   ```
4. (Optional) Run the evaluation script:
   ```bash
   python eval.py
   ```
5. Launch the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

## Running via Docker

You can easily containerize and run the entire application using Docker. The ETL process runs automatically during the Docker build.

1. Build the image:
   ```bash
   docker build -t chat-with-data .
   ```
2. Run the container:
   ```bash
   docker run -p 8501:8501 -e GROQ_API_KEY="your-api-key-here" chat-with-data
   ```
3. Open `http://localhost:8501` in your browser.

## Sample Questions
Try these out in the dashboard:
- "How many customers registered in 2023?"
- "What is the total revenue generated from the Electronics category?"
- "Who are the top 5 customers by total amount spent?"
- "Show total sales grouped by product category."
