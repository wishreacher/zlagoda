import sqlite3
import hashlib

class DatabaseHelper:
    def __init__(self, db_path="store.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_password_field(self):
        """Add password field to the Employee table if it doesn't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # First, check if the Employee table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
            if not cursor.fetchone():
                print("Error: Employee table does not exist.")
                print("Available tables:")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                for table in tables:
                    print(f" - {table[0]}")
                conn.close()
                return False

            # Check if password column already exists
            cursor.execute("PRAGMA table_info(Employee)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            print(f"Current columns in Employee table: {column_names}")

            if "password" not in column_names:
                print("Attempting to add password column...")
                cursor.execute("ALTER TABLE Employee ADD COLUMN password VARCHAR(100)")
                conn.commit()
                print("Password column added successfully")
            else:
                print("Password column already exists")

            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            print(f"Database path: {self.db_path}")
            return False

    def set_password(self, employee_id, password):
        """Set hashed password for an employee"""
        try:
            # First verify the employee exists
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_employee FROM Employee WHERE id_employee = ?", (employee_id,))
            if not cursor.fetchone():
                print(f"Employee with ID {employee_id} not found")
                conn.close()
                return False

            # Make sure password column exists
            self.create_password_field()

            # Now set the password
            hashed_password = self._hash_password(password)
            cursor.execute("UPDATE Employee SET password = ? WHERE id_employee = ?",
                           (hashed_password, employee_id))
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            if rows_affected > 0:
                print(f"Password set successfully for employee ID {employee_id}")
                return True
            else:
                print(f"No rows updated for employee ID {employee_id}")
                return False
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def validate_login(self, login, password):
        """Validate login credentials against the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id_employee, role, password FROM Employee WHERE id_employee = ?", (login,))
            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                stored_id, role, stored_password = user_data

                # If password is not set yet in the database
                if stored_password is None:
                    return None

                # Verify password
                hashed_input = self._hash_password(password)
                if hashed_input == stored_password:
                    return {"id": stored_id, "role": role}

            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def _hash_password(self, password):
        """Create a SHA-256 hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()