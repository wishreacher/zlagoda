import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# Mapping of tab names to database table names
TABLE_MAPPING = {
    'Продукти': 'Product',
    'Продукти в магазині': 'Store_Product',
    'Категорії': 'Category',
    'Працівники': 'Employee',
    'Постійні клієнти': 'Customer_Card',
    'Чеки': 'Check'
}

# Mapping of Ukrainian labels to database column names for each tab
COLUMN_MAPPING = {
    'Продукти': {
        'назва': 'product_name',
        'id продукту': 'id_product',
        'id категорії': 'category_number',
        'Опис': 'characteristics'
    },
    'Продукти в магазині': {
        'UPC': 'UPC',
        'id продукту': 'id_product',
        'назва': 'product_name',  # This is fetched via JOIN
        'ціна': 'selling_price',
        'наявність': 'products_number',
        'акційнний товар': 'promotional_product'
    },
    'Категорії': {
        'назва': 'category_name',
        'номер категорії': 'category_number'
    },
    'Працівники': {
        'id працівника': 'id_employee',
        'прізвище': 'surname',
        'імʼя': 'name',
        'по-батькові': 'patronymic',
        'посада': 'role',
        'зарплата': 'salary',
        'дата народження': 'date_of_birth',
        'дата початку': 'date_of_start',
        'адреса': 'address'
    },
    'Постійні клієнти': {
        'номер картки': 'card_number',
        'прізвище': 'cust_surname',
        'імʼя': 'cust_name',
        'по-батькові': 'cust_patronymic',
        'номер телефону': 'phone_number',
        'адреса': 'street',  # Will concatenate with zip_code in UI
        'відсоток знижки': 'percent'
    },
    'Чеки': {
        'номер чеку': 'check_number',
        'касир': 'cashier',  # This is computed in the query
        'дата': 'print_date',
        'загальна сума': 'sum_total'
    }
}

def add_new_item(self, tab_name):
    """Handle adding a new item to the specified tab"""
    columns = self.entity_columns[tab_name]
    values = {}

    dialog = tk.Toplevel(self.root)
    dialog.title(f"Add New Record - {tab_name}")
    dialog.geometry("400x500")
    dialog.transient(self.root)
    dialog.grab_set()

    for i, col in enumerate(columns):
        label = tk.Label(dialog, text=f"{col}:", anchor="w")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(dialog, font=("Space Mono", 12), width=25)
        entry.grid(row=i, column=1, padx=10, pady=5)
        values[col] = entry

    def save_item():
        # Map UI labels to database columns
        db_columns = [COLUMN_MAPPING[tab_name][col] for col in columns]
        new_values = tuple(entry.get() for entry in values.values())

        # Special handling for certain fields
        processed_values = []
        for col, val in zip(columns, new_values):
            if tab_name == 'Продукти в магазині' and col == 'акційнний товар':
                processed_values.append(1 if val.lower() in ['так', 'yes'] else 0)
            else:
                processed_values.append(val)

        table_name = TABLE_MAPPING[tab_name]
        placeholders = ', '.join(['?' for _ in processed_values])
        query = f'INSERT INTO "{table_name}" ({", ".join(db_columns)}) VALUES ({placeholders})'

        self.db.begin_transaction()
        try:
            self.db.execute_query(query, processed_values)
            self.db.commit_transaction()
        except Exception as e:
            self.db.rollback_transaction()
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
            return

        # Update the corresponding treeview
        if tab_name == 'Працівники':
            self.update_employee_treeview()
        elif tab_name == 'Постійні клієнти':
            self.update_customer_treeview()
        elif tab_name == 'Продукти':
            self.update_product_treeview()
        elif tab_name == 'Продукти в магазині':
            self.update_store_product_treeview()

        dialog.destroy()

    save_button = tk.Button(dialog, text="Save", font=("Space Mono", 12), command=save_item)
    save_button.grid(row=len(columns), column=0, columnspan=2, pady=20)

    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

def delete_selected_item(self, tab_name):
    """Delete the selected item from the treeview"""
    tree = self.treeviews[tab_name]
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showinfo("Information", "Please select an item to delete")
        return

    item_values = tree.item(selected_item, 'values')
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this record?\n\n{item_values}")

    if confirm:
        table_name = TABLE_MAPPING[tab_name]
        pk_column = COLUMN_MAPPING[tab_name][self.entity_columns[tab_name][0]]  # First column is the primary key
        pk_value = item_values[0]

        query = f"DELETE FROM \"{table_name}\" WHERE {pk_column} = ?"

        self.db.begin_transaction()
        try:
            self.db.execute_query(query, (pk_value,))
            self.db.commit_transaction()
        except Exception as e:
            self.db.rollback_transaction()
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
            return

        tree.delete(selected_item)

        # Update the corresponding treeview
        if tab_name == 'Працівники':
            self.update_employee_treeview()
        elif tab_name == 'Постійні клієнти':
            self.update_customer_treeview()
        elif tab_name == 'Продукти':
            self.update_product_treeview()
        elif tab_name == 'Продукти в магазині':
            self.update_store_product_treeview()

