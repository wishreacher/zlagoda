# Standalone script to set up passwords
import sqlite3
import hashlib


class PasswordSetupTool:
    def __init__(self, db_path="store.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def check_database_structure(self):
        """Check database structure and tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            print("Database tables:")
            for table in tables:
                print(f" - {table[0]}")
                # Show structure of each table
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"   * {col[1]} ({col[2]})")

            conn.close()
        except sqlite3.Error as e:
            print(f"Error checking database: {e}")

    def add_password_column(self):
        """Add password column to the Employee table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if Employee table exists and has the expected structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
            if not cursor.fetchone():
                print("Table 'Employee' does not exist.")
                employee_table_name = input("Enter the correct employee table name: ")
                if not employee_table_name:
                    conn.close()
                    return False
            else:
                employee_table_name = "Employee"

            # Check if password column already exists
            cursor.execute(f"PRAGMA table_info({employee_table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            if "password" not in column_names:
                print(f"Adding password column to {employee_table_name} table...")
                cursor.execute(f"ALTER TABLE {employee_table_name} ADD COLUMN password VARCHAR(100)")
                conn.commit()
                print("Password column added successfully")
            else:
                print("Password column already exists")

            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def list_employees(self):
        """List all employees to select for password setting"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # First check if Employee table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
            if not cursor.fetchone():
                print("Table 'Employee' does not exist.")
                employee_table_name = input("Enter the correct employee table name: ")
                if not employee_table_name:
                    conn.close()
                    return []
            else:
                employee_table_name = "Employee"

            # Check what columns are available
            cursor.execute(f"PRAGMA table_info({employee_table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            print(f"Available columns: {column_names}")

            # Construct query based on available columns
            query = f"SELECT id_employee"
            if "name" in column_names:
                query += ", name"
            if "surname" in column_names:
                query += ", surname"
            if "date_of_start" in column_names:
                query += ", date_of_start"
            if "role" in column_names:
                query += ", role"
            query += f" FROM {employee_table_name}"

            print(f"Executing query: {query}")
            cursor.execute(query)
            employees = cursor.fetchall()
            conn.close()
            return employees
        except sqlite3.Error as e:
            print(f"Error listing employees: {e}")
            return []

    def set_employee_password(self, employee_id, password):
        """Set password for an employee"""
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            conn = self.get_connection()
            cursor = conn.cursor()

            # First check if Employee table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
            if not cursor.fetchone():
                print("Table 'Employee' does not exist.")
                employee_table_name = input("Enter the correct employee table name: ")
                if not employee_table_name:
                    conn.close()
                    return False
            else:
                employee_table_name = "Employee"

            # Make sure password column exists
            self.add_password_column()

            # Update the password
            query = f"UPDATE {employee_table_name} SET password = ? WHERE id_employee = ?"
            print(f"Executing: {query} with values ({hashed_password}, {employee_id})")
            cursor.execute(query, (hashed_password, employee_id))
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            if rows_affected > 0:
                return True
            else:
                print(f"No rows updated. Employee ID {employee_id} may not exist.")
                return False
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False


# Run this as a standalone script
if __name__ == "__main__":
    setup = PasswordSetupTool()

    print("==== Database Structure Check ====")
    setup.check_database_structure()

    print("\n==== Adding Password Column ====")
    setup.add_password_column()

    print("\n==== Available Employees ====")
    employees = setup.list_employees()

    if employees:
        print("Available employees:")
        for emp in employees:
            # Print available fields (may vary depending on database structure)
            print(f"ID: {emp[0]}", end="")
            if len(emp) > 1:
                print(f", Name: {emp[1]}", end="")
            if len(emp) > 2:
                print(f" {emp[2]}", end="")
            if len(emp) > 3:
                print(f", Login: {emp[3]}", end="")
            if len(emp) > 4:
                print(f", Role: {emp[4]}", end="")
            print()

        emp_id = input("\nEnter employee ID to set password: ")
        password = input("Enter password: ")
        if setup.set_employee_password(emp_id, password):
            print("Password set successfully")
        else:
            print("Failed to set password")
    else:
        print("No employees found.")