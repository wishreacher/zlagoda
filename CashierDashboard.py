import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from mock_data import get_mock_data
from treeview_updater import (
    update_cashier_product_treeview,
    update_cashier_store_product_treeview,
    update_cashier_customer_treeview,
    update_cashier_receipt_treeview,
)
from item_operations import add_new_item, delete_selected_item, on_cell_double_click, sort_treeview, show_receipt_items, sell_products

class CashierDashboard:
    cashier_show_promotional_only = False  # Track promotional products toggle
    cashier_show_non_promotional_only = False  # Track non-promotional products toggle

    # Bind methods from other modules
    update_cashier_product_treeview = update_cashier_product_treeview
    update_cashier_store_product_treeview = update_cashier_store_product_treeview
    update_cashier_customer_treeview = update_cashier_customer_treeview
    update_cashier_receipt_treeview = update_cashier_receipt_treeview
    add_new_item = add_new_item
    delete_selected_item = delete_selected_item
    on_cell_double_click = on_cell_double_click
    sort_treeview = sort_treeview
    show_receipt_items = show_receipt_items
    sell_products = sell_products

    def __init__(self, root, cashier_id):
        self.root = root
        self.root.title("Cashier Dashboard")
        self.root.geometry("1200x800")
        self.cashier_id = cashier_id

        # Define and apply the custom font globally for standard Tkinter widgets
        custom_font = font.Font(family="Space Mono", size=12)
        self.root.option_add("*Font", custom_font)

        # Load mock data
        self.mock_data = get_mock_data()

        # Get cashier info (Req 15)
        cashier_info = next((worker for worker in self.mock_data['Працівники'] if worker[0] == cashier_id), None)
        if cashier_info:
            cashier_text = (f"Касир: {cashier_info[1]} {cashier_info[2]} {cashier_info[3]}\n"
                           f"ID: {cashier_info[0]} | Посада: {cashier_info[4]} | Зарплата: {cashier_info[5]}\n"
                           f"Дата народження: {cashier_info[6]} | Дата початку: {cashier_info[7]} | Адреса: {cashier_info[8]}")
        else:
            cashier_text = "Касир: Невідомий"

        # Role label at the top with cashier info (Req 15)
        role_label = tk.Label(
            self.root,
            text=cashier_text,
            anchor="w",
            justify="left"
        )
        role_label.pack(anchor="nw", padx=10, pady=10)

        # Create the notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Configure styles for ttk widgets to use "Space Mono" font
        style = ttk.Style()
        style.configure("Treeview", font=("Space Mono", 12))
        style.configure("Treeview.Heading", font=("Space Mono", 12))
        style.configure("TNotebook.Tab", font=("Space Mono", 12))

        # Define the columns for each entity
        self.entity_columns = {
            'Продукти': ['назва', 'id продукту', 'id категорії', 'Опис'],
            'Продукти в магазині': ['UPC', 'id продукту', 'назва', 'ціна', 'наявність', 'акційнний товар'],
            'Постійні клієнти': ['номер картки', 'прізвище', 'імʼя', 'по-батькові', 'номер телефону', 'адреса', 'відсоток знижки'],
            'Чеки': ['номер чеку', 'касир', 'дата', 'загальна сума'],
            'Продаж': [],  # Placeholder tab with custom content
        }

        # Store treeviews for later reference
        self.treeviews = {}

        # Store search terms for each tab
        self.cashier_product_name_var = tk.StringVar()  # For Продукти (назва)
        self.cashier_product_category_var = tk.StringVar()  # For Продукти (id категорії)
        self.cashier_store_product_search_var = tk.StringVar()  # For Продукти в магазині (UPC)
        self.cashier_customer_search_var = tk.StringVar()  # For Постійні клієнти (прізвище)
        self.cashier_promotional_sort_var = tk.StringVar(value="кількість")  # For sorting products in store
        self.cashier_receipt_start_date_var = tk.StringVar()  # For Чеки (початкова дата)
        self.cashier_receipt_end_date_var = tk.StringVar()  # For Чеки (кінцева дата)

        # Create tabs for each entity
        for entity, columns in self.entity_columns.items():
            self.create_tab(self.notebook, entity, columns)

        # Set up trace callbacks after tabs are created
        self.cashier_product_name_var.trace("w", lambda *args: self.update_cashier_product_treeview())
        self.cashier_product_category_var.trace("w", lambda *args: self.update_cashier_product_treeview())
        self.cashier_store_product_search_var.trace("w", lambda *args: self.update_cashier_store_product_treeview())
        self.cashier_customer_search_var.trace("w", lambda *args: self.update_cashier_customer_treeview())
        self.cashier_promotional_sort_var.trace("w", lambda *args: self.update_cashier_store_product_treeview())
        self.cashier_receipt_start_date_var.trace("w", lambda *args: self.update_cashier_receipt_treeview())
        self.cashier_receipt_end_date_var.trace("w", lambda *args: self.update_cashier_receipt_treeview())

    def create_tab(self, notebook, tab_text, columns):
        # Create a frame for the tab
        frame = tk.Frame(notebook)
        notebook.add(frame, text=tab_text)

        # Create a container frame that will hold the buttons and treeview
        container_frame = tk.Frame(frame)
        container_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create a button frame for the top
        button_frame = tk.Frame(container_frame)
        button_frame.pack(side='top', fill='x', pady=(0, 5))

        # Special handling for Продаж tab (Req 7)
        if tab_text == 'Продаж':
            sell_button = tk.Button(
                container_frame,
                text="Новий продаж",
                font=("Space Mono", 12),
                command=self.sell_products
            )
            sell_button.pack(pady=10)
            return  # No Treeview for this tab

        # Add search functionality for Продукти tab (Req 4, 5)
        if tab_text == 'Продукти':
            # Search bar for назва
            name_label = tk.Label(button_frame, text="Пошук (назва):")
            name_label.pack(side='left', padx=(5, 0))
            name_entry = tk.Entry(button_frame, textvariable=self.cashier_product_name_var, font=("Space Mono", 12))
            name_entry.pack(side='left', padx=(5, 10))

            # Search bar for id категорії
            category_label = tk.Label(button_frame, text="Пошук (id категорії):")
            category_label.pack(side='left', padx=(5, 0))
            category_entry = tk.Entry(button_frame, textvariable=self.cashier_product_category_var, font=("Space Mono", 12))
            category_entry.pack(side='left', padx=(5, 10))

        # Add search and filter functionality for Продукти в магазині tab (Req 12, 13, 14)
        if tab_text == 'Продукти в магазині':
            # Search bar for UPC (Req 14)
            search_label = tk.Label(button_frame, text="Пошук (UPC):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.cashier_store_product_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10))

            # Toggle button for promotional products (Req 12)
            def toggle_promotional():
                self.cashier_show_promotional_only = not self.cashier_show_promotional_only
                self.cashier_show_non_promotional_only = False
                promo_button.config(
                    text="Показати всі товари" if self.cashier_show_promotional_only else "Показати акційні товари"
                )
                non_promo_button.config(
                    text="Показати неакційні товари"
                )
                self.update_cashier_store_product_treeview()

            # Toggle button for non-promotional products (Req 13)
            def toggle_non_promotional():
                self.cashier_show_non_promotional_only = not self.cashier_show_non_promotional_only
                self.cashier_show_promotional_only = False
                non_promo_button.config(
                    text="Показати всі товари" if self.cashier_show_non_promotional_only else "Показати неакційні товари"
                )
                promo_button.config(
                    text="Показати акційні товари"
                )
                self.update_cashier_store_product_treeview()

            promo_button = tk.Button(
                button_frame,
                text="Показати акційні товари",
                font=("Space Mono", 12),
                command=toggle_promotional
            )
            promo_button.pack(side='left', padx=(5, 0))

            non_promo_button = tk.Button(
                button_frame,
                text="Показати неакційні товари",
                font=("Space Mono", 12),
                command=toggle_non_promotional
            )
            non_promo_button.pack(side='left', padx=(5, 0))

            # Sort option for products (Req 12, 13)
            sort_label = tk.Label(button_frame, text="Сортувати за:")
            sort_label.pack(side='left', padx=(10, 0))
            sort_menu = ttk.OptionMenu(
                button_frame,
                self.cashier_promotional_sort_var,
                "кількість",
                "кількість",
                "назва"
            )
            sort_menu.pack(side='left', padx=(5, 10))

        # Add search functionality for Постійні клієнти tab (Req 6)
        if tab_text == 'Постійні клієнти':
            # Search bar for прізвище
            search_label = tk.Label(button_frame, text="Пошук (прізвище):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.cashier_customer_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10), fill='x', expand=True)

        # Add date range filters for Чеки tab (Req 9, 10)
        if tab_text == 'Чеки':
            # Start date filter
            start_date_label = tk.Label(button_frame, text="Початкова дата (РРРР-ММ-ДД):")
            start_date_label.pack(side='left', padx=(5, 0))
            start_date_entry = tk.Entry(button_frame, textvariable=self.cashier_receipt_start_date_var, font=("Space Mono", 12), width=12)
            start_date_entry.pack(side='left', padx=(5, 10))

            # End date filter
            end_date_label = tk.Label(button_frame, text="Кінцева дата (РРРР-ММ-ДД):")
            end_date_label.pack(side='left', padx=(5, 0))
            end_date_entry = tk.Entry(button_frame, textvariable=self.cashier_receipt_end_date_var, font=("Space Mono", 12), width=12)
            end_date_entry.pack(side='left', padx=(5, 10))

        # Add the + button (aligned right, only for Постійні клієнти) (Req 8)
        if tab_text == 'Постійні клієнти':
            add_button = tk.Button(
                button_frame,
                text="+",
                font=("Space Mono", 16, "bold"),
                width=3,
                command=lambda t=tab_text: self.add_new_item(t)
            )
            add_button.pack(side='right', padx=(5, 0))

            # Add delete button (aligned right)
            delete_button = tk.Button(
                button_frame,
                text="Видалити",
                font=("Space Mono", 12),
                command=lambda t=tab_text: self.delete_selected_item(t)
            )
            delete_button.pack(side='right', padx=(5, 0))

        # Create a frame for the treeview and scrollbars
        tree_frame = tk.Frame(container_frame)
        tree_frame.pack(fill='both', expand=True)

        # Create the Treeview with specified columns
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        # Store the treeview reference
        self.treeviews[tab_text] = tree

        # Set column headings and default width
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

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

        # Function to update the Treeview (for tabs without specific updaters)
        def update_treeview():
            tree.delete(*tree.get_children())  # Clear existing rows
            data = self.mock_data.get(tab_text, [])
            for row in data:
                tree.insert("", "end", values=row)

        # Use the appropriate update function for each tab
        if tab_text == 'Продукти':
            self.update_cashier_product_treeview()
        elif tab_text == 'Продукти в магазині':
            self.update_cashier_store_product_treeview()
        elif tab_text == 'Постійні клієнти':
            self.update_cashier_customer_treeview()
        elif tab_text == 'Чеки':
            self.update_cashier_receipt_treeview()
        else:
            update_treeview()

        # Bind double-click event for editing cells or viewing receipt details
        tree.bind('<Double-1>', lambda event, t=tab_text: self.on_cell_double_click(event, t))

if __name__ == "__main__":
    root = tk.Tk()
    app = CashierDashboard(root, "1")  # Example cashier ID
    root.mainloop()