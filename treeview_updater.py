from datetime import datetime, date


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