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