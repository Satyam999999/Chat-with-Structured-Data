import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_messy_data():
    print("Generating mock messy data...")
    
    # 1. Customers
    np.random.seed(42)
    customer_ids = range(1, 101)
    customers = pd.DataFrame({
        'customer_id': customer_ids,
        'name': [f"Customer_{i}" for i in customer_ids],
        'email': [f"customer{i}@example.com" if random.random() > 0.1 else None for i in customer_ids], # 10% missing emails
        'registration_date': [(datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d') for _ in customer_ids]
    })
    
    # Introduce messy duplicates
    customers = pd.concat([customers, customers.sample(5)]).sample(frac=1).reset_index(drop=True)
    
    customers.to_csv('data/customers.csv', index=False)
    print("Created data/customers.csv")

    # 2. Products
    products = pd.DataFrame({
        'product_id': range(1, 21),
        'name': [f"Product_{i}" for i in range(1, 21)],
        'category': random.choices(['Electronics', 'Clothing', 'Home', 'Toys'], k=20),
        'price': [str(round(random.uniform(10.0, 500.0), 2)) + ("" if random.random() > 0.1 else " USD") for _ in range(20)] # Some strings with " USD"
    })
    
    products.to_csv('data/products.csv', index=False)
    print("Created data/products.csv")

    # 3. Orders
    order_ids = range(1, 501)
    orders = pd.DataFrame({
        'order_id': order_ids,
        'customer_id': random.choices(customer_ids, k=500),
        'product_id': random.choices(range(1, 21), k=500),
        'order_date': [(datetime(2023, 6, 1) + timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d') for _ in order_ids],
        'quantity': random.choices([1, 2, 3, 4, 5, None], weights=[50, 30, 10, 5, 2, 3], k=500), # Some missing quantities
    })
    
    # We won't include total_amount, we'll let it be computed or just leave it for SQL to calculate, wait the prompt says to have total_amount.
    # Let's add it, but make some of them missing or incorrect so ETL can fix it if needed, or just standard.
    # We will just add it by joining product price, but let's make it messy.
    prices = products.set_index('product_id')['price'].str.replace(' USD', '').astype(float).to_dict()
    orders['total_amount'] = orders.apply(
        lambda row: round(prices[row['product_id']] * row['quantity'], 2) if pd.notnull(row['quantity']) else None, 
        axis=1
    )
    
    orders.to_csv('data/orders.csv', index=False)
    print("Created data/orders.csv")

if __name__ == "__main__":
    generate_messy_data()