def on_cell_double_click(self, event, tab_name):
    """Handle double-click on a cell to edit its value or view receipt details"""
    tree = self.treeviews[tab_name]
    region = tree.identify("region", event.x, event.y)
    if region != "cell":
        return

    if tab_name == 'Чеки':
        selected_item = tree.selection()
        if not selected_item:
            return
        check_number = tree.item(selected_item, 'values')[0]
        self.show_receipt_items(check_number)
        return

    column = tree.identify_column(event.x)
    item = tree.identify_row(event.y)
    if not item:
        return

    column_index = int(column.replace('#', '')) - 1
    columns = self.entity_columns[tab_name]
    if column_index >= len(columns):
        return
    column_name = columns[column_index]

    current_value = tree.item(item, 'values')[column_index]

    edit_dialog = tk.Toplevel(self.root)
    edit_dialog.title(f"Edit {column_name}")
    edit_dialog.geometry("300x150")
    edit_dialog.transient(self.root)
    edit_dialog.grab_set()

    label = tk.Label(edit_dialog, text=f"Edit {column_name}:")
    label.pack(pady=(20, 10))
    entry = tk.Entry(edit_dialog, font=("Space Mono", 12), width=25)
    entry.insert(0, current_value)
    entry.pack(pady=10)
    entry.select_range(0, tk.END)
    entry.focus_set()

    def save_edit():
        new_value = entry.get()
        if new_value != current_value:
            values = list(tree.item(item, 'values'))
            values[column_index] = new_value

            table_name = TABLE_MAPPING[tab_name]
            db_column = COLUMN_MAPPING[tab_name][column_name]
            pk_column = COLUMN_MAPPING[tab_name][columns[0]]
            pk_value = values[0]

            # Special handling for certain fields
            if tab_name == 'Продукти в магазині' and column_name == 'акційнний товар':
                new_value = 1 if new_value.lower() in ['так', 'yes'] else 0
                values[column_index] = 'Так' if new_value == 1 else 'Ні'

            query = f"UPDATE \"{table_name}\" SET {db_column} = ? WHERE {pk_column} = ?"

            self.db.begin_transaction()
            try:
                self.db.execute_query(query, (new_value, pk_value))
                self.db.commit_transaction()
            except Exception as e:
                self.db.rollback_transaction()
                messagebox.showerror("Error", f"Failed to update item: {str(e)}")
                return

            tree.item(item, values=values)

            # Update the corresponding treeview
            if tab_name == 'Працівники':
                self.update_employee_treeview()
            elif tab_name == 'Постійні клієнти':
                self.update_customer_treeview()
            elif tab_name == 'Продукти':
                self.update_product_treeview()
            elif tab_name == 'Продукти в магазині':
                self.update_store_product_treeview()

        edit_dialog.destroy()

    save_button = tk.Button(edit_dialog, text="Save", font=("Space Mono", 12), command=save_edit)
    save_button.pack(pady=10)

    edit_dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (edit_dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (edit_dialog.winfo_height() // 2)
    edit_dialog.geometry(f"+{x}+{y}")
    entry.bind("<Return>", lambda event: save_edit())

def show_receipt_items(self, check_number):
    """Show the purchased items in a specific check"""
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Items in Check {check_number}")
    dialog.geometry("600x400")
    dialog.transient(self.root)
    dialog.grab_set()

    tree_frame = tk.Frame(dialog)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

    columns = ('product_name', 'UPC', 'quantity', 'selling_price', 'total_price')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    v_scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    h_scrollbar = tk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    tree.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    query = '''
        SELECT p.product_name, s.UPC, s.product_number, s.selling_price, (s.product_number * s.selling_price) as total_price
        FROM Sale s
        JOIN Store_Product sp ON s.UPC = sp.UPC
        JOIN Product p ON sp.id_product = p.id_product
        WHERE s.check_number = ?
    '''
    items = self.db.fetch_filtered(query, (check_number,))

    for item in items:
        tree.insert("", "end", values=item)

    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

def sell_products(self):
    """Handle product sales by creating a new check (Req 7)"""
    dialog = tk.Toplevel(self.root)
    dialog.title("Sell Products")
    dialog.geometry("600x600")
    dialog.transient(self.root)
    dialog.grab_set()

    customer_frame = tk.Frame(dialog)
    customer_frame.pack(fill='x', padx=10, pady=(10, 5))

    customer_label = tk.Label(customer_frame, text="Customer (card_number):")
    customer_label.pack(side='left', padx=(5, 0))
    customer_var = tk.StringVar()
    customers = self.db.fetch_all('Customer_Card')
    customer_options = [""] + [customer[0] for customer in customers]
    customer_menu = ttk.OptionMenu(customer_frame, customer_var, customer_options[0], *customer_options)
    customer_menu.pack(side='left', padx=(5, 10))

    products_frame = tk.Frame(dialog)
    products_frame.pack(fill='both', expand=True, padx=10, pady=5)

    product_entries = []

    def add_product_entry():
        entry_frame = tk.Frame(products_frame)
        entry_frame.pack(fill='x', pady=2)

        upc_label = tk.Label(entry_frame, text="UPC:")
        upc_label.pack(side='left', padx=(5, 0))
        upc_entry = tk.Entry(entry_frame, font=("Space Mono", 12), width=15)
        upc_entry.pack(side='left', padx=(5, 5))

        qty_label = tk.Label(entry_frame, text="Quantity:")
        qty_label.pack(side='left', padx=(5, 0))
        qty_entry = tk.Entry(entry_frame, font=("Space Mono", 12), width=5)
        qty_entry.pack(side='left', padx=(5, 5))

        product_entries.append((entry_frame, upc_entry, qty_entry))

    add_product_button = tk.Button(dialog, text="+ Add Product", font=("Space Mono", 12), command=add_product_entry)
    add_product_button.pack(pady=5)

    add_product_entry()

    total_frame = tk.Frame(dialog)
    total_frame.pack(fill='x', padx=10, pady=5)
    total_label = tk.Label(total_frame, text="Total Amount: 0.00")
    total_label.pack()

    def update_total():
        total = 0.0
        for _, upc_entry, qty_entry in product_entries:
            upc = upc_entry.get()
            qty = qty_entry.get()
            if upc and qty:
                try:
                    qty = int(qty)
                    info = self.db.get_product_info(upc)
                    if info:
                        price, _ = info
                        total += price * qty
                except ValueError:
                    pass
        card_number = customer_var.get()
        if card_number:
            discount = self.db.get_customer_discount(card_number)
            if discount:
                total = total * (1 - discount / 100)
        total_label.config(text=f"Total Amount: {total:.2f}")

    for _, upc_entry, qty_entry in product_entries:
        upc_entry.bind("<KeyRelease>", lambda e: update_total())
        qty_entry.bind("<KeyRelease>", lambda e: update_total())
    customer_var.trace("w", lambda *args: update_total())

    def save_sale():
        # Aggregate items by UPC to avoid UNIQUE constraint violation
        items_dict = {}  # Dictionary to store UPC: (total_qty, price)

        for _, upc_entry, qty_entry in product_entries:
            upc = upc_entry.get()
            qty = qty_entry.get()
            if not upc or not qty:
                continue
            try:
                qty = int(qty)
                if qty <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
                info = self.db.get_product_info(upc)
                if not info:
                    messagebox.showerror("Error", f"Product with UPC {upc} not found")
                    return
                price, available = info
                if upc in items_dict:
                    items_dict[upc] = (items_dict[upc][0] + qty, price)
                else:
                    items_dict[upc] = (qty, price)
                # Check total quantity for this UPC against available stock
                total_qty = items_dict[upc][0]
                if total_qty > available:
                    messagebox.showerror("Error", f"Not enough stock for UPC {upc}. Available: {available}")
                    return
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number")
                return

        if not items_dict:
            messagebox.showerror("Error", "Add at least one product")
            return

        # Calculate total amount
        total = sum(qty * price for qty, price in items_dict.values())
        card_number = customer_var.get()
        if card_number:
            discount = self.db.get_customer_discount(card_number)
            if discount:
                total = total * (1 - discount / 100)

        new_id_num = self.db.get_max_receipt_id() + 1
        check_number = f"R{new_id_num:03d}"
        print_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Begin a transaction
        self.db.begin_transaction()
        try:
            # Insert into Check
            self.db.execute_query(
                'INSERT INTO "Check" (check_number, id_employee, card_number, print_date, sum_total) VALUES (?, ?, ?, ?, ?)',
                (check_number, self.cashier_id, card_number if card_number else None, print_date, total)
            )

            # Insert aggregated items into Sale
            for upc, (qty, price) in items_dict.items():
                self.db.execute_query(
                    "INSERT INTO Sale (UPC, check_number, product_number, selling_price) VALUES (?, ?, ?, ?)",
                    (upc, check_number, qty, price)
                )

            # Update product quantities
            for upc, (qty, _) in items_dict.items():
                self.db.execute_query(
                    "UPDATE Store_Product SET products_number = products_number - ? WHERE UPC = ?",
                    (qty, upc)
                )

            # Commit the transaction
            self.db.commit_transaction()
        except Exception as e:
            # Rollback on error
            self.db.rollback_transaction()
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
            return

        self.update_cashier_store_product_treeview()
        self.update_cashier_receipt_treeview()

        dialog.destroy()
        messagebox.showinfo("Success", f"Sale completed! Check Number: {check_number}")

    save_button = tk.Button(dialog, text="Complete Sale", font=("Space Mono", 12), command=save_sale)
    save_button.pack(pady=10)

    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")