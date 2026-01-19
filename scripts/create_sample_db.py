"""Script to create sample e-commerce database with realistic data."""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)


def create_database(db_path: str = "data/ecommerce.db"):
    """Create and populate the sample e-commerce database."""
    
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database
    if Path(db_path).exists():
        Path(db_path).unlink()
        print(f"Removed existing database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating database: {db_path}")
    
    # Create tables
    create_tables(cursor)
    print("✓ Tables created")
    
    # Insert sample data
    insert_categories(cursor)
    print("✓ Categories inserted")
    
    insert_products(cursor, num_products=100)
    print("✓ Products inserted")
    
    insert_customers(cursor, num_customers=50)
    print("✓ Customers inserted")
    
    insert_orders(cursor, num_orders=200)
    print("✓ Orders inserted")
    
    insert_order_items(cursor)
    print("✓ Order items inserted")
    
    insert_reviews(cursor, num_reviews=150)
    print("✓ Reviews inserted")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database created successfully: {db_path}")
    print_database_stats(db_path)


def create_tables(cursor):
    """Create all database tables."""
    
    # Categories table
    cursor.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    
    # Customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            country TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TIMESTAMP NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # Order items table
    cursor.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Reviews table
    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)


def insert_categories(cursor):
    """Insert product categories."""
    categories = [
        ("Electronics", "Electronic devices and gadgets"),
        ("Clothing", "Apparel and fashion items"),
        ("Books", "Physical and digital books"),
        ("Home & Garden", "Home improvement and garden supplies"),
        ("Sports & Outdoors", "Sports equipment and outdoor gear"),
        ("Toys & Games", "Toys, games, and puzzles"),
        ("Food & Beverages", "Groceries and drinks"),
        ("Health & Beauty", "Health and beauty products"),
    ]
    
    cursor.executemany(
        "INSERT INTO categories (name, description) VALUES (?, ?)",
        categories
    )


def insert_products(cursor, num_products=100):
    """Insert sample products."""
    
    product_templates = {
        1: ["Laptop", "Smartphone", "Tablet", "Headphones", "Camera", "Monitor", "Keyboard", "Mouse"],
        2: ["T-Shirt", "Jeans", "Dress", "Jacket", "Shoes", "Hat", "Scarf", "Socks"],
        3: ["Novel", "Textbook", "Magazine", "Comic Book", "Biography", "Cookbook"],
        4: ["Chair", "Table", "Lamp", "Rug", "Plant", "Curtains", "Vase"],
        5: ["Basketball", "Tennis Racket", "Yoga Mat", "Dumbbell", "Bicycle", "Tent"],
        6: ["Action Figure", "Board Game", "Puzzle", "Doll", "LEGO Set", "Video Game"],
        7: ["Coffee", "Tea", "Snacks", "Pasta", "Sauce", "Cereal", "Juice"],
        8: ["Shampoo", "Soap", "Lotion", "Vitamins", "Makeup", "Perfume"],
    }
    
    products = []
    for _ in range(num_products):
        category_id = random.randint(1, 8)
        product_type = random.choice(product_templates[category_id])
        brand = fake.company()
        
        name = f"{brand} {product_type}"
        price = round(random.uniform(9.99, 999.99), 2)
        stock = random.randint(0, 200)
        description = fake.sentence(nb_words=10)
        
        products.append((name, category_id, price, stock, description))
    
    cursor.executemany(
        "INSERT INTO products (name, category_id, price, stock, description) VALUES (?, ?, ?, ?, ?)",
        products
    )


def insert_customers(cursor, num_customers=50):
    """Insert sample customers."""
    customers = []
    
    for _ in range(num_customers):
        name = fake.name()
        email = fake.email()
        country = fake.country()
        city = fake.city()
        
        customers.append((name, email, country, city))
    
    cursor.executemany(
        "INSERT INTO customers (name, email, country, city) VALUES (?, ?, ?, ?)",
        customers
    )


def insert_orders(cursor, num_orders=200):
    """Insert sample orders."""
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    orders = []
    
    for _ in range(num_orders):
        customer_id = random.randint(1, 50)
        order_date = fake.date_time_between(start_date="-1y", end_date="now")
        total_amount = round(random.uniform(20.0, 2000.0), 2)
        status = random.choice(statuses)
        
        orders.append((customer_id, order_date, total_amount, status))
    
    cursor.executemany(
        "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?)",
        orders
    )


def insert_order_items(cursor):
    """Insert order items for each order."""
    order_items = []
    
    for order_id in range(1, 201):
        num_items = random.randint(1, 5)
        
        for _ in range(num_items):
            product_id = random.randint(1, 100)
            quantity = random.randint(1, 5)
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            price = cursor.fetchone()[0]
            
            order_items.append((order_id, product_id, quantity, price))
    
    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
        order_items
    )


def insert_reviews(cursor, num_reviews=150):
    """Insert product reviews."""
    reviews = []
    
    for _ in range(num_reviews):
        product_id = random.randint(1, 100)
        customer_id = random.randint(1, 50)
        rating = random.randint(1, 5)
        comment = fake.sentence(nb_words=15) if random.random() > 0.3 else None
        
        reviews.append((product_id, customer_id, rating, comment))
    
    cursor.executemany(
        "INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES (?, ?, ?, ?)",
        reviews
    )


def print_database_stats(db_path):
    """Print statistics about the created database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ["categories", "products", "customers", "orders", "order_items", "reviews"]
    
    print("\nDatabase Statistics:")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:20s}: {count:5d} rows")
    
    conn.close()


if __name__ == "__main__":
    create_database()
