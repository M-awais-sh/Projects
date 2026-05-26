import sqlite3

# Database functions
def connect_db():
    return sqlite3.connect('inventory.db')

def create_table():
    with connect_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS stock (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_name TEXT NOT NULL,
                            quantity INTEGER NOT NULL,
                            price REAL NOT NULL,
                            category TEXT NOT NULL)''')
        conn.commit()

def insert_item(name, qty, price, category):
    with connect_db() as conn:
        conn.execute("INSERT INTO stock (item_name, quantity, price, category) VALUES (?, ?, ?, ?)", (name, qty, price, category))
        conn.commit()

def get_items():
    with connect_db() as conn:
        return conn.execute("SELECT * FROM stock").fetchall()

def update_item(item_id, name, qty, price, category):
    with connect_db() as conn:
        conn.execute("UPDATE stock SET item_name=?, quantity=?, price=?, category=? WHERE id=?", (name, qty, price, category, item_id))
        conn.commit()

def delete_item(item_id):
    with connect_db() as conn:
        conn.execute("DELETE FROM stock WHERE id=?", (item_id,))
        conn.commit()

def delete_table():
    with connect_db() as conn:
        conn.execute("DROP TABLE IF EXISTS stock")
        conn.commit()

# Additional utility functions for category management
def get_items_by_category(category):
    """Get all items in a specific category"""
    with connect_db() as conn:
        return conn.execute("SELECT * FROM stock WHERE category=?", (category,)).fetchall()

def get_category_summary():
    """Get count and total value by category"""
    with connect_db() as conn:
        return conn.execute("""
            SELECT category, 
                   COUNT(*) as item_count, 
                   SUM(quantity) as total_quantity,
                   SUM(quantity * price) as total_value
            FROM stock 
            GROUP BY category
            ORDER BY category
        """).fetchall()

def migrate_existing_data():
    """Add category column to existing database and set default values"""
    with connect_db() as conn:
        try:
            # Check if category column exists
            cursor = conn.execute("PRAGMA table_info(stock)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'category' not in columns:
                # Add category column with default value
                conn.execute("ALTER TABLE stock ADD COLUMN category TEXT DEFAULT 'Other'")
                # Update all existing records to have 'Other' category
                conn.execute("UPDATE stock SET category = 'Other' WHERE category IS NULL")
                conn.commit()
                print("Database migrated successfully - added category column")
            else:
                print("Category column already exists")
                
        except Exception as e:
            print(f"Migration error: {e}")

# Billing system functions
def create_billing_tables():
    """Create tables for billing system"""
    with connect_db() as conn:
        # Bills table
        conn.execute('''CREATE TABLE IF NOT EXISTS bills (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            customer_name TEXT NOT NULL,
                            bill_date TEXT NOT NULL,
                            total_amount REAL NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Bill items table
        conn.execute('''CREATE TABLE IF NOT EXISTS bill_items (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            bill_id INTEGER NOT NULL,
                            item_id INTEGER NOT NULL,
                            item_name TEXT NOT NULL,
                            quantity INTEGER NOT NULL,
                            unit_price REAL NOT NULL,
                            total_price REAL NOT NULL,
                            FOREIGN KEY (bill_id) REFERENCES bills (id),
                            FOREIGN KEY (item_id) REFERENCES stock (id))''')
        conn.commit()

def search_item_by_name(item_name):
    """Search for items by name (partial match)"""
    with connect_db() as conn:
        return conn.execute("""
            SELECT id, item_name, quantity, price, category 
            FROM stock 
            WHERE LOWER(item_name) LIKE LOWER(?) AND quantity > 0
        """, (f'%{item_name}%',)).fetchall()

def get_item_by_id(item_id):
    """Get item details by ID"""
    with connect_db() as conn:
        return conn.execute("SELECT * FROM stock WHERE id=?", (item_id,)).fetchone()

def create_bill(customer_name, bill_date, bill_items):
    """Create a new bill with items"""
    with connect_db() as conn:
        # Calculate total amount
        total_amount = sum(item['total_price'] for item in bill_items)
        
        # Insert bill
        cursor = conn.execute("""
            INSERT INTO bills (customer_name, bill_date, total_amount) 
            VALUES (?, ?, ?)
        """, (customer_name, bill_date, total_amount))
        
        bill_id = cursor.lastrowid
        
        # Insert bill items and update stock
        for item in bill_items:
            # Insert bill item
            conn.execute("""
                INSERT INTO bill_items (bill_id, item_id, item_name, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (bill_id, item['item_id'], item['item_name'], item['quantity'], 
                  item['unit_price'], item['total_price']))
            
            # Update stock quantity
            conn.execute("""
                UPDATE stock SET quantity = quantity - ? WHERE id = ?
            """, (item['quantity'], item['item_id']))
        
        conn.commit()
        return bill_id

def get_bills():
    """Get all bills"""
    with connect_db() as conn:
        return conn.execute("""
            SELECT id, customer_name, bill_date, total_amount, created_at 
            FROM bills 
            ORDER BY created_at DESC
        """).fetchall()

def get_bill_details(bill_id):
    """Get bill details with items"""
    with connect_db() as conn:
        # Get bill info
        bill = conn.execute("""
            SELECT id, customer_name, bill_date, total_amount, created_at 
            FROM bills WHERE id = ?
        """, (bill_id,)).fetchone()
        
        # Get bill items
        items = conn.execute("""
            SELECT item_name, quantity, unit_price, total_price 
            FROM bill_items WHERE bill_id = ?
        """, (bill_id,)).fetchall()
        
        return bill, items

def get_daily_sales(date):
    """Get total sales for a specific date"""
    with connect_db() as conn:
        return conn.execute("""
            SELECT COUNT(*) as bill_count, SUM(total_amount) as total_sales
            FROM bills WHERE bill_date = ?
        """, (date,)).fetchone()

def get_monthly_sales(year_month):
    """Get monthly sales summary (year_month format: '2024-01')"""
    with connect_db() as conn:
        return conn.execute("""
            SELECT COUNT(*) as bill_count, SUM(total_amount) as total_sales
            FROM bills WHERE strftime('%Y-%m', bill_date) = ?
        """, (year_month,)).fetchone()