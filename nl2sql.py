import os
import sqlite3
import pandas as pd
from groq import Groq
import re

# Database Schema string for prompt
SCHEMA_INFO = """
Table: Customers
- customer_id (INTEGER PRIMARY KEY)
- name (TEXT)
- email (TEXT)
- registration_date (TEXT, YYYY-MM-DD)

Table: Products
- product_id (INTEGER PRIMARY KEY)
- name (TEXT)
- category (TEXT)
- price (REAL)

Table: Orders
- order_id (INTEGER PRIMARY KEY)
- customer_id (INTEGER, Foreign Key to Customers)
- product_id (INTEGER, Foreign Key to Products)
- order_date (TEXT, YYYY-MM-DD)
- quantity (INTEGER)
- total_amount (REAL)
"""

SYSTEM_PROMPT = f"""
You are an expert SQL assistant. Your task is to generate a SQLite query to answer the user's question based on the following schema:
{SCHEMA_INFO}

Rules:
1. ONLY return the SQL query. Do not include markdown formatting like ```sql or explanations.
2. The query must be a valid SQLite SELECT statement. Do not use INSERT, UPDATE, DELETE, DROP, etc.
3. If the question cannot be answered using the given schema, return "ERROR: Cannot answer based on schema."
"""

def extract_sql(llm_output: str) -> str:
    """Extracts SQL from LLM output, handling potential markdown."""
    llm_output = llm_output.strip()
    if llm_output.startswith("```sql"):
        llm_output = llm_output[6:]
    elif llm_output.startswith("```"):
        llm_output = llm_output[3:]
    
    if llm_output.endswith("```"):
        llm_output = llm_output[:-3]
        
    return llm_output.strip()

def is_safe_query(query: str) -> bool:
    """Simple check to reject non-SELECT statements."""
    query = query.strip().upper()
    if not query.startswith("SELECT"):
        return False
    # Check for dangerous keywords anywhere
    dangerous = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'REPLACE']
    for word in dangerous:
        if re.search(rf'\b{word}\b', query):
            return False
    return True

def ask_database(question: str, db_path: str = 'retail.db'):
    """
    Takes a natural language question, generates SQL via Groq, executes it, 
    and returns (sql_query, result_dataframe, error_message).
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    if not client.api_key:
        return None, None, "GROQ_API_KEY environment variable not set."

    model = "openai/gpt-oss-120b"

    def generate_sql(prompt_messages):
        response = client.chat.completions.create(
            messages=prompt_messages,
            model=model,
            temperature=0.0,
            max_tokens=500
        )
        return extract_sql(response.choices[0].message.content)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    # Try generating and running SQL
    try:
        sql = generate_sql(messages)
        
        if "ERROR:" in sql:
            return sql, None, sql
            
        if not is_safe_query(sql):
            return sql, None, "Unsafe query generated. Only SELECT is allowed."
            
        conn = sqlite3.connect(db_path)
        try:
            df = pd.read_sql_query(sql, conn)
            return sql, df, None
        except sqlite3.Error as e:
            # Retry logic: feed error back
            error_msg = str(e)
            messages.append({"role": "assistant", "content": sql})
            messages.append({"role": "user", "content": f"The query failed with error: {error_msg}. Please correct the SQL query and return ONLY the raw SQL."})
            
            # 2nd attempt
            sql_retry = generate_sql(messages)
            if not is_safe_query(sql_retry):
                return sql_retry, None, "Unsafe query generated on retry."
                
            df = pd.read_sql_query(sql_retry, conn)
            return sql_retry, df, None
            
        finally:
            conn.close()
            
    except Exception as e:
        return None, None, f"An unexpected error occurred: {str(e)}"
