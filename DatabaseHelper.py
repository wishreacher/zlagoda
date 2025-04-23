import sqlite3
from hashlib import sha256  # Kept for other uses in the project
import bcrypt  # For password hashing

class DatabaseHelper:
    def __init__(self):
        # Initialize database connection and cursor
        self.conn = sqlite3.connect("store.db")  # Adjust the database path if needed
        self.cursor = self.conn.cursor()

    def create_password_field(self):
        # Ensure the password field exists in the Employee table
        try:
            self.cursor.execute("ALTER TABLE Employee ADD COLUMN password TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

    def validate_login(self, username, password):
        # Fetch the stored (hashed) password and role for the given username
        query = "SELECT password, role FROM Employee WHERE id_employee = ?"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()

        if result:
            stored_password, role = result
            # Verify the entered password against the stored bcrypt hash
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    return {"role": role}
            except ValueError:
                # Invalid hash format (e.g., if it's a sha256 hash or corrupted)
                return None
        return None

    def fetch_all(self, table_name):
        # Fetch all records from a given table
        query = f"SELECT * FROM \"{table_name}\""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_filtered(self, query, params=()):
        # Fetch records based on a custom query with parameters
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_query(self, query, params=()):
        # Execute a query (INSERT, UPDATE, DELETE) with parameters
        self.cursor.execute(query, params)

    def begin_transaction(self):
        # Start a transaction
        self.conn.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        # Commit the current transaction
        self.conn.commit()

    def rollback_transaction(self):
        # Rollback the current transaction
        self.conn.rollback()

    def get_max_receipt_id(self):
        # Get the maximum receipt ID to generate a new check_number
        self.cursor.execute("SELECT MAX(check_number) FROM \"Check\"")
        max_id = self.cursor.fetchone()[0]
        if max_id:
            # Extract the numeric part (e.g., "R001" -> 1)
            num = int(max_id.replace("R", ""))
            return num
        return 0

    def get_product_info(self, upc):
        # Get product info (price and stock) by UPC
        query = "SELECT selling_price, products_number FROM Store_Product WHERE UPC = ?"
        self.cursor.execute(query, (upc,))
        result = self.cursor.fetchone()
        return result if result else None

    def get_customer_discount(self, card_number):
        # Get the discount percentage for a customer card
        query = "SELECT percent FROM Customer_Card WHERE card_number = ?"
        self.cursor.execute(query, (card_number,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        # Close the database connection
        self.conn.close()

    # Placeholder for other methods that might use sha256
    def some_other_method(self):
        data = "some_data"
        hashed_data = sha256(data.encode('utf-8')).hexdigest()
        return hashed_data