from datetime import datetime, date


# Cashier Dashboard Methods (from previous implementation)
def update_cashier_product_treeview(self):
    """Update the Product Treeview with name and category search (Req 1, 4, 5)"""
    tree = self.treeviews['Product']
    tree.delete(*tree.get_children())

    name_search = self.cashier_product_name_var.get().lower()
    category_search = self.cashier_product_category_var.get()

    query = "SELECT id_product, product_name, category_number, characteristics FROM Product"
    conditions = []
    params = []

    if name_search:
        conditions.append("LOWER(product_name) LIKE ?")
        params.append(f"%{name_search}%")
    if category_search:
        conditions.append("category_number = ?")
        params.append(category_search)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY product_name ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_cashier_store_product_treeview(self):
    """Update the Store_Product Treeview with filters and sorting (Req 2, 12, 13, 14)"""
    tree = self.treeviews['Store_Product']
    tree.delete(*tree.get_children())

    search_term = self.cashier_store_product_search_var.get().lower()
    sort_option = self.cashier_promotional_sort_var.get()

    query = '''
        SELECT sp.UPC, sp.id_product, p.product_name, sp.selling_price, sp.products_number, 
               CASE sp.promotional_product WHEN 1 THEN 'Yes' ELSE 'No' END as promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
    '''
    conditions = []
    params = []

    if search_term:
        conditions.append("LOWER(sp.UPC) LIKE ?")
        params.append(f"%{search_term}%")

    if self.cashier_show_promotional_only:
        conditions.append("sp.promotional_product = 1")
    elif self.cashier_show_non_promotional_only:
        conditions.append("sp.promotional_product = 0")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_option == "кількість":
        query += " ORDER BY sp.products_number DESC"
    elif sort_option == "назва":
        query += " ORDER BY p.product_name ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_cashier_customer_treeview(self):
    """Update the Customer_Card Treeview with surname search (Req 3, 6)"""
    tree = self.treeviews['Customer_Card']
    tree.delete(*tree.get_children())

    search_term = self.cashier_customer_search_var.get().lower()

    query = "SELECT card_number, cust_surname, cust_name, cust_patronymic, phone_number, street, zip_code, percent FROM Customer_Card"
    params = []

    if search_term:
        query += " WHERE LOWER(cust_surname) LIKE ?"
        params.append(f"%{search_term}%")

    query += " ORDER BY cust_surname ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_cashier_receipt_treeview(self):
    """Update the Check Treeview for the cashier with date range filters (Req 9, 10)"""
    tree = self.treeviews['Check']
    tree.delete(*tree.get_children())

    start_date = self.cashier_receipt_start_date_var.get()
    end_date = self.cashier_receipt_end_date_var.get()
    today = date.today().strftime('%Y-%m-%d')

    if not start_date and not end_date:
        start_date = today
        end_date = today

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        start, end = None, None

    query = '''
        SELECT c.check_number, (e.surname || ' ' || e.name) as cashier, c.print_date, c.sum_total
        FROM "Check" c
        JOIN Employee e ON c.id_employee = e.id_employee
        WHERE c.id_employee = ?
    '''
    params = [self.cashier_id]

    if start and end:
        query += " AND c.print_date BETWEEN ? AND ?"
        params.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
    elif start:
        query += " AND c.print_date >= ?"
        params.append(start_date + " 00:00:00")
    elif end:
        query += " AND c.print_date <= ?"
        params.append(end_date + " 23:59:59")

    query += " ORDER BY c.print_date DESC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


# Manager Dashboard Methods
def update_employee_treeview(self):
    """Update the Employee Treeview with surname search and cashier filter"""
    tree = self.treeviews['Працівники']
    tree.delete(*tree.get_children())

    search_term = self.search_var.get().lower()

    query = "SELECT id_employee, surname, name, patronymic, role, salary, date_of_birth, date_of_start, address FROM Employee"
    conditions = []
    params = []

    if search_term:
        conditions.append("LOWER(surname) LIKE ?")
        params.append(f"%{search_term}%")

    if self.show_cashiers_only:
        conditions.append("role = 'Cashier'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY surname ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_customer_treeview(self):
    """Update the Customer_Card Treeview with discount percentage filter"""
    tree = self.treeviews['Постійні клієнти']
    tree.delete(*tree.get_children())

    discount_search = self.customer_search_var.get()

    query = "SELECT card_number, cust_surname, cust_name, cust_patronymic, phone_number, street || ', ' || zip_code AS address, percent FROM Customer_Card"
    conditions = []
    params = []

    if discount_search:
        try:
            discount = int(discount_search)
            conditions.append("percent >= ?")
            params.append(discount)
        except ValueError:
            pass  # Ignore invalid input

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY cust_surname ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_product_treeview(self):
    """Update the Product Treeview with category search"""
    tree = self.treeviews['Продукти']
    tree.delete(*tree.get_children())

    category_search = self.product_search_var.get()

    query = "SELECT product_name, id_product, category_number, characteristics FROM Product"
    conditions = []
    params = []

    if category_search:
        conditions.append("category_number = ?")
        params.append(category_search)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY product_name ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_store_product_treeview(self):
    """Update the Store_Product Treeview with UPC search, promotional filter, and sorting"""
    tree = self.treeviews['Продукти в магазині']
    tree.delete(*tree.get_children())

    search_term = self.store_product_search_var.get().lower()
    sort_option = self.promotional_sort_var.get()

    query = '''
        SELECT sp.UPC, sp.id_product, p.product_name, sp.selling_price, sp.products_number, 
               CASE sp.promotional_product WHEN 1 THEN 'Так' ELSE 'Ні' END as promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
    '''
    conditions = []
    params = []

    if search_term:
        conditions.append("LOWER(sp.UPC) LIKE ?")
        params.append(f"%{search_term}%")

    if self.show_promotional_only:
        conditions.append("sp.promotional_product = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_option == "кількість":
        query += " ORDER BY sp.products_number DESC"
    elif sort_option == "назва":
        query += " ORDER BY p.product_name ASC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)


def update_receipt_treeview(self):
    """Update the Check Treeview with cashier and date range filters"""
    tree = self.treeviews['Чеки']
    tree.delete(*tree.get_children())

    cashier_display = self.receipt_cashier_var.get()
    cashier_id = self.cashier_mapping.get(cashier_display, "Всі касири")
    start_date = self.receipt_start_date_var.get()
    end_date = self.receipt_end_date_var.get()
    today = date.today().strftime('%Y-%m-%d')

    if not start_date and not end_date:
        start_date = today
        end_date = today

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        start, end = None, None

    query = '''
        SELECT c.check_number, (e.surname || ' ' || e.name) as cashier, c.print_date, c.sum_total
        FROM "Check" c
        JOIN Employee e ON c.id_employee = e.id_employee
    '''
    conditions = []
    params = []

    if cashier_id != "Всі касири":
        conditions.append("c.id_employee = ?")
        params.append(cashier_id)

    if start and end:
        conditions.append("c.print_date BETWEEN ? AND ?")
        params.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
    elif start:
        conditions.append("c.print_date >= ?")
        params.append(start_date + " 00:00:00")
    elif end:
        conditions.append("c.print_date <= ?")
        params.append(end_date + " 23:59:59")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY c.print_date DESC"

    data = self.db.fetch_filtered(query, params)

    for row in data:
        tree.insert("", "end", values=row)

    # Update the reports after updating the treeview
    self.update_receipt_reports()


def update_receipt_reports(self):
    """Update the sales and quantity reports in the Check tab"""
    cashier_display = self.receipt_cashier_var.get()
    cashier_id = self.cashier_mapping.get(cashier_display, "Всі касири")
    start_date = self.receipt_start_date_var.get()
    end_date = self.receipt_end_date_var.get()
    upc = self.receipt_product_var.get()
    today = date.today().strftime('%Y-%m-%d')

    if not start_date and not end_date:
        start_date = today
        end_date = today

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        start, end = None, None

    # Calculate total sales for the selected cashier
    query_specific = '''
        SELECT SUM(c.sum_total)
        FROM "Check" c
        JOIN Employee e ON c.id_employee = e.id_employee
    '''
    conditions_specific = []
    params_specific = []

    if cashier_id != "Всі касири":
        conditions_specific.append("c.id_employee = ?")
        params_specific.append(cashier_id)

    if start and end:
        conditions_specific.append("c.print_date BETWEEN ? AND ?")
        params_specific.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
    elif start:
        conditions_specific.append("c.print_date >= ?")
        params_specific.append(start_date + " 00:00:00")
    elif end:
        conditions_specific.append("c.print_date <= ?")
        params_specific.append(end_date + " 23:59:59")

    if conditions_specific:
        query_specific += " WHERE " + " AND ".join(conditions_specific)

    result = self.db.fetch_filtered(query_specific, params_specific)
    total_specific = result[0][0] or 0.0
    self.total_sales_specific_label.config(text=f"Сума (вибраний касир): {total_specific:.2f}")

    # Calculate total sales for all cashiers
    query_all = '''
        SELECT SUM(c.sum_total)
        FROM "Check" c
    '''
    conditions_all = []
    params_all = []

    if start and end:
        conditions_all.append("c.print_date BETWEEN ? AND ?")
        params_all.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
    elif start:
        conditions_all.append("c.print_date >= ?")
        params_all.append(start_date + " 00:00:00")
    elif end:
        conditions_all.append("c.print_date <= ?")
        params_all.append(end_date + " 23:59:59")

    if conditions_all:
        query_all += " WHERE " + " AND ".join(conditions_all)

    result = self.db.fetch_filtered(query_all, params_all)
    total_all = result[0][0] or 0.0
    self.total_sales_all_label.config(text=f"Сума (всі касири): {total_all:.2f}")

    # Calculate total quantity for the selected UPC
    if upc:
        query_quantity = '''
            SELECT SUM(sOral

            SELECT SUM(s.product_number)
            FROM Sale s
            JOIN "Check" c ON s.check_number = c.check_number
        '''
        conditions_quantity = ["s.UPC = ?"]
        params_quantity = [upc]

        if start and end:
            conditions_quantity.append("c.print_date BETWEEN ? AND ?")
            params_quantity.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
        elif start:
            conditions_quantity.append("c.print_date >= ?")
            params_quantity.append(start_date + " 00:00:00")
        elif end:
            conditions_quantity.append("c.print_date <= ?")
            params_quantity.append(end_date + " 23:59:59")

        query_quantity += " WHERE " + " AND ".join(conditions_quantity)
        result = self.db.fetch_filtered(query_quantity, params_quantity)
        total_quantity = result[0][0] or 0
        self.total_quantity_label.config(text=f"Кількість товару ({upc}): {total_quantity}")
    else:
        self.total_quantity_label.config(text="Кількість товару (UPC не вибрано): 0")