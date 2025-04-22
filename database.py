import sqlite3

class Database:
    def __init__(self, db_name='store.db'):
        self.db_name = db_name
        # Create a single connection with a timeout
        self.conn = sqlite3.connect(self.db_name, timeout=10)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def fetch_all(self, table_name):
        """Fetch all records from a table"""
        self.cursor.execute(f'SELECT * FROM "{table_name}"')
        data = self.cursor.fetchall()
        return data

    def fetch_filtered(self, query, params=()):
        """Fetch records with a custom query and parameters"""
        self.cursor.execute(query, params)
        data = self.cursor.fetchall()
        return data

    def execute_query(self, query, params=()):
        """Execute a query that modifies the database (INSERT, UPDATE, DELETE)"""
        self.cursor.execute(query, params)

    def begin_transaction(self):
        """Begin a transaction"""
        self.conn.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        """Commit the transaction"""
        self.conn.commit()

    def rollback_transaction(self):
        """Rollback the transaction"""
        self.conn.rollback()

    def get_max_receipt_id(self):
        """Get the highest receipt ID number"""
        self.cursor.execute('SELECT check_number FROM "Check" WHERE check_number LIKE \'R%\'')
        receipt_ids = self.cursor.fetchall()
        if not receipt_ids:
            return 0
        numbers = [int(r[0][1:]) for r in receipt_ids]
        return max(numbers)

    def get_product_info(self, upc):
        """Get price and quantity of a product by UPC"""
        self.cursor.execute("SELECT selling_price, products_number FROM Store_Product WHERE UPC = ?", (upc,))
        result = self.cursor.fetchone()
        return result

    def get_customer_discount(self, card_number):
        """Get discount percentage for a customer"""
        self.cursor.execute("SELECT percent FROM Customer_Card WHERE card_number = ?", (card_number,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_promotional_status(self, upc):
        """Check if a product is promotional by UPC"""
        self.cursor.execute("SELECT promotional_product FROM Store_Product WHERE UPC = ?", (upc,))
        result = self.cursor.fetchone()
        return bool(result[0]) if result else False