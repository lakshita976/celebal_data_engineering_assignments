import os
import re
import sqlite3
import pandas as pd
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
DB_PATH = os.path.join(BASE_DIR, "data", "ecommerce.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")
ANOMALY_REPORT_PATH = os.path.join(BASE_DIR, "output", "anomaly_report.txt")

os.makedirs(CLEANED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(ANOMALY_REPORT_PATH), exist_ok=True)

# Helper function to parse dates robustly
def parse_date(date_val):
    if pd.isna(date_val) or not str(date_val).strip():
        return None
    val = str(date_val).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d-%m-%Y', '%Y-%m-%d'):
        try:
            dt = datetime.strptime(val, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
    return None

def clean_orders(df_orders):
 
    print("\n--- Cleaning Orders ---")
    initial_rows = len(df_orders)
    
    # 1. Parse and standardize dates
    original_dates = df_orders['order_date'].copy()
    df_orders['order_date'] = df_orders['order_date'].apply(parse_date)
    
    date_fixes_mask = df_orders['order_date'] != original_dates
    num_date_fixes = date_fixes_mask.sum()
    print(f"Standardized {num_date_fixes} order dates to YYYY-MM-DD HH:MM:SS.")
    
    # 2. Check for missing customer_id
    null_cust_mask = df_orders['customer_id'].isna() | (df_orders['customer_id'].astype(str).str.strip() == '')
    null_cust_orders = df_orders[null_cust_mask]
    
    df_orders_cleaned = df_orders[~null_cust_mask].copy()
    removed_count = len(null_cust_orders)
    
    print(f"Found {removed_count} orders with NULL or missing customer_id (filtered out).")
    return df_orders_cleaned, null_cust_orders

def clean_products(df_products):
   
    print("\nCleaning Products ")
    df_products_cleaned = df_products.copy()
    
    # Normalize product_name
    df_products_cleaned['product_name'] = df_products_cleaned['product_name'].astype(str).str.strip().str.title()
    print("Normalized product names (trimmed spaces and converted to Title Case).")
    
    return df_products_cleaned

def validate_emails(df_customers):
   
    print("\nValidating Emails ")
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    invalid_mask = ~df_customers['email'].astype(str).str.match(email_regex, na=False)
    df_invalid = df_customers[invalid_mask].copy()
    
    print(f"Validated {len(df_customers)} emails. Found {len(df_invalid)} invalid emails.")
    return df_invalid

def check_referential_integrity(df_orders, df_products, df_order_items):
   
    print("\nChecking Referential Integrity ")
    valid_order_ids = set(df_orders['order_id'])
    valid_product_ids = set(df_products['product_id'])
    
    # Orphaned orders check
    orphan_order_mask = ~df_order_items['order_id'].isin(valid_order_ids)
    orphaned_orders = df_order_items[orphan_order_mask]
    
    # Orphaned products check
    orphan_product_mask = ~df_order_items['product_id'].isin(valid_product_ids)
    orphaned_products = df_order_items[orphan_product_mask]
    
    # Filter clean items
    df_items_clean = df_order_items[~orphan_order_mask & ~orphan_product_mask].copy()
    
    print(f"Found {len(orphaned_orders)} order_items referencing non-existent orders.")
    print(f"Found {len(orphaned_products)} order_items referencing non-existent products.")
    
    return df_items_clean, orphaned_orders, orphaned_products

def load_into_sqlite(df_cust, df_prod, df_ord, df_items):
   
    print("\n Loading into SQLite Database")
   
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH} for clean setup.")
        
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("PRAGMA foreign_keys = ON;")
    
    with open(SCHEMA_PATH, 'r') as schema_file:
        schema_sql = schema_file.read()
    conn.executescript(schema_sql)
    print("Database tables initialized from schema.sql.")
    
    # Insert data
    df_cust.to_sql("customers", conn, if_exists="append", index=False)
    df_prod.to_sql("products", conn, if_exists="append", index=False)
    df_ord.to_sql("orders", conn, if_exists="append", index=False)
    df_items.to_sql("order_items", conn, if_exists="append", index=False)
    
    print("Cleaned data successfully loaded into SQL tables.")
    
    # Verify row counts
    cursor = conn.cursor()
    tables = ["customers", "products", "orders", "order_items"]
    print("\nVerified Row Counts in SQL Database:")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"  - Table '{t}': {count} rows")
        
    conn.close()

def main():
    print("Starting data cleaning pipeline...")
    
    # Load raw CSVs
    df_cust = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    df_prod = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    df_ord = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
    df_items = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))
    
    # 1. Clean Products
    df_prod_clean = clean_products(df_prod)
    
    # 2. Validate Emails
    df_invalid_emails = validate_emails(df_cust)
    df_cust_clean = df_cust.copy()  # Keep all customers, but invalid emails are logged
    
    # 3. Clean Orders
    df_ord_clean, df_null_cust_orders = clean_orders(df_ord)
    
    df_items_clean, df_orph_orders, df_orph_products = check_referential_integrity(
        df_ord_clean, df_prod_clean, df_items
    )
    
    # Export cleaned CSVs
    df_cust_clean.to_csv(os.path.join(CLEANED_DIR, "customers_clean.csv"), index=False)
    df_prod_clean.to_csv(os.path.join(CLEANED_DIR, "products_clean.csv"), index=False)
    df_ord_clean.to_csv(os.path.join(CLEANED_DIR, "orders_clean.csv"), index=False)
    df_items_clean.to_csv(os.path.join(CLEANED_DIR, "order_items_clean.csv"), index=False)
    print(f"\nExported cleaned CSVs to {CLEANED_DIR}")
    
    
    load_into_sqlite(df_cust_clean, df_prod_clean, df_ord_clean, df_items_clean)
    

if __name__ == "__main__":
    main()
