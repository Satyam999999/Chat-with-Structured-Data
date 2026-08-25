import pandas as pd
import sqlite3
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl.log"),
        logging.StreamHandler()
    ]
)

def run_etl():
    logging.info("Starting ETL process...")
    
    # Extract
    try:
        customers = pd.read_csv('customers.csv')
        products = pd.read_csv('products.csv')
        orders = pd.read_csv('orders.csv')
    except Exception as e:
        logging.error(f"Failed to load CSVs: {e}")
        return

    logging.info(f"Loaded Customers: {len(customers)} rows")
    logging.info(f"Loaded Products: {len(products)} rows")
    logging.info(f"Loaded Orders: {len(orders)} rows")

    # Transform - Customers
    # Drop exact duplicates
    cust_pre = len(customers)
    customers = customers.drop_duplicates()
    # Fill missing emails with a placeholder
    customers['email'] = customers['email'].fillna('unknown@example.com')
    logging.info(f"Customers cleaning: dropped {cust_pre - len(customers)} duplicate rows.")

    # Transform - Products
    prod_pre = len(products)
    products = products.drop_duplicates()
    # Fix price column (remove ' USD' and convert to float)
    if products['price'].dtype == object:
        products['price'] = products['price'].astype(str).str.replace(' USD', '').astype(float)
    logging.info(f"Products cleaning: dropped {prod_pre - len(products)} duplicate rows and fixed price types.")

    # Transform - Orders
    order_pre = len(orders)
    orders = orders.drop_duplicates()
    
    # Handle missing quantities: set to 1 if missing
    orders['quantity'] = orders['quantity'].fillna(1).astype(int)
    
    # Recalculate total_amount to ensure correctness, or drop nulls
    # We will recalculate just to be safe
    prices_dict = products.set_index('product_id')['price'].to_dict()
    orders['total_amount'] = orders.apply(
        lambda row: round(prices_dict.get(row['product_id'], 0) * row['quantity'], 2), 
        axis=1
    )
    logging.info(f"Orders cleaning: dropped {order_pre - len(orders)} duplicate rows, fixed null quantities.")

    # Load
    db_path = 'retail.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    try:
        customers.to_sql('Customers', conn, index=False, if_exists='replace')
        products.to_sql('Products', conn, index=False, if_exists='replace')
        orders.to_sql('Orders', conn, index=False, if_exists='replace')
        
        logging.info("Successfully loaded clean data into retail.db")
    except Exception as e:
        logging.error(f"Failed to load data to DB: {e}")
    finally:
        conn.close()
        
if __name__ == "__main__":
    run_etl()
