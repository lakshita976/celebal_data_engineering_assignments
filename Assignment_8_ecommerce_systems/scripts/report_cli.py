import os
import sys
import sqlite3
import argparse
from datetime import datetime, timedelta

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "sql")
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "ecommerce.db")

# Dictionary mapping report names to SQL files and statement indices (0-based)
REPORTS_MAPPING = {
    "revenue": ("aggregations.sql", 0, "Total Revenue per Category"),
    "top_customers": ("aggregations.sql", 1, "Top 10 Customers by Total Order Value"),
    "monthly_orders": ("aggregations.sql", 2, "Month-wise Order Count (Last 12 Months)"),
    "undelivered": ("aggregations.sql", 3, "Customers with Undelivered Orders Only"),
    "high_returns": ("aggregations.sql", 4, "Products with More Returns than Purchases"),
    "return_rates": ("aggregations.sql", 5, "Return Rate (Returned / Purchased) per Category"),
    "running_totals": ("window_functions.sql", 0, "Running Total of Revenue per Region"),
    "product_ranking": ("window_functions.sql", 1, "Product Revenue Ranking inside Categories"),
    "lag_analysis": ("window_functions.sql", 2, "Customer Days Between Consecutive Orders (Gap Analysis)"),
    "spend_cohorts": ("window_functions.sql", 3, "Spender Cohort Customer Count per Month"),
    "ltv_segmentation": ("window_functions.sql", 4, "Customer LTV Quartile Segmentation"),
    "yoy_growth": ("window_functions.sql", 5, "Year-over-Year Monthly Revenue Growth Comparison"),
    "category_shift": ("window_functions.sql", 6, "Customer First vs Last Category Shift Analysis"),
    "cumulative_dist": ("window_functions.sql", 7, "Cumulative Distribution of Customer Revenue"),
    "cohort_retention": ("cohort_analysis.sql", 0, "Cohort Retention Analysis (Months 0-3)"),
    "co_purchase": ("window_functions.sql", 8, "Products Frequently Bought Together")
}

def format_as_table(headers, rows):
    if not rows:
        return "No data found."
    
    num_cols = len(headers)
  
    string_rows = []
    for r in rows:
        string_rows.append([str(val) if val is not None else "NULL" for val in r])
        
    col_widths = [len(h) for h in headers]
    for row in string_rows:
        for col_idx in range(num_cols):
            if col_idx < len(row):
                col_widths[col_idx] = max(col_widths[col_idx], len(row[col_idx]))
                
    alignments = []
    for col_idx in range(num_cols):
        align = "<"
        for r in rows:
            if r[col_idx] is not None:
                val = r[col_idx]
                if isinstance(val, (int, float)) or (isinstance(val, str) and val.replace('.', '', 1).replace('-', '', 1).isdigit()):
                    align = ">"
                break
        alignments.append(align)
        
    lines = []
    
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    lines.append(separator)
    
    header_cells = [f" {headers[i]:^{col_widths[i]}} " for i in range(num_cols)]
    lines.append("|" + "|".join(header_cells) + "|")
    lines.append(separator)
    
    for row in string_rows:
        cells = []
        for col_idx in range(num_cols):
            val = row[col_idx]
            align = alignments[col_idx]
            if align == ">":
                cells.append(f" {val:>{col_widths[col_idx]}} ")
            else:
                cells.append(f" {val:<{col_widths[col_idx]}} ")
        lines.append("|" + "|".join(cells) + "|")
        
    lines.append(separator)
    return "\n".join(lines)

def load_query_from_sql(sql_filename, statement_index):
    
    filepath = os.path.join(SQL_DIR, sql_filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"SQL file not found at: {filepath}")
        
    with open(filepath, 'r') as f:
        content = f.read()
        
    statements = []
    parts = content.split(";")
    for part in parts:
        lines = part.split("\n")
        clean_lines = []
        for line in lines:
            if not line.strip().startswith("--"):
                clean_lines.append(line)
        query = "\n".join(clean_lines).strip()
        if query:
            statements.append(query)
            
    if statement_index >= len(statements):
        raise IndexError(f"Index {statement_index} out of bounds (found {len(statements)} statements in {sql_filename}).")
        
    return statements[statement_index]

def run_named_report(db_path, report_key):
    if report_key not in REPORTS_MAPPING:
        print(f"Error: Unknown report '{report_key}'")
        print("Available reports: " + ", ".join(REPORTS_MAPPING.keys()))
        return
        
    sql_file, stmt_idx, report_title = REPORTS_MAPPING[report_key]
    
    try:
        query = load_query_from_sql(sql_file, stmt_idx)
    except Exception as e:
        print(f"Error loading query from SQL file: {e}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        
        print(format_as_table(headers, rows))
        print(f"Total Rows: {len(rows)}\n")
        
    except sqlite3.Error as e:
        print(f"Database error executing query: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def run_interactive_period_report(db_path):
    print("\n--- Interactive Period Report Generator ---")
    
    while True:
        report_type = input("Enter report type (daily / weekly / monthly): ").strip().lower()
        if report_type in ['daily', 'weekly', 'monthly']:
            break
        print("Invalid input. Please enter 'daily', 'weekly', or 'monthly'.")
        
    while True:
        date_str = input("Enter start date (YYYY-MM-DD): ").strip()
        try:
            start_date = datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            
    # Compute current and previous period boundaries
    if report_type == 'daily':
        duration_days = 1
        end_date = start_date
    elif report_type == 'weekly':
        duration_days = 7
        end_date = start_date + timedelta(days=6)
    else: 
        # Find start of next month to get exact days in calendar month
        if start_date.month == 12:
            next_month = datetime(start_date.year + 1, 1, 1)
        else:
            next_month = datetime(start_date.year, start_date.month + 1, 1)
        duration_days = (next_month - start_date).days
        end_date = start_date + timedelta(days=duration_days - 1)
        
    # Previous period is the same duration ending the day before start_date
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = start_date - timedelta(days=duration_days)
    
    current_start_str = start_date.strftime("%Y-%m-%d 00:00:00")
    current_end_str = end_date.strftime("%Y-%m-%d 23:59:59")
    prev_start_str = prev_start_date.strftime("%Y-%m-%d 00:00:00")
    prev_end_str = prev_end_date.strftime("%Y-%m-%d 23:59:59")
    
    print(f"\nAnalyzing Period:")
    print(f"  - Current:  {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({duration_days} days)")
    print(f"  - Previous: {prev_start_date.strftime('%Y-%m-%d')} to {prev_end_date.strftime('%Y-%m-%d')} ({duration_days} days)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        
        def get_period_stats(t_start, t_end):
            # Orders
            cursor.execute("SELECT COUNT(DISTINCT order_id) FROM orders WHERE order_date BETWEEN ? AND ?", (t_start, t_end))
            orders_cnt = cursor.fetchone()[0] or 0
            
            # Revenue
            cursor.execute("""
                SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0))
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.order_date BETWEEN ? AND ?
            """, (t_start, t_end))
            rev = cursor.fetchone()[0] or 0.0
            
            # Customers
            cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM orders WHERE order_date BETWEEN ? AND ? AND customer_id != ''", (t_start, t_end))
            custs = cursor.fetchone()[0] or 0
            
            return orders_cnt, rev, custs

        curr_orders, curr_revenue, curr_customers = get_period_stats(current_start_str, current_end_str)
        prev_orders, prev_revenue, prev_customers = get_period_stats(prev_start_str, prev_end_str)
        
        # Calculate percent changes
        def get_pct_change(curr, prev):
            if prev == 0:
                return "N/A"
            change = (curr - prev) * 100.0 / prev
            sign = "+" if change >= 0 else ""
            return f"{sign}{change:.2f}%"

        orders_change = get_pct_change(curr_orders, prev_orders)
        revenue_change = get_pct_change(curr_revenue, prev_revenue)
        customers_change = get_pct_change(curr_customers, prev_customers)
        
        # Top 3 products in current period
        cursor.execute("""
            SELECT 
                p.product_name,
                SUM(oi.quantity) AS qty_sold,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS prod_rev
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_date BETWEEN ? AND ?
            GROUP BY p.product_id, p.product_name
            ORDER BY qty_sold DESC
            LIMIT 3
        """, (current_start_str, current_end_str))
        top_products = cursor.fetchall()
        
        # Output Summary table
        print(f"\n==================================================================")
        print(f" PERIOD SUMMARY REPORT ({report_type.upper()})")
        print(f"==================================================================")
        
        summary_headers = ["Metric", "Previous Period", "Current Period", "% Change"]
        summary_rows = [
            ["Total Orders", prev_orders, curr_orders, orders_change],
            ["Total Revenue", f"${prev_revenue:,.2f}", f"${curr_revenue:,.2f}", revenue_change],
            ["Unique Customers", prev_customers, curr_customers, customers_change]
        ]
        print(format_as_table(summary_headers, summary_rows))
        
        # Output Top 3 products
        print("\nTOP 3 PRODUCTS BY QUANTITY SOLD:")
        if top_products:
            prod_headers = ["Product Name", "Quantity Sold", "Revenue"]
            prod_rows = [[r[0], r[1], f"${r[2]:,.2f}"] for r in top_products]
            print(format_as_table(prod_headers, prod_rows))
        else:
            print("No product sales recorded in this period.")
            
    except sqlite3.Error as e:
        print(f"Database connection or execution error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="E-Commerce Order Analytics System CLI Tool")
    parser.add_argument(
        "--report", 
        type=str, 
        choices=list(REPORTS_MAPPING.keys()),
        help="Run a specific predefined analytical report. Choices: " + ", ".join(REPORTS_MAPPING.keys())
    )
    parser.add_argument(
        "--interactive", 
        action="store_true", 
        help="Run in interactive mode to generate custom period summary reports."
    )
    parser.add_argument(
        "--db", 
        type=str, 
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})"
    )
    
    args = parser.parse_args()
    
    # Validate database file exists
    if not os.path.exists(args.db):
        print(f"Error: Database file does not exist at '{args.db}'")
        print("Please run scripts/clean_data.py to clean raw data and populate the database first.")
        sys.exit(1)
        
    # Determine mode: default to interactive if no report is explicitly requested
    if args.report:
        run_named_report(args.db, args.report)
    elif args.interactive or len(sys.argv) == 1:
        run_interactive_period_report(args.db)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
