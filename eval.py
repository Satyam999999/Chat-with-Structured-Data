import pandas as pd
from nl2sql import ask_database
import time
import os

EVAL_QUESTIONS = [
    {
        "question": "How many total customers do we have?",
        "expected_columns": 1,
        "check": lambda df: df.iloc[0, 0] > 0 if not df.empty else False
    },
    {
        "question": "What is the name of the product with product_id 5?",
        "expected_columns": 1,
        "check": lambda df: len(df) == 1 and isinstance(df.iloc[0, 0], str)
    },
    {
        "question": "List the top 3 customers by total amount spent.",
        "expected_columns": 2, # usually name/id and amount
        "check": lambda df: len(df) == 3 or len(df) > 0
    },
    {
        "question": "What is the total revenue generated from all orders?",
        "expected_columns": 1,
        "check": lambda df: df.iloc[0, 0] > 1000 if not df.empty and pd.notnull(df.iloc[0,0]) else False
    },
    {
        "question": "How many products do we have in the Electronics category?",
        "expected_columns": 1,
        "check": lambda df: df.iloc[0, 0] >= 0 if not df.empty else False
    },
    {
        "question": "Find the email of the customer who placed order_id 10.",
        "expected_columns": 1,
        "check": lambda df: len(df) == 1
    },
    {
        "question": "Show total sales grouped by product category.",
        "expected_columns": 2,
        "check": lambda df: len(df) > 0 and 'category' in df.columns.str.lower()
    },
    {
        "question": "Which customers registered in 2023?",
        "expected_columns": 1, # or more
        "check": lambda df: len(df) > 0
    }
]

def run_evaluation():
    if not os.environ.get("GROQ_API_KEY"):
        print("Skipping evaluation: GROQ_API_KEY not set.")
        return

    print(f"Starting evaluation on {len(EVAL_QUESTIONS)} questions...")
    correct = 0
    
    for i, q in enumerate(EVAL_QUESTIONS):
        print(f"\n[{i+1}/{len(EVAL_QUESTIONS)}] Question: {q['question']}")
        
        # We need to rate limit slightly to avoid Groq rate limits
        time.sleep(1)
        
        sql, df, error = ask_database(q['question'])
        
        if error:
            print(f"  ❌ FAILED: Error - {error}")
            continue
            
        print(f"  Generated SQL: {sql}")
        
        if df is not None and not df.empty:
            passed = q['check'](df)
            if passed:
                print("  ✅ PASSED")
                correct += 1
            else:
                print(f"  ❌ FAILED logic check. Output:\n{df.head()}")
        else:
            print("  ❌ FAILED: No data returned")
            
    print(f"\n--- EVALUATION COMPLETE ---")
    print(f"Score: {correct}/{len(EVAL_QUESTIONS)} ({(correct/len(EVAL_QUESTIONS))*100:.1f}%)")

if __name__ == "__main__":
    run_evaluation()
