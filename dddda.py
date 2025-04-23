# # # Standalone script to set up passwords
# # import sqlite3
# # import hashlib
# #
# #
# # class PasswordSetupTool:
# #     def __init__(self, db_path="store.db"):
# #         self.db_path = db_path
# #
# #     def get_connection(self):
# #         return sqlite3.connect(self.db_path)
# #
# #     def check_database_structure(self):
# #         """Check database structure and tables"""
# #         try:
# #             conn = self.get_connection()
# #             cursor = conn.cursor()
# #
# #             # List all tables
# #             cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
# #             tables = cursor.fetchall()
# #
# #             print("Database tables:")
# #             for table in tables:
# #                 print(f" - {table[0]}")
# #                 # Show structure of each table
# #                 cursor.execute(f"PRAGMA table_info({table[0]})")
# #                 columns = cursor.fetchall()
# #                 for col in columns:
# #                     print(f"   * {col[1]} ({col[2]})")
# #
# #             conn.close()
# #         except sqlite3.Error as e:
# #             print(f"Error checking database: {e}")
# #
# #     def add_password_column(self):
# #         """Add password column to the Employee table"""
# #         try:
# #             conn = self.get_connection()
# #             cursor = conn.cursor()
# #
# #             # Check if Employee table exists and has the expected structure
# #             cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
# #             if not cursor.fetchone():
# #                 print("Table 'Employee' does not exist.")
# #                 employee_table_name = input("Enter the correct employee table name: ")
# #                 if not employee_table_name:
# #                     conn.close()
# #                     return False
# #             else:
# #                 employee_table_name = "Employee"
# #
# #             # Check if password column already exists
# #             cursor.execute(f"PRAGMA table_info({employee_table_name})")
# #             columns = cursor.fetchall()
# #             column_names = [col[1] for col in columns]
# #
# #             if "password" not in column_names:
# #                 print(f"Adding password column to {employee_table_name} table...")
# #                 cursor.execute(f"ALTER TABLE {employee_table_name} ADD COLUMN password VARCHAR(100)")
# #                 conn.commit()
# #                 print("Password column added successfully")
# #             else:
# #                 print("Password column already exists")
# #
# #             conn.close()
# #             return True
# #         except sqlite3.Error as e:
# #             print(f"Database error: {e}")
# #             return False
# #
# #     def list_employees(self):
# #         """List all employees to select for password setting"""
# #         try:
# #             conn = self.get_connection()
# #             cursor = conn.cursor()
# #
# #             # First check if Employee table exists
# #             cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
# #             if not cursor.fetchone():
# #                 print("Table 'Employee' does not exist.")
# #                 employee_table_name = input("Enter the correct employee table name: ")
# #                 if not employee_table_name:
# #                     conn.close()
# #                     return []
# #             else:
# #                 employee_table_name = "Employee"
# #
# #             # Check what columns are available
# #             cursor.execute(f"PRAGMA table_info({employee_table_name})")
# #             columns = cursor.fetchall()
# #             column_names = [col[1] for col in columns]
# #
# #             print(f"Available columns: {column_names}")
# #
# #             # Construct query based on available columns
# #             query = f"SELECT id_employee"
# #             if "name" in column_names:
# #                 query += ", name"
# #             if "surname" in column_names:
# #                 query += ", surname"
# #             if "date_of_start" in column_names:
# #                 query += ", date_of_start"
# #             if "role" in column_names:
# #                 query += ", role"
# #             query += f" FROM {employee_table_name}"
# #
# #             print(f"Executing query: {query}")
# #             cursor.execute(query)
# #             employees = cursor.fetchall()
# #             conn.close()
# #             return employees
# #         except sqlite3.Error as e:
# #             print(f"Error listing employees: {e}")
# #             return []
# #
# #     def set_employee_password(self, employee_id, password):
# #         """Set password for an employee"""
# #         try:
# #             hashed_password = hashlib.sha256(password.encode()).hexdigest()
# #             conn = self.get_connection()
# #             cursor = conn.cursor()
# #
# #             # First check if Employee table exists
# #             cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employee'")
# #             if not cursor.fetchone():
# #                 print("Table 'Employee' does not exist.")
# #                 employee_table_name = input("Enter the correct employee table name: ")
# #                 if not employee_table_name:
# #                     conn.close()
# #                     return False
# #             else:
# #                 employee_table_name = "Employee"
# #
# #             # Make sure password column exists
# #             self.add_password_column()
# #
# #             # Update the password
# #             query = f"UPDATE {employee_table_name} SET password = ? WHERE id_employee = ?"
# #             print(f"Executing: {query} with values ({hashed_password}, {employee_id})")
# #             cursor.execute(query, (hashed_password, employee_id))
# #             rows_affected = cursor.rowcount
# #             conn.commit()
# #             conn.close()
# #
# #             if rows_affected > 0:
# #                 return True
# #             else:
# #                 print(f"No rows updated. Employee ID {employee_id} may not exist.")
# #                 return False
# #         except sqlite3.Error as e:
# #             print(f"Database error: {e}")
# #             return False
# #
# #
# # # Run this as a standalone script
# # if __name__ == "__main__":
# #     setup = PasswordSetupTool()
# #
# #     print("==== Database Structure Check ====")
# #     setup.check_database_structure()
# #
# #     print("\n==== Adding Password Column ====")
# #     setup.add_password_column()
# #
# #     print("\n==== Available Employees ====")
# #     employees = setup.list_employees()
# #
# #     if employees:
# #         print("Available employees:")
# #         for emp in employees:
# #             # Print available fields (may vary depending on database structure)
# #             print(f"ID: {emp[0]}", end="")
# #             if len(emp) > 1:
# #                 print(f", Name: {emp[1]}", end="")
# #             if len(emp) > 2:
# #                 print(f" {emp[2]}", end="")
# #             if len(emp) > 3:
# #                 print(f", Login: {emp[3]}", end="")
# #             if len(emp) > 4:
# #                 print(f", Role: {emp[4]}", end="")
# #             print()
# #
# #         emp_id = input("\nEnter employee ID to set password: ")
# #         password = input("Enter password: ")
# #         if setup.set_employee_password(emp_id, password):
# #             print("Password set successfully")
# #         else:
# #             print("Failed to set password")
# #     else:
# #         print("No employees found.")
#
# import sqlite3
# import bcrypt
#
# # Connect to the database
# conn = sqlite3.connect("store.db")
# cursor = conn.cursor()
#
# # Fetch all employees
# cursor.execute("SELECT id_employee, password FROM Employee")
# employees = cursor.fetchall()
#
# for id_employee, stored_password in employees:
#     if stored_password:
#         # Check if the password is already a bcrypt hash
#         if not stored_password.startswith('$2b$'):
#             # If the password was hashed with sha256 or is plain text, reset it
#             default_password = "resetme"
#             hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
#             cursor.execute(
#                 "UPDATE Employee SET password = ? WHERE id_employee = ?",
#                 (hashed_password.decode('utf-8'), id_employee)
#             )
#
# # Commit the changes
# conn.commit()
# conn.close()
#
# print("All passwords have been updated to bcrypt hashes. Use 'resetme' as the default password for existing employees.")

