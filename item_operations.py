import tkinter as tk
from tkinter import messagebox, ttk

def add_new_item(self, tab_name):
    """Handle adding a new item to the specified tab"""
    # Get the columns for this tab
    columns = self.entity_columns[tab_name]

    # Create a dictionary to store the values
    values = {}

    # Create a new dialog window
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Додати новий запис - {tab_name}")
    dialog.geometry("400x500")
    dialog.transient(self.root)  # Make dialog modal
    dialog.grab_set()

    # Create entry fields for each column
    for i, col in enumerate(columns):
        # Label for the field
        label = tk.Label(dialog, text=f"{col}:", anchor="w")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

        # Entry field
        entry = tk.Entry(dialog, font=("Space Mono", 12), width=25)
        entry.grid(row=i, column=1, padx=10, pady=5)

        # Store the entry widget in the values dictionary
        values[col] = entry

    # Function to save the new item
    def save_item():
        # Get values from all entry fields
        new_values = tuple(entry.get() for entry in values.values())

        # Adjust for Продукти в магазині (exclude назва since it's derived)
        if tab_name == 'Продукти в магазині':
            new_values = (new_values[0], new_values[1], new_values[3], new_values[4], new_values[5])

        # Add the new item to the mock data
        self.mock_data[tab_name].append(new_values)

        # Sort the mock data if it's Працівники, Постійні клієнти, Категорії, Продукти, or Продукти в магазині
        if tab_name in ['Працівники', 'Постійні клієнти', 'Категорії', 'Продукти', 'Продукти в магазині']:
            if tab_name == 'Категорії' or tab_name == 'Продукти':
                self.mock_data[tab_name].sort(key=lambda x: x[0])
            elif tab_name == 'Продукти в магазині':
                self.mock_data[tab_name].sort(key=lambda x: int(x[3]), reverse=True)
            else:
                self.mock_data[tab_name].sort(key=lambda x: x[1])

        # Update the Treeview
        if tab_name == 'Працівники':
            self.update_employee_treeview()
        elif tab_name == 'Постійні клієнти':
            self.update_customer_treeview()
        elif tab_name == 'Продукти':
            self.update_product_treeview()
        elif tab_name == 'Продукти в магазині':
            self.update_store_product_treeview()
        else:
            tree = self.treeviews[tab_name]
            tree.delete(*tree.get_children())  # Clear existing rows
            data = self.mock_data[tab_name]
            for row in data:
                tree.insert("", "end", values=row)

        # Close the dialog
        dialog.destroy()

    # Add save button
    save_button = tk.Button(
        dialog,
        text="Зберегти",
        font=("Space Mono", 12),
        command=save_item
    )
    save_button.grid(row=len(columns), column=0, columnspan=2, pady=20)

    # Center the dialog on the parent window
    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

def delete_selected_item(self, tab_name):
    """Delete the selected item from the treeview"""
    tree = self.treeviews[tab_name]
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showinfo("Інформація", "Виберіть елемент для видалення")
        return

    # Get the values of the selected item to find it in the mock data
    item_values = tree.item(selected_item, 'values')

    # Ask for confirmation
    confirm = messagebox.askyesno(
        "Підтвердження видалення",
        f"Ви впевнені, що хочете видалити цей запис?\n\n{item_values}"
    )

    if confirm:
        # Remove from treeview
        tree.delete(selected_item)

        # Adjust for Продукти в магазині (exclude назва)
        if tab_name == 'Продукти в магазині':
            item_values = (item_values[0], item_values[1], item_values[3], item_values[4], item_values[5])

        # Remove from mock data
        item_values_tuple = tuple(item_values)
        if item_values_tuple in self.mock_data[tab_name]:
            self.mock_data[tab_name].remove(item_values_tuple)

        # Sort the mock data if it's Працівники, Постійні клієнти, Категорії, Продукти, or Продукти в магазині
        if tab_name in ['Працівники', 'Постійні клієнти', 'Категорії', 'Продукти', 'Продукти в магазині']:
            if tab_name == 'Категорії' or tab_name == 'Продукти':
                self.mock_data[tab_name].sort(key=lambda x: x[0])
            elif tab_name == 'Продукти в магазині':
                self.mock_data[tab_name].sort(key=lambda x: int(x[3]), reverse=True)
            else:
                self.mock_data[tab_name].sort(key=lambda x: x[1])

        # Update the Treeview
        if tab_name == 'Працівники':
            self.update_employee_treeview()
        elif tab_name == 'Постійні клієнти':
            self.update_customer_treeview()
        elif tab_name == 'Продукти':
            self.update_product_treeview()
        elif tab_name == 'Продукти в магазині':
            self.update_store_product_treeview()
        else:
            tree.delete(*tree.get_children())  # Clear existing rows
            data = self.mock_data[tab_name]
            for row in data:
                tree.insert("", "end", values=row)

