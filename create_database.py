import sqlite3
from datetime import datetime

def create_database():
    # Connect to SQLite database
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    # Create tables
    # Category
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Category (
            category_number INTEGER PRIMARY KEY,
            category_name VARCHAR(50) NOT NULL
        )
    ''')

    # Product
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id_product INTEGER PRIMARY KEY,
            category_number INTEGER,
            product_name VARCHAR(50) NOT NULL,
            characteristics VARCHAR(100) NOT NULL,
            FOREIGN KEY (category_number) REFERENCES Category(category_number)
        )
    ''')

    # Store_Product
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Store_Product (
            UPC VARCHAR(12) PRIMARY KEY,
            id_product INTEGER,
            selling_price DECIMAL(13,4) NOT NULL,
            products_number INTEGER NOT NULL,
            promotional_product BOOLEAN NOT NULL,
            FOREIGN KEY (id_product) REFERENCES Product(id_product)
        )
    ''')

    # Employee
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employee (
            id_employee VARCHAR(10) PRIMARY KEY,
            surname VARCHAR(50) NOT NULL,
            name VARCHAR(50) NOT NULL,
            patronymic VARCHAR(50) NOT NULL,
            role VARCHAR(50) NOT NULL,
            salary INTEGER NOT NULL,
            date_of_birth VARCHAR(10) NOT NULL,
            date_of_start VARCHAR(10) NOT NULL,
            address VARCHAR(60) NOT NULL
        )
    ''')

    # Customer_Card
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customer_Card (
            card_number VARCHAR(13) PRIMARY KEY,
            cust_surname VARCHAR(50) NOT NULL,
            cust_name VARCHAR(50) NOT NULL,
            cust_patronymic VARCHAR(50) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            street VARCHAR(50) NOT NULL,
            zip_code VARCHAR(6) NOT NULL,
            percent INTEGER NOT NULL
        )
    ''')

    # Check
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "Check" (
            check_number VARCHAR(10) PRIMARY KEY,
            id_employee VARCHAR(10),
            card_number VARCHAR(13),
            print_date DATETIME NOT NULL,
            sum_total DECIMAL(13,4) NOT NULL,
            FOREIGN KEY (id_employee) REFERENCES Employee(id_employee),
            FOREIGN KEY (card_number) REFERENCES Customer_Card(card_number)
        )
    ''')

    # Sale
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sale (
            UPC VARCHAR(12),
            check_number VARCHAR(10),
            product_number INTEGER NOT NULL,
            selling_price DECIMAL(13,4) NOT NULL,
            PRIMARY KEY (UPC, check_number),
            FOREIGN KEY (UPC) REFERENCES Store_Product(UPC),
            FOREIGN KEY (check_number) REFERENCES "Check"(check_number)
        )
    ''')

    # Insert sample data
    # Category
    cursor.executemany('INSERT OR IGNORE INTO Category (category_number, category_name) VALUES (?, ?)', [
        (1, 'Food'),
        (2, 'Beverages'),
    ])

    # Product
    cursor.executemany('INSERT OR IGNORE INTO Product (id_product, category_number, product_name, characteristics) VALUES (?, ?, ?, ?)', [
        (101, 1, 'Bread', 'Fresh bread'),
        (102, 2, 'Milk', '2% fat'),
    ])

    # Store_Product
    cursor.executemany('INSERT OR IGNORE INTO Store_Product (UPC, id_product, selling_price, products_number, promotional_product) VALUES (?, ?, ?, ?, ?)', [
        ('123456789012', 101, 20.50, 100, 0),
        ('123456789013', 102, 25.00, 50, 1),
    ])

    # Employee
    cursor.executemany('INSERT OR IGNORE INTO Employee (id_employee, surname, name, patronymic, role, salary, date_of_birth, date_of_start, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [
        ('1', 'Ivanov', 'Ivan', 'Ivanovich', 'Cashier', 15000, '1990-01-01', '2020-05-01', 'Kyiv'),
        ('2', 'Petrenko', 'Petro', 'Petrovich', 'Manager', 25000, '1985-03-15', '2018-09-10', 'Lviv'),
        ('3', 'Kovalenko', 'Anna', 'Serhiivna', 'Cashier', 16000, '1995-07-12', '2021-03-15', 'Kyiv'),
        ('4', 'Shevchenko', 'Zoya', 'Oleksandrivna', 'Consultant', 14000, '1992-11-05', '2022-01-10', 'Odesa'),
    ])

    # Customer_Card
    cursor.executemany('INSERT OR IGNORE INTO Customer_Card (card_number, cust_surname, cust_name, cust_patronymic, phone_number, street, zip_code, percent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [
        ('1001', 'Olenova', 'Olena', 'Ivanivna', '0987654321', 'Main St', '65001', 5),
        ('1002', 'Marienko', 'Maria', 'Petrivna', '0976543210', 'Central Ave', '61002', 10),
        ('1003', 'Kovalenko', 'Ihor', 'Serhiiovych', '0965432109', 'Park Rd', '01003', 7),
    ])

    # Check
    cursor.executemany('INSERT OR IGNORE INTO "Check" (check_number, id_employee, card_number, print_date, sum_total) VALUES (?, ?, ?, ?, ?)', [
        ('R001', '1', '1001', '2024-10-01 10:00:00', 100.50),
        ('R002', '3', '1002', '2024-10-02 12:30:00', 75.00),
        ('R003', '1', None, '2024-11-01 09:15:00', 50.00),
    ])

    # Sale
    cursor.executemany('INSERT OR IGNORE INTO Sale (UPC, check_number, product_number, selling_price) VALUES (?, ?, ?, ?)', [
        ('123456789012', 'R001', 2, 20.50),
        ('123456789013', 'R001', 1, 25.00),
        ('123456789013', 'R002', 3, 25.00),
        ('123456789012', 'R003', 1, 20.50),
    ])

    # Commit and close
    conn.commit()
    conn.close()
    print("Database created and populated successfully!")

if __name__ == "__main__":
    create_database()