import sqlite3
import bcrypt
from DatabaseHelper import DatabaseHelper


def repopulate_employee_table():
    # Initialize DatabaseHelper
    db = DatabaseHelper()

    try:
        # Step 1: Drop the existing Employee table
        db.cursor.execute("DROP TABLE IF EXISTS Employee")
        db.commit()

        # Step 2: Recreate the Employee table with the correct schema
        create_table_query = """
        CREATE TABLE Employee (
            id_employee TEXT PRIMARY KEY,
            surname TEXT NOT NULL,
            name TEXT NOT NULL,
            patronymic TEXT,
            role TEXT NOT NULL,
            salary REAL NOT NULL,
            date_of_birth TEXT NOT NULL,
            date_of_start TEXT NOT NULL,
            address TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
        db.cursor.execute(create_table_query)
        db.commit()

        # Step 3: Define sample employee data
        employees = [
            {
                "id_employee": "E001",
                "surname": "Smith",
                "name": "John",
                "patronymic": "Michael",
                "role": "manager",
                "salary": 50000.0,
                "date_of_birth": "1985-03-15",
                "date_of_start": "2023-01-10",
                "address": "123 Main St, City",
                "password": "manager123"
            },
            {
                "id_employee": "E002",
                "surname": "Johnson",
                "name": "Emily",
                "patronymic": "Anne",
                "role": "cashier",
                "salary": 30000.0,
                "date_of_birth": "1990-07-22",
                "date_of_start": "2023-06-01",
                "address": "456 Oak Ave, Town",
                "password": "cashier123"
            },
            {
                "id_employee": "E003",
                "surname": "Brown",
                "name": "David",
                "patronymic": "Lee",
                "role": "cashier",
                "salary": 32000.0,
                "date_of_birth": "1992-11-30",
                "date_of_start": "2024-01-15",
                "address": "789 Pine Rd, Village",
                "password": "cashier456"
            }
        ]

        # Step 4: Insert employees with bcrypt-hashed passwords
        insert_query = """
        INSERT INTO Employee (id_employee, surname, name, patronymic, role, salary, date_of_birth, date_of_start, address, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for employee in employees:
            # Hash the password with bcrypt
            hashed_password = bcrypt.hashpw(employee["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Prepare the values for insertion
            values = (
                employee["id_employee"],
                employee["surname"],
                employee["name"],
                employee["patronymic"],
                employee["role"],
                employee["salary"],
                employee["date_of_birth"],
                employee["date_of_start"],
                employee["address"],
                hashed_password
            )

            # Insert the employee record
            db.cursor.execute(insert_query, values)

        # Commit the changes
        db.commit()

        print("Employee table has been repopulated successfully with the following employees:")
        for employee in employees:
            print(
                f"- ID: {employee['id_employee']}, Name: {employee['name']} {employee['surname']}, Role: {employee['role']}, Password: {employee['password']}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        db.rollback()

    finally:
        # Close the database connection
        db.close()


if __name__ == "__main__":
    repopulate_employee_table()