def on_cell_double_click(self, event, tab_name):
    """Handle double-click on a cell to edit its value or view receipt details"""
    tree = self.treeviews[tab_name]

    # Get the clicked region (check if it's on a cell, not a header)
    region = tree.identify("region", event.x, event.y)
    if region != "cell":
        return

    # Special handling for Чеки tab to show purchased items
    if tab_name == 'Чеки':
        selected_item = tree.selection()
        if not selected_item:
            return
        receipt_id = tree.item(selected_item, 'values')[0]
        self.show_receipt_items(receipt_id)
        return

    # Get the item and column that was clicked
    column = tree.identify_column(event.x)
    item = tree.identify_row(event.y)

    if not item:
        return

    # Convert column string like '#1', '#2' to an index
    column_index = int(column.replace('#', '')) - 1

    # Get the column name
    columns = self.entity_columns[tab_name]
    if column_index >= len(columns):
        return
    column_name = columns[column_index]

    # Prevent editing the 'назва' column in Продукти в магазині
    if tab_name == 'Продукти в магазині' and column_name == 'назва':
        messagebox.showinfo("Інформація", "Назва товару редагується в вкладці 'Продукти'.")
        return

    # Get the current value
    current_value = tree.item(item, 'values')[column_index]

    # Create a top-level window for editing
    edit_dialog = tk.Toplevel(self.root)
    edit_dialog.title(f"Редагувати {column_name}")
    edit_dialog.geometry("300x150")
    edit_dialog.transient(self.root)
    edit_dialog.grab_set()

    # Label
    label = tk.Label(edit_dialog, text=f"Редагувати {column_name}:")
    label.pack(pady=(20, 10))

    # Entry widget with current value
    entry = tk.Entry(edit_dialog, font=("Space Mono", 12), width=25)
    entry.insert(0, current_value)
    entry.pack(pady=10)
    entry.select_range(0, tk.END)  # Select all text
    entry.focus_set()  # Give focus to the entry

    # Function to save the edited value
    def save_edit():
        new_value = entry.get()
        if new_value != current_value:
            # Get all values from the item
            values = list(tree.item(item, 'values'))

            # Update the specific column
            values[column_index] = new_value

            # Update in treeview
            tree.item(item, values=values)

            # Update in mock data (need to find and replace the tuple)
            if tab_name == 'Продукти в магазині':
                old_values = (values[0], values[1], values[3], values[4], values[5])
                new_values = (values[0], values[1], values[3], values[4], values[5])
            else:
                old_values = tuple(tree.item(item, 'values'))
                new_values = tuple(values)

            if old_values in self.mock_data[tab_name]:
                index = self.mock_data[tab_name].index(old_values)
                self.mock_data[tab_name][index] = new_values

            # Sort if we're in the relevant tab and changed the relevant field
            if (tab_name in ['Працівники', 'Постійні клієнти'] and column_name == 'прізвище') or \
               (tab_name == 'Категорії' and column_name == 'назва') or \
               (tab_name == 'Продукти' and column_name == 'назва') or \
               (tab_name == 'Продукти в магазині' and column_name == 'наявність'):
                if tab_name == 'Категорії' or tab_name == 'Продукти':
                    self.mock_data[tab_name].sort(key=lambda x: x[0])
                elif tab_name == 'Продукти в магазині':
                    self.mock_data[tab_name].sort(key=lambda x: int(x[3]), reverse=True)
                else:
                    self.mock_data[tab_name].sort(key=lambda x: x[1])
                if tab_name == 'Працівники':
                    self.update_employee_treeview()
                elif tab_name == 'Постійні клієнти':
                    self.update_customer_treeview()
                elif tab_name == 'Продукти':
                    self.update_product_treeview()
                elif tab_name == 'Продукти в магазині':
                    self.update_store_product_treeview()
                else:
                    tree.delete(*tree.get_children())
                    data = self.mock_data[tab_name]
                    for row in data:
                        tree.insert("", "end", values=row)

        edit_dialog.destroy()

    # Save button
    save_button = tk.Button(
        edit_dialog,
        text="Зберегти",
        font=("Space Mono", 12),
        command=save_edit
    )
    save_button.pack(pady=10)

    # Center the dialog
    edit_dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (edit_dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (edit_dialog.winfo_height() // 2)
    edit_dialog.geometry(f"+{x}+{y}")

    # Handle Enter key
    entry.bind("<Return>", lambda event: save_edit())

def sort_treeview(self, tab_name, column, column_index):
    """Sort treeview by the specified column"""
    tree = self.treeviews[tab_name]

    # Get all items from the treeview
    data = [(tree.item(item, 'values'), item) for item in tree.get_children('')]

    # Sort based on the clicked column
    data.sort(key=lambda x: x[0][column_index])

    # Rearrange items in the treeview
    for index, (values, item) in enumerate(data):
        tree.move(item, '', index)

def show_receipt_items(self, receipt_id):
    """Show the purchased items in a specific receipt"""
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Товари в чеку {receipt_id}")
    dialog.geometry("600x400")
    dialog.transient(self.root)
    dialog.grab_set()

    # Create a frame for the treeview and scrollbars
    tree_frame = tk.Frame(dialog)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Define columns
    columns = ('назва', 'UPC', 'кількість', 'ціна за одиницю', 'загальна ціна')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

    # Set column headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    # Add scrollbars
    v_scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    h_scrollbar = tk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Layout the Treeview and scrollbars using grid
    tree.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')

    # Configure the frame to expand the Treeview
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # Get purchased items
    items = [item for item in self.mock_data['Товари в чеку'] if item[0] == receipt_id]
    product_dict = {product[1]: product[0] for product in self.mock_data['Продукти']}  # id продукту -> назва
    upc_to_product_id = {item[0]: item[1] for item in self.mock_data['Продукти в магазині']}  # UPC -> id продукту

    # Populate the treeview
    for item in items:
        upc = item[1]
        quantity = int(item[2])
        price_per_unit = float(item[3])
        total_price = quantity * price_per_unit
        product_id = upc_to_product_id.get(upc, "Невідомий")
        product_name = product_dict.get(product_id, "Невідомий продукт")
        tree.insert("", "end", values=(product_name, upc, quantity, price_per_unit, total_price))

    # Center the dialog
    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")