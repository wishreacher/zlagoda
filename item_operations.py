import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import bcrypt  # Added for password hashing

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
        'адреса': 'address',
        'пароль': 'password'
    },
    'Постійні клієнти': {
        'номер картки': 'card_number',
        'прізвище': 'cust_surname',
        'імʼя': 'cust_name',
        'по-батькові': 'cust_patronymic',
        'номер телефона': 'phone_number',
        'адреса': 'street',
        'індекс': 'zip_code',
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
    dialog.title(f"Додати новий запис - {tab_name}")
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
        # Перевірка назви вкладки (враховуємо можливі варіанти написання)
        if tab_name in ['Продукти у магазині', 'Продукти в магазині']:
            product_name = values['назва'].get()
            if not product_name:
                messagebox.showerror("Помилка", "Поле 'назва' є обов’язковим.")
                return

            # Знайти id_product за назвою
            product = self.db.fetch_filtered("SELECT id_product FROM Product WHERE product_name = ?", (product_name,))
            if not product:
                messagebox.showerror("Помилка", f"Продукт з назвою '{product_name}' не знайдено.")
                return
            id_product = product[0][0]

            # Виключити 'назва' із даних для вставки
            columns_to_insert = [col for col in columns if col != 'назва']
            db_columns = []
            new_values = []
            for col in columns_to_insert:
                if col in COLUMN_MAPPING[tab_name]:
                    db_columns.append(COLUMN_MAPPING[tab_name][col])
                    if col == 'ID продукта':
                        new_values.append(id_product)
                    else:
                        new_values.append(values[col].get())
                else:
                    messagebox.showerror("Помилка", f"Невідоме поле: {col}")
                    return

        else:
            # Для інших вкладок (наприклад, Постійні клієнти)
            db_columns = []
            new_values = []
            for col in columns:
                if col in COLUMN_MAPPING[tab_name]:
                    db_columns.append(COLUMN_MAPPING[tab_name][col])
                    new_values.append(values[col].get())
                else:
                    messagebox.showerror("Помилка", f"Невідоме поле: {col}")
                    return

        table_name = TABLE_MAPPING[tab_name]
        placeholders = ', '.join(['?' for _ in new_values])
        query = f'INSERT INTO "{table_name}" ({", ".join(db_columns)}) VALUES ({placeholders})'

        self.db.begin_transaction()
        try:
            self.db.execute_query(query, tuple(new_values))
            self.db.commit_transaction()
            if tab_name in ['Продукти у магазині', 'Продукти в магазині']:
                self.update_cashier_store_product_treeview()
            elif tab_name == 'Постійні клієнти':
                self.update_cashier_customer_treeview()
            dialog.destroy()
            messagebox.showinfo("Успіх", f"Дані успішно додані до {tab_name}!")
        except Exception as e:
            self.db.rollback_transaction()
            messagebox.showerror("Помилка", f"Не вдалося додати запис: {str(e)}")

    save_button = tk.Button(dialog, text="Зберегти", font=("Space Mono", 12), command=save_item)
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
        messagebox.showinfo("Попередження", "Виберіть запис для видалення.")
        return

    item_values = tree.item(selected_item, 'values')
    confirm = messagebox.askyesno("Підтвердіть видалення", f"Ви хочете видалити цей запис?\n\n{item_values}")

    if confirm:
        table_name = TABLE_MAPPING[tab_name]
        pk_column = COLUMN_MAPPING[tab_name][self.entity_columns[tab_name][0]]
        pk_value = item_values[0]

        query = f"DELETE FROM \"{table_name}\" WHERE {pk_column} = ?"

        self.db.begin_transaction()
        try:
            self.db.execute_query(query, (pk_value,))
            self.db.commit_transaction()
        except Exception as e:
            self.db.rollback_transaction()
            messagebox.showerror("Помилка", f"Не вдалося видалити запис: {str(e)}")
            return

        tree.delete(selected_item)

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

    columns = self.entity_columns[tab_name]
    column_index = int(column.replace('#', '')) - 1
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
    if tab_name == 'Працівники' and column_name == 'пароль':
        entry = tk.Entry(edit_dialog, font=("Space Mono", 12), width=25, show="*")
        entry.insert(0, "")  # Do not display the hashed password
    else:
        entry = tk.Entry(edit_dialog, font=("Space Mono", 12), width=25)
        entry.insert(0, current_value)
    entry.pack(pady=10)
    entry.select_range(0, tk.END)
    entry.focus_set()

    def save_edit():
        new_value = entry.get()
        if new_value != ("" if tab_name == 'Працівники' and column_name == 'пароль' else current_value):
            if tab_name == 'Працівники' and column_name == 'пароль' and not new_value:
                messagebox.showerror("Помилка", "Пароль не може бути порожнім.")
                return

            values = list(tree.item(item, 'values'))
            if tab_name == 'Працівники' and column_name == 'пароль':
                hashed_password = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt())
                new_value = hashed_password.decode('utf-8')
                values[column_index] = "********"  # Display placeholder in UI
            else:
                values[column_index] = new_value

            table_name = TABLE_MAPPING[tab_name]
            db_column = COLUMN_MAPPING[tab_name][column_name]
            pk_column = COLUMN_MAPPING[tab_name][columns[0]]
            pk_value = values[0]

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
                messagebox.showerror("Помилка", f"Не вдалося оновити запис: {str(e)}")
                return

            tree.item(item, values=values)

            if tab_name == 'Працівники':
                self.update_employee_treeview()
            elif tab_name == 'Постійні клієнти':
                self.update_customer_treeview()
            elif tab_name == 'Продукти':
                self.update_product_treeview()
            elif tab_name == 'Продукти в магазині':
                self.update_store_product_treeview()

        edit_dialog.destroy()

    save_button = tk.Button(edit_dialog, text="Зберегти", font=("Space Mono", 12), command=save_edit)
    save_button.pack(pady=10)

    edit_dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (edit_dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (edit_dialog.winfo_height() // 2)
    edit_dialog.geometry(f"+{x}+{y}")
    entry.bind("<Return>", lambda event: save_edit())

def show_receipt_items(self, check_number):
    """Show the purchased items in a specific check"""
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Товари в чеку {check_number}")
    dialog.geometry("600x400")
    dialog.transient(self.root)
    dialog.grab_set()

    tree_frame = tk.Frame(dialog)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

    columns = ('назва', 'UPC', 'кількість', 'ціна', 'сума')
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
    """Handle product sales with VAT, promotional discounts, and customer discounts"""
    dialog = tk.Toplevel(self.root)
    dialog.title("Продажі")
    dialog.geometry("800x600")
    dialog.transient(self.root)
    dialog.grab_set()

    customer_frame = tk.Frame(dialog)
    customer_frame.pack(fill='x', padx=10, pady=(10, 5))

    customer_label = tk.Label(customer_frame, text="Пошук за номером картки:")
    customer_label.pack(side='left', padx=(5, 0))
    customer_var = tk.StringVar()
    customers = self.db.fetch_all('Customer_Card')
    customer_options = [""] + [customer[0] for customer in customers]
    customer_menu = ttk.OptionMenu(customer_frame, customer_var, customer_options[0], *customer_options)
    customer_menu.pack(side='left', padx=(5, 10))

    products_frame = tk.Frame(dialog)
    products_frame.pack(fill='both', expand=True, padx=10, pady=5)

    product_entries = []

    products = self.db.fetch_filtered(
        "SELECT p.product_name, sp.UPC, sp.products_number, sp.selling_price FROM Product p JOIN Store_Product sp ON p.id_product = sp.id_product")
    product_names = [row[0] for row in products]
    product_dict = {row[0]: {'upc': row[1], 'stock': row[2], 'price': row[3]} for row in products}
    upc_dict = {row[1]: {'name': row[0], 'stock': row[2], 'price': row[3]} for row in products}

    def add_product_entry():
        entry_frame = tk.Frame(products_frame)
        entry_frame.pack(fill='x', pady=2)

        upc_var = tk.StringVar()
        product_name_var = tk.StringVar()
        qty_var = tk.StringVar()
        available_qty_var = tk.StringVar(value="/0")

        def update_fields_from_product(event=None):
            product_name = product_name_var.get()
            if product_name in product_dict:
                upc_var.set(product_dict[product_name]['upc'])
                available_qty_var.set(f"/{product_dict[product_name]['stock']}")
            else:
                upc_var.set("")
                available_qty_var.set("/0")
            update_total()

        def update_fields_from_upc(event=None):
            upc = upc_var.get()
            if upc in upc_dict:
                product_name_var.set(upc_dict[upc]['name'])
                available_qty_var.set(f"/{upc_dict[upc]['stock']}")
            else:
                product_name_var.set("")
                available_qty_var.set("/0")
            update_total()

        upc_label = tk.Label(entry_frame, text="UPC:")
        upc_label.pack(side='left', padx=(5, 0))
        upc_entry = tk.Entry(entry_frame, textvariable=upc_var, font=("Space Mono", 12), width=15)
        upc_entry.pack(side='left', padx=(5, 5))
        upc_entry.bind("<KeyRelease>", update_fields_from_upc)

        product_label = tk.Label(entry_frame, text="Product:")
        product_label.pack(side='left', padx=(5, 0))
        product_combobox = ttk.Combobox(entry_frame, textvariable=product_name_var, values=product_names,
                                        font=("Space Mono", 12), width=20)
        product_combobox.pack(side='left', padx=(5, 5))
        product_combobox.bind("<<ComboboxSelected>>", update_fields_from_product)

        qty_label = tk.Label(entry_frame, text="Quantity:")
        qty_label.pack(side='left', padx=(5, 0))
        qty_entry = tk.Entry(entry_frame, textvariable=qty_var, font=("Space Mono", 12), width=5)
        qty_entry.pack(side='left', padx=(5, 0))
        tk.Label(entry_frame, textvariable=available_qty_var, font=("Space Mono", 12)).pack(side='left', padx=(0, 5))

        def delete_entry():
            product_entries.remove((entry_frame, upc_entry, qty_entry))
            entry_frame.destroy()
            update_total()

        delete_button = tk.Button(entry_frame, text="x", font=("Space Mono", 12), width=2, command=delete_entry)
        delete_button.pack(side='left', padx=(5, 0))

        product_entries.append((entry_frame, upc_entry, qty_entry))

        qty_entry.bind("<KeyRelease>", lambda e: update_total())

    add_product_button = tk.Button(dialog, text="+ Add Product", font=("Space Mono", 12), command=add_product_entry)
    add_product_button.pack(pady=5)

    add_product_entry()

    total_frame = tk.Frame(dialog)
    total_frame.pack(fill='x', padx=10, pady=5)
    total_label = tk.Label(total_frame, text=" Сума включно з ПДВ: 0.00")
    total_label.pack()

    def calculate_product_total(upc, qty):
        info = self.db.get_product_info(upc)
        if not info:
            return 0.0
        price, _ = info
        promotional = self.db.fetch_filtered("SELECT promotional_product FROM Store_Product WHERE UPC = ?", (upc,))[0][0]

        if promotional:
            price = price * 0.80
        price_with_vat = price * 1.20
        return qty * price_with_vat

    def update_total():
        total = 0.0
        for _, upc_entry, qty_entry in product_entries:
            upc = upc_entry.get()
            qty = qty_entry.get()
            if upc and qty:
                try:
                    qty = int(qty)
                    total += calculate_product_total(upc, qty)
                except ValueError:
                    pass
        card_number = customer_var.get()
        if card_number:
            discount = self.db.get_customer_discount(card_number)
            if discount:
                total = total * (1 - discount / 100)
        total_label.config(text=f"Сума включно з ПДВ: {total:.2f}")

    customer_var.trace("w", lambda *args: update_total())

    def save_sale():
        items_dict = {}
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
                total_qty = items_dict[upc][0]
                if total_qty > available:
                    messagebox.showerror("Помилка", f"Недостатньо у наявності для UPC {upc}. У наявності: {available}")
                    return
            except ValueError:
                messagebox.showerror("Помилка", "Кількість має бути числом")
                return
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка обробки UPC {upc}: {str(e)}")
                return

        if not items_dict:
            messagebox.showerror("Помилка", "Додайте хочаб один продукт")
            return

        total = 0.0
        for upc, (qty, price) in items_dict.items():
            total += calculate_product_total(upc, qty)
        card_number = customer_var.get()
        if card_number:
            discount = self.db.get_customer_discount(card_number)
            if discount:
                total = total * (1 - discount / 100)

        new_id_num = self.db.get_max_receipt_id() + 1
        check_number = f"R{new_id_num:03d}"
        print_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            self.db.execute_query(
                'INSERT INTO "Check" (check_number, id_employee, card_number, print_date, sum_total) VALUES (?, ?, ?, ?, ?)',
                (check_number, self.cashier_id, card_number if card_number else None, print_date, total)
            )

            for upc, (qty, price) in items_dict.items():
                self.db.execute_query(
                    "INSERT INTO Sale (UPC, check_number, product_number, selling_price) VALUES (?, ?, ?, ?)",
                    (upc, check_number, qty, price)
                )

            for upc, (qty, _) in items_dict.items():
                self.db.execute_query(
                    "UPDATE Store_Product SET products_number = products_number - ? WHERE UPC = ?",
                    (qty, upc)
                )

            self.db.commit_transaction()
        except Exception as e:
            self.db.rollback_transaction()
            messagebox.showerror("Помилка", f"Не вийшло завершити продаж: {str(e)}")
            return

        self.update_cashier_store_product_treeview()
        self.update_cashier_receipt_treeview()

        dialog.destroy()
        messagebox.showinfo("Ура!", f"Продукт продано! Номер чеку: {check_number}")

    save_button = tk.Button(dialog, text="Продати", font=("Space Mono", 12), command=save_sale)
    save_button.pack(pady=10)

    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")