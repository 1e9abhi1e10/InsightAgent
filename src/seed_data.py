"""Synthetic retail dataset with 5 joinable tables."""

from __future__ import annotations

import random
from datetime import date, timedelta

from src.database import DB_PATH, get_connection

SEED = 42

CATEGORIES = [
    (1, "Electronics"),
    (2, "Clothing"),
    (3, "Home & Garden"),
    (4, "Sports"),
    (5, "Books"),
    (6, "Beauty"),
    (7, "Toys"),
    (8, "Grocery"),
]

PRODUCTS = [
    (1, "Wireless Headphones", 1, 79.99, 120),
    (2, "USB-C Hub", 1, 34.50, 200),
    (3, "Smart Watch", 1, 199.00, 85),
    (4, "Running Shoes", 4, 89.99, 150),
    (5, "Yoga Mat", 4, 29.99, 300),
    (6, "Denim Jacket", 2, 59.99, 90),
    (7, "Cotton T-Shirt", 2, 19.99, 500),
    (8, "Ceramic Planter", 3, 24.99, 180),
    (9, "LED Desk Lamp", 3, 44.99, 110),
    (10, "Python Crash Course", 5, 39.99, 75),
    (11, "Data Science Handbook", 5, 49.99, 60),
    (12, "Bluetooth Speaker", 1, 54.99, 140),
    (13, "Winter Scarf", 2, 22.99, 220),
    (14, "Tennis Racket", 4, 129.99, 45),
    (15, "Cookbook Collection", 5, 34.99, 95),
    (16, "Gaming Mouse", 1, 49.99, 130),
    (17, "Mechanical Keyboard", 1, 89.99, 95),
    (18, "Leather Wallet", 2, 39.99, 160),
    (19, "Wool Sweater", 2, 69.99, 80),
    (20, "Garden Hose", 3, 27.99, 140),
    (21, "Indoor Plant Set", 3, 34.99, 100),
    (22, "Basketball", 4, 24.99, 210),
    (23, "Dumbbell Set", 4, 119.99, 55),
    (24, "Mystery Novel", 5, 14.99, 300),
    (25, "Science Encyclopedia", 5, 59.99, 40),
    (26, "Facial Serum", 6, 44.99, 120),
    (27, "Lipstick Set", 6, 29.99, 180),
    (28, "Building Blocks", 7, 39.99, 150),
    (29, "Remote Control Car", 7, 54.99, 70),
    (30, "Organic Coffee", 8, 18.99, 260),
    (31, "Green Tea Pack", 8, 12.99, 320),
]

CUSTOMERS = [
    (1, "Alice Johnson", "alice@example.com", "North", "2023-01-15"),
    (2, "Bob Smith", "bob@example.com", "South", "2023-02-20"),
    (3, "Carol Williams", "carol@example.com", "East", "2023-03-10"),
    (4, "David Brown", "david@example.com", "West", "2023-04-05"),
    (5, "Eva Martinez", "eva@example.com", "North", "2023-05-18"),
    (6, "Frank Lee", "frank@example.com", "South", "2023-06-22"),
    (7, "Grace Kim", "grace@example.com", "East", "2023-07-30"),
    (8, "Henry Davis", "henry@example.com", "West", "2023-08-14"),
    (9, "Ivy Chen", "ivy@example.com", "North", "2023-09-01"),
    (10, "Jack Wilson", "jack@example.com", "South", "2023-10-25"),
    (11, "Karen Taylor", "karen@example.com", "East", "2023-11-12"),
    (12, "Leo Anderson", "leo@example.com", "West", "2024-01-08"),
    (13, "Mia Thomas", "mia@example.com", "North", "2024-02-17"),
    (14, "Noah Jackson", "noah@example.com", "South", "2024-03-22"),
    (15, "Olivia White", "olivia@example.com", "East", "2024-04-30"),
    (16, "Paul Green", "paul@example.com", "West", "2024-05-11"),
    (17, "Quinn Adams", "quinn@example.com", "North", "2024-05-28"),
    (18, "Rachel Nelson", "rachel@example.com", "South", "2024-06-15"),
    (19, "Sam Carter", "sam@example.com", "East", "2024-06-30"),
    (20, "Tina Mitchell", "tina@example.com", "West", "2024-07-19"),
    (21, "Umar Perez", "umar@example.com", "North", "2024-08-03"),
    (22, "Vera Roberts", "vera@example.com", "South", "2024-08-21"),
    (23, "Will Turner", "will@example.com", "East", "2024-09-09"),
    (24, "Xena Phillips", "xena@example.com", "West", "2024-09-27"),
    (25, "Yara Campbell", "yara@example.com", "North", "2024-10-14"),
    (26, "Zack Parker", "zack@example.com", "South", "2024-11-02"),
    (27, "Amy Evans", "amy@example.com", "East", "2024-11-20"),
    (28, "Brian Edwards", "brian@example.com", "West", "2024-12-08"),
    (29, "Cara Collins", "cara@example.com", "North", "2024-12-26"),
    (30, "Derek Stewart", "derek@example.com", "South", "2025-01-13"),
    (31, "Elena Sanchez", "elena@example.com", "East", "2025-01-31"),
    (32, "Felix Morris", "felix@example.com", "West", "2025-02-18"),
    (33, "Gina Rogers", "gina@example.com", "North", "2025-03-08"),
    (34, "Hugo Reed", "hugo@example.com", "South", "2025-03-26"),
    (35, "Iris Cook", "iris@example.com", "East", "2025-04-13"),
    (36, "Jonah Bell", "jonah@example.com", "West", "2025-05-01"),
    (37, "Kira Murphy", "kira@example.com", "North", "2025-05-19"),
    (38, "Liam Bailey", "liam@example.com", "South", "2025-06-06"),
    (39, "Nina Rivera", "nina@example.com", "East", "2025-06-24"),
    (40, "Omar Foster", "omar@example.com", "West", "2025-07-12"),
]

STATUSES = ["completed", "completed", "completed", "pending", "cancelled", "refunded"]

NUM_ORDERS = 250


def _generate_orders_and_items() -> tuple[list[tuple], list[tuple]]:
    rng = random.Random(SEED)  # local RNG → reproducible on every call
    orders: list[tuple] = []
    items: list[tuple] = []
    order_id = 1
    item_id = 1
    start = date(2024, 1, 1)

    for _ in range(NUM_ORDERS):
        customer_id = rng.randint(1, len(CUSTOMERS))
        order_date = start + timedelta(days=rng.randint(0, 600))
        status = rng.choice(STATUSES)
        orders.append((order_id, customer_id, order_date.isoformat(), status))

        num_items = rng.randint(1, 4)
        chosen_products = rng.sample(PRODUCTS, k=num_items)
        for product in chosen_products:
            qty = rng.randint(1, 3)
            price = product[3] * rng.choice([1.0, 1.0, 0.9, 1.1])
            items.append((item_id, order_id, product[0], qty, round(price, 2)))
            item_id += 1
        order_id += 1

    return orders, items


def seed_database(force: bool = False) -> None:
    if DB_PATH.exists() and not force:
        return

    orders, items = _generate_orders_and_items()
    conn = get_connection()
    try:
        conn.executescript(
            """
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS customers;
            DROP TABLE IF EXISTS categories;

            CREATE TABLE categories (
                category_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category_id INTEGER NOT NULL REFERENCES categories(category_id),
                unit_price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL
            );

            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                region TEXT NOT NULL,
                signup_date TEXT NOT NULL
            );

            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                order_date TEXT NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE order_items (
                item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(order_id),
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL
            );
            """
        )
        conn.executemany("INSERT INTO categories VALUES (?, ?)", CATEGORIES)
        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)", PRODUCTS
        )
        conn.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?)", CUSTOMERS
        )
        conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
        conn.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", items
        )
        conn.commit()
    finally:
        conn.close()
