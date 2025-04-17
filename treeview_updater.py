from datetime import datetime

def update_employee_treeview(self):
    """Update the Працівники Treeview with search and cashier filters"""
    tree = self.treeviews['Працівники']
    tree.delete(*tree.get_children())  # Clear existing rows

    # Get the search term
    search_term = self.search_var.get().lower()
    data = self.mock_data['Працівники']

    # Apply cashier filter
    if self.show_cashiers_only:
        data = [row for row in data if row[4] == 'Касир']

    # Apply search filter (прізвище is index 1)
    if search_term:
        data = [
            row for row in data
            if search_term in row[1].lower()
        ]

    # Insert filtered data
    for row in data:
        tree.insert("", "end", values=row)

def update_customer_treeview(self):
    """Update the Постійні клієнти Treeview with discount percentage filter"""
    tree = self.treeviews['Постійні клієнти']
    tree.delete(*tree.get_children())  # Clear existing rows

    # Get the search term
    search_term = self.customer_search_var.get()
    data = self.mock_data['Постійні клієнти']

    # Apply discount filter (відсоток знижки is index 6)
    if search_term:
        try:
            search_discount = float(search_term)
            data = [
                row for row in data
                if float(row[6].rstrip('%')) >= search_discount
            ]
        except ValueError:
            # If the input is not a valid number, show all data
            pass

    # Insert filtered data
    for row in data:
        tree.insert("", "end", values=row)

def update_product_treeview(self):
    """Update the Продукти Treeview with category ID filter"""
    tree = self.treeviews['Продукти']
    tree.delete(*tree.get_children())  # Clear existing rows

    # Get the search term
    search_term = self.product_search_var.get().lower()
    data = self.mock_data['Продукти']

    # Apply category ID filter (id категорії is index 2)
    if search_term:
        data = [
            row for row in data
            if search_term == row[2].lower()
        ]

    # Insert filtered data
    for row in data:
        tree.insert("", "end", values=row)

def update_store_product_treeview(self):
    """Update the Продукти в магазині Treeview with UPC search and promotional filter"""
    tree = self.treeviews['Продукти в магазині']
    tree.delete(*tree.get_children())  # Clear existing rows

    # Get the search term
    search_term = self.store_product_search_var.get().lower()
    data = self.mock_data['Продукти в магазині']

    # Apply UPC search filter (UPC is index 0)
    if search_term:
        data = [
            row for row in data
            if search_term in row[0].lower()
        ]

    # Apply promotional filter (акційнний товар is index 4)
    if self.show_promotional_only:
        data = [row for row in data if row[4] == 'Так']

    # Join with Продукти to get the name and create display data
    display_data = []
    product_dict = {product[1]: product[0] for product in self.mock_data['Продукти']}  # id продукту -> назва
    for row in data:
        product_id = row[1]
        product_name = product_dict.get(product_id, "Невідомий продукт")
        # New row format: (UPC, id продукту, назва, ціна, наявність, акційнний товар)
        display_row = (row[0], row[1], product_name, row[2], row[3], row[4])
        display_data.append(display_row)

    # Sort based on the selected option
    sort_option = self.promotional_sort_var.get()
    if sort_option == "кількість":
        display_data.sort(key=lambda x: int(x[4]), reverse=True)  # Sort by наявність (index 4)
    elif sort_option == "назва":
        display_data.sort(key=lambda x: x[2])  # Sort by назва (index 2)

    # Insert filtered and sorted data
    for row in display_data:
        tree.insert("", "end", values=row)

def update_receipt_treeview(self):
    """Update the Чеки Treeview with cashier and date range filters"""
    tree = self.treeviews['Чеки']
    tree.delete(*tree.get_children())  # Clear existing rows

    # Get filter values
    cashier_id = self.receipt_cashier_var.get()
    start_date = self.receipt_start_date_var.get()
    end_date = self.receipt_end_date_var.get()

    # Validate dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        start, end = None, None

    # Get receipt data
    data = self.mock_data['Чеки']
    cashier_dict = {worker[0]: f"{worker[1]} {worker[2]}" for worker in self.mock_data['Працівники']}

    # Filter by cashier
    if cashier_id and cashier_id != "Всі касири":
        data = [row for row in data if row[1] == cashier_id]

    # Filter by date range
    filtered_data = []
    for row in data:
        receipt_date = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
        if start and receipt_date < start:
            continue
        if end and receipt_date > end:
            continue
        filtered_data.append(row)

    # Prepare display data with cashier name
    display_data = []
    for row in filtered_data:
        cashier_id = row[1]
        cashier_name = cashier_dict.get(cashier_id, "Невідомий касир")
        display_row = (row[0], cashier_name, row[2], row[3])
        display_data.append(display_row)

    # Insert filtered data
    for row in display_data:
        tree.insert("", "end", values=row)

    # Update reports (totals)
    self.update_receipt_reports()

def update_receipt_reports(self):
    """Update the reports section with total sales and product quantities"""
    # Get filter values
    cashier_id = self.receipt_cashier_var.get()
    start_date = self.receipt_start_date_var.get()
    end_date = self.receipt_end_date_var.get()
    product_upc = self.receipt_product_var.get()

    # Validate dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        start, end = None, None

    # Get receipt data
    receipts = self.mock_data['Чеки']
    receipt_items = self.mock_data['Товари в чеку']

    # Filter receipts by cashier and date range
    filtered_receipts = []
    for receipt in receipts:
        receipt_date = datetime.strptime(receipt[2], '%Y-%m-%d %H:%M:%S')
        if start and receipt_date < start:
            continue
        if end and receipt_date > end:
            continue
        if cashier_id and cashier_id != "Всі касири" and receipt[1] != cashier_id:
            continue
        filtered_receipts.append(receipt)

    # Calculate total sales for specific cashier (Requirement 19)
    total_sales_specific = sum(float(receipt[3]) for receipt in filtered_receipts if cashier_id and cashier_id != "Всі касири")

    # Calculate total sales for all cashiers (Requirement 20)
    total_sales_all = sum(float(receipt[3]) for receipt in filtered_receipts)

    # Calculate total quantity of a specific product sold (Requirement 21)
    total_quantity = 0
    if product_upc:
        for receipt in filtered_receipts:
            receipt_id = receipt[0]
            for item in receipt_items:
                if item[0] == receipt_id and item[1] == product_upc:
                    total_quantity += int(item[2])

    # Update report labels
    self.total_sales_specific_label.config(text=f"Сума (вибраний касир): {total_sales_specific:.2f}")
    self.total_sales_all_label.config(text=f"Сума (всі касири): {total_sales_all:.2f}")
    self.total_quantity_label.config(text=f"Кількість товару (UPC {product_upc or 'не вибрано'}): {total_quantity}")