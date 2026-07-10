import os
import csv
import random
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_data_dir = os.path.join(base_dir, "data", "raw")
os.makedirs(raw_data_dir, exist_ok=True)

random.seed(42)

FIRST_NAMES = [
    "John", "Jane", "Robert", "Emily", "Michael", "Jessica", "David", "Sarah",
    "James", "Emma", "William", "Olivia", "Daniel", "Sophia", "Matthew",
    "Isabella", "Christopher", "Ava", "Andrew", "Mia", "Joseph", "Abigail",
    "Joshua", "Emily", "Ryan", "Charlotte", "Nicholas", "Harper", "Tyler",
    "Amelia", "Brandon", "Evelyn", "Zachary", "Abigail", "Justin",
    "Elizabeth", "Alexander", "Sofia", "Kevin", "Avery"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

PRODUCT_CATALOG = {
    "Electronics": [
        ("Laptop Pro 15", 1200.00),
        ("Smartphone X", 800.00),
        ("Wireless Headphones", 150.00),
        ("Smartwatch Sport", 250.00),
        ("4K Monitor 27", 350.00),
        ("Bluetooth Speaker", 75.00),
        ("USB-C Charger Hub", 29.99),
        ("Ergonomic Wireless Mouse", 49.99),
        ("Mechanical Keyboard", 89.99)
    ],
    "Clothing": [
        ("Classic Crewneck T-Shirt", 19.99),
        ("Slim Fit Denim Jeans", 59.99),
        ("Fleece Pullover Hoodie", 45.00),
        ("Waterproof Winter Jacket", 120.00),
        ("Running Sneakers", 85.00),
        ("Athletic Crew Socks (3-Pack)", 12.50),
        ("Summer Floral Dress", 49.99),
        ("Wide Brim Sun Hat", 24.50),
        ("Leather Dress Belt", 35.00)
    ],
    "Home": [
        ("Drip Coffee Maker", 49.99),
        ("High-Speed Countertop Blender", 89.99),
        ("2-Slice Retro Toaster", 39.99),
        ("Adjustable LED Desk Lamp", 29.99),
        ("HEPA Air Purifier", 120.00),
        ("Cordless Stick Vacuum", 199.99),
        ("Memory Foam Pillow", 35.00),
        ("Boho Area Rug", 75.00),
        ("Organic Cotton Towel Set", 40.00)
    ],
    "Books": [
        ("The Midnight Mystery Fiction Novel", 14.99),
        ("Unbroken Spirit Biography", 19.99),
        ("Beyond The Stars Sci-Fi Book", 16.50),
        ("Mastering the Kitchen Cookbook", 29.99),
        ("History of the Modern World", 35.00),
        ("Echoes in the Dark Mystery Novel", 12.99),
        ("Daily Habits Self-Help Book", 15.00),
        ("Intro to Python Programming Textbook", 49.99),
        ("Financial Freedom Guide", 22.00)
    ]
}

REGIONS = ["US-EAST", "US-WEST", "EU-CENTRAL", "AP-SOUTH", "AP-EAST", "LA-SOUTH"]
ORDER_STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]


def generate_customers(num_customers=100):
    customers = []
    start = datetime(2024, 1, 1)

    for i in range(1, num_customers + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"

        if i % 30 == 0:
            email = f"{first.lower()}.{last.lower()}example.com"
        elif i % 45 == 0:
            email = f"{first.lower()}.{last.lower()}@"
        else:
            email = f"{first.lower()}.{last.lower()}@example.com"

        reg_date = start + timedelta(days=random.randint(0, 800))

        customer_type = random.choices(
            CUSTOMER_TYPES,
            weights=[0.70, 0.20, 0.10]
        )[0]

        customers.append({
            "customer_id": f"CUST{i:04d}",
            "customer_name": name,
            "email": email,
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "customer_type": customer_type
        })

    return customers


def generate_products(num_products=50):
    products = []
    categories = list(PRODUCT_CATALOG.keys())
    pid = 1

    while len(products) < num_products:
        category = random.choice(categories)
        name, price = random.choice(PRODUCT_CATALOG[category])

        modified_name = name
        r = random.random()

        if r < 0.10:
            modified_name = f"  {name}  "
        elif r < 0.20:
            modified_name = "".join(
                c.upper() if random.random() > 0.5 else c.lower()
                for c in name
            )

        products.append({
            "product_id": f"PROD{pid:03d}",
            "product_name": modified_name,
            "category": category,
            "subcategory": name.split()[-1],
            "cost_price": round(price, 2)
        })

        pid += 1

    return products


def generate_orders(customers, num_orders=600):
    orders = []

    for i in range(1, num_orders + 1):
        if random.random() < 0.05:
            customer_id = ""
        else:
            customer_id = random.choice(customers)["customer_id"]

        if customer_id:
            reg = next(
                c["registration_date"]
                for c in customers
                if c["customer_id"] == customer_id
            )
            reg_date = datetime.strptime(reg, "%Y-%m-%d")
        else:
            reg_date = datetime(2024, 1, 1)

        max_days = (datetime(2026, 7, 1) - reg_date).days

        if max_days <= 0:
            order_date = reg_date
        else:
            order_date = reg_date + timedelta(
                days=random.randint(0, max_days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )

        if random.random() < 0.05:
            date_value = order_date.strftime("%d-%m-%Y")
        else:
            date_value = order_date.strftime("%Y-%m-%d %H:%M:%S")

        orders.append({
            "order_id": f"ORD{i:05d}",
            "customer_id": customer_id,
            "order_date": date_value,
            "status": random.choices(
                ORDER_STATUSES,
                weights=[0.10, 0.15, 0.60, 0.08, 0.07]
            )[0],
            "region_code": random.choice(REGIONS)
        })

    return orders


def generate_order_items(orders, products, num_items=1200):
    items = []

    for i in range(1, num_items + 1):
        if random.random() < 0.01:
            order_id = f"ORD{random.randint(99990, 99999):05d}"
        else:
            order_id = random.choice(orders)["order_id"]

        product = random.choice(products)

        cost = product["cost_price"]
        unit_price = round(cost * random.uniform(1.2, 1.5), 2)

        if random.random() < 0.30:
            discount = random.choices(
                [5, 10, 15, 20, 25, 30],
                weights=[0.3, 0.3, 0.2, 0.1, 0.05, 0.05]
            )[0]
        else:
            discount = 0

        if random.random() < 0.03:
            quantity = -random.randint(1, 3)
        else:
            quantity = random.randint(1, 5)

        items.append({
            "item_id": f"ITEM{i:05d}",
            "order_id": order_id,
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percent": discount
        })

    return items


def save_to_csv(data, filename, columns):
    path = os.path.join(raw_data_dir, filename)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)

    print(f"{filename} created with {len(data)} rows")


if __name__ == "__main__":
    print("Creating datasets...")

    customers = generate_customers(120)
    save_to_csv(
        customers,
        "customers.csv",
        ["customer_id", "customer_name", "email",
         "registration_date", "customer_type"]
    )

    products = generate_products(60)
    save_to_csv(
        products,
        "products.csv",
        ["product_id", "product_name",
         "category", "subcategory", "cost_price"]
    )

    orders = generate_orders(customers, 550)
    save_to_csv(
        orders,
        "orders.csv",
        ["order_id", "customer_id",
         "order_date", "status", "region_code"]
    )

    order_items = generate_order_items(orders, products, 1100)
    save_to_csv(
        order_items,
        "order_items.csv",
        ["item_id", "order_id", "product_id",
         "quantity", "unit_price", "discount_percent"]
    )

    print("Done!")