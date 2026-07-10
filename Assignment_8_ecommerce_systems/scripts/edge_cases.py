import os
import sqlite3
import pandas as pd
from datetime import datetime

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DB_PATH = os.path.join(BASE_DIR, "data", "test_edge_cases.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")

def setup_test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    with open(SCHEMA_PATH, 'r') as schema_file:
        schema_sql = schema_file.read()
    conn.executescript(schema_sql)
    return conn

def test_orphaned_order_items():
  
    print("\n--- Test Case 1: Orphaned Order Items ---")
    conn = setup_test_db()
    cursor = conn.cursor()
    
    
    cursor.execute("INSERT INTO customers VALUES ('C001', 'Test User', 'test@example.com', '2026-01-01', 'REGULAR')")
    cursor.execute("INSERT INTO products VALUES ('P001', 'Test Product', 'Electronics', 'Gadgets', 10.0)")
    conn.commit()
    
   
    try:
        cursor.execute("INSERT INTO order_items VALUES ('IT001', 'O999', 'P001', 2, 12.0, 0.0)")
        conn.commit()
        print("FAIL")
    except sqlite3.IntegrityError as e:
        print(f"SUCCESS: {e}")
    finally:
        conn.close()

def test_invalid_discount_percent():
    
    print("\n--- Test Case 2: Invalid Discount Percent (> 100%) ---")
    conn = setup_test_db()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO customers VALUES ('C001', 'Test User', 'test@example.com', '2026-01-01', 'REGULAR')")
    cursor.execute("INSERT INTO products VALUES ('P001', 'Test Product', 'Electronics', 'Gadgets', 10.0)")
    cursor.execute("INSERT INTO orders VALUES ('O001', 'C001', '2026-01-02 12:00:00', 'PLACED', 'US-EAST')")
    conn.commit()
    
    
    try:
        cursor.execute("INSERT INTO order_items VALUES ('IT001', 'O001', 'P001', 1, 12.0, 110.0)")
        conn.commit()
        print("FAIL: ")
    except sqlite3.IntegrityError as e:
        print(f"SUCCESS: {e}")
    finally:
        conn.close()

def test_zero_quantity():
    print("\n--- Test Case 3: Zero Quantity Validation ---")
    

    raw_data = {
        'item_id': ['IT001', 'IT002', 'IT003'],
        'order_id': ['O001', 'O001', 'O001'],
        'product_id': ['P001', 'P002', 'P003'],
        'quantity': [2, 0, -1],  # IT002 has quantity 0
        'unit_price': [10.0, 15.0, 20.0],
        'discount_percent': [0.0, 5.0, 10.0]
    }
    df = pd.DataFrame(raw_data)
    print("Raw DataFrame with zero quantity row:")
    print(df)
    
    # In python cleaning, drop quantity = 0
    clean_df = df[df['quantity'] != 0]
    print("\nDataFrame after filtering zero quantity:")
    print(clean_df)
    
    if len(clean_df) == 2 and 'IT002' not in clean_df['item_id'].values:
        print("SUCCESS: Python filtered out zero quantity row correctly.")
    else:
        print("FAIL: Zero quantity row was not filtered.")

def test_future_order_date():
    
    print("\n--- Test Case 4: Future Order Dates ---")
    
    current_time = datetime.now()
    future_date = (current_time + pd.Timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    
    raw_orders = {
        'order_id': ['O001', 'O002'],
        'customer_id': ['C001', 'C002'],
        'order_date': ['2026-01-01 10:00:00', future_date],
        'status': ['PLACED', 'PLACED'],
        'region_code': ['US-EAST', 'US-WEST']
    }
    df = pd.DataFrame(raw_orders)
    print(f"Raw orders including a future order (Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}):")
    print(df)
    
    # Clean future order dates: convert to datetime and filter
    df['parsed_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    clean_df = df[df['parsed_date'] <= current_time].drop(columns=['parsed_date'])
    
    print("\nOrders after filtering out future dates:")
    print(clean_df)
    
    if len(clean_df) == 1 and 'O002' not in clean_df['order_id'].values:
        print("SUCCESS: Future order was correctly flagged and removed.")
    else:
        print("FAIL: Future order was not filtered.")

def run_all_tests():
    test_orphaned_order_items()
    test_invalid_discount_percent()
    test_zero_quantity()
    test_future_order_date()
    
    # Cleanup test DB file
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        
if __name__ == "__main__":
    run_all_tests()
