# Chat with Structured Data

A natural-language interface for querying tabular data via SQL, powered by Groq LLMs, Next.js, and PostgreSQL.

## Components

1. **Dataset & Schema**: A mock e-commerce dataset (`generate_data.py`) consisting of `customers`, `products`, and `orders` tables.
2. **ETL Pipeline**: (`etl.py`) Cleans the messy CSV data (handling nulls, fixing types, deduplication) and loads it into a normalized PostgreSQL database using SQLAlchemy.
3. **NL-to-SQL Engine**: (`nl2sql.py`) Takes natural language questions, uses Groq's LLM to generate PostgreSQL based on the schema, safely executes read-only queries, and handles errors with retry logic.
4. **Evaluation**: (`eval.py`) A test suite that runs predefined questions through the engine and verifies logic.
5. **Dashboard**: (`app.py` / `api.py` & `frontend/`) A Next.js web interface and FastAPI backend to interact with the data, displaying SQL queries, tables, and auto-generated charts.

## Screenshots

![Query Interface](images/screenshot_query_1790870282230.jpg)
![Query Results](images/screenshot_results_1790870367618.jpg)

## Database Schema (3NF)

- **Customers**: `customer_id` (PK), `name`, `email`, `registration_date`
- **Products**: `product_id` (PK), `name`, `category`, `price`
- **Orders**: `order_id` (PK), `customer_id` (FK), `product_id` (FK), `order_date`, `quantity`, `total_amount`

## Setup & Running Locally

1. Create a virtual environment and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your environment variables. You will need a Groq API Key, and a PostgreSQL database connection string. You can get a free managed PostgreSQL database in seconds from [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com).
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   export DATABASE_URL="postgresql://user:password@host/dbname"
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
5. Run the FastAPI backend:
   ```bash
   uvicorn api:app --reload
   ```
6. In a new terminal, launch the Next.js frontend:
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

## Running via Docker

You can easily containerize and run the entire application using Docker. The ETL process runs automatically during the Docker build (ensure you pass DATABASE_URL if ETL runs during build, or run ETL separately).

1. Build the image:
   ```bash
   docker build -t chat-with-data .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 -e GROQ_API_KEY="your-api-key-here" -e DATABASE_URL="postgresql://..." chat-with-data
   ```

## Sample Questions
Try these out in the dashboard:
- "How many customers registered in 2023?"
- "What is the total revenue generated from the Electronics category?"
- "Who are the top 5 customers by total amount spent?"
- "Show total sales grouped by product category."
