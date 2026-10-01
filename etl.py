import pandas as pd
from sqlalchemy import create_engine, text
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
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logging.error("DATABASE_URL environment variable is not set. Cannot load data.")
        return
        
    engine = create_engine(db_url)
    try:
        # Use lowercase table names for PostgreSQL to avoid quoting issues
        customers.to_sql('customers', engine, index=False, if_exists='replace', method='multi')
        products.to_sql('products', engine, index=False, if_exists='replace', method='multi')
        orders.to_sql('orders', engine, index=False, if_exists='replace', method='multi')
        
        # Add primary keys and foreign keys for Postgres schema
        with engine.begin() as con:
            con.execute(text("ALTER TABLE customers ADD PRIMARY KEY (customer_id);"))
            con.execute(text("ALTER TABLE products ADD PRIMARY KEY (product_id);"))
            con.execute(text("ALTER TABLE orders ADD PRIMARY KEY (order_id);"))
            con.execute(text("ALTER TABLE orders ADD CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id);"))
            con.execute(text("ALTER TABLE orders ADD CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(product_id);"))
            
        logging.info("Successfully loaded clean data into PostgreSQL database")
    except Exception as e:
        logging.error(f"Failed to load data to DB: {e}")
    finally:
        engine.dispose()
        
if __name__ == "__main__":
    run_etl()
