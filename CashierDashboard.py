import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from database import Database
from treeview_updater import (
    update_cashier_product_treeview,
    update_cashier_store_product_treeview,
    update_cashier_customer_treeview,
    update_cashier_receipt_treeview,
)
from item_operations import add_new_item, delete_selected_item, on_cell_double_click, show_receipt_items, sell_products

class CashierDashboard:
    cashier_show_promotional_only = False
    cashier_show_non_promotional_only = False

    update_cashier_product_treeview = update_cashier_product_treeview
    update_cashier_store_product_treeview = update_cashier_store_product_treeview
    update_cashier_customer_treeview = update_cashier_customer_treeview
    update_cashier_receipt_treeview = update_cashier_receipt_treeview
    add_new_item = add_new_item
    delete_selected_item = delete_selected_item
    on_cell_double_click = on_cell_double_click
    show_receipt_items = show_receipt_items
    sell_products = sell_products

    def __init__(self, root, cashier_id):
        self.root = root
        self.root.title("Cashier Dashboard")
        self.root.geometry("1200x800")
        self.cashier_id = cashier_id
        self.db = Database()

        custom_font = font.Font(family="Space Mono", size=12)
        self.root.option_add("*Font", custom_font)

        cashier_info = self.db.fetch_filtered("SELECT * FROM Employee WHERE id_employee = ?", (cashier_id,))
        cashier_info = cashier_info[0] if cashier_info else None
        if cashier_info:
            cashier_text = (f"Cashier: {cashier_info[1]} {cashier_info[2]} {cashier_info[3]}\n"
                           f"ID: {cashier_info[0]} | Role: {cashier_info[4]} | Salary: {cashier_info[5]}\n"
                           f"Date of Birth: {cashier_info[6]} | Date of Start: {cashier_info[7]} | Address: {cashier_info[8]}")
        else:
            cashier_text = "Cashier: Unknown"

        role_label = tk.Label(self.root, text=cashier_text, anchor="w", justify="left")
        role_label.pack(anchor="nw", padx=10, pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Treeview", font=("Space Mono", 12))
        style.configure("Treeview.Heading", font=("Space Mono", 12))
        style.configure("TNotebook.Tab", font=("Space Mono", 12))

        self.entity_columns = {
            'Product': ['id_product', 'product_name', 'category_number', 'characteristics'],
            'Store_Product': ['UPC', 'id_product', 'product_name', 'selling_price', 'products_number', 'promotional_product'],
            'Customer_Card': ['card_number', 'cust_surname', 'cust_name', 'cust_patronymic', 'phone_number', 'street', 'zip_code', 'percent'],
            'Check': ['check_number', 'cashier', 'print_date', 'sum_total'],
            'Sale': [],
        }

        self.treeviews = {}
        self.cashier_product_name_var = tk.StringVar()
        self.cashier_product_category_var = tk.StringVar()
        self.cashier_store_product_search_var = tk.StringVar()
        self.cashier_customer_search_var = tk.StringVar()
        self.cashier_promotional_sort_var = tk.StringVar(value="кількість")
        self.cashier_receipt_start_date_var = tk.StringVar()
        self.cashier_receipt_end_date_var = tk.StringVar()

        for entity, columns in self.entity_columns.items():
            self.create_tab(self.notebook, entity, columns)

        self.cashier_product_name_var.trace("w", lambda *args: self.update_cashier_product_treeview())
        self.cashier_product_category_var.trace("w", lambda *args: self.update_cashier_product_treeview())
        self.cashier_store_product_search_var.trace("w", lambda *args: self.update_cashier_store_product_treeview())
        self.cashier_customer_search_var.trace("w", lambda *args: self.update_cashier_customer_treeview())
        self.cashier_promotional_sort_var.trace("w", lambda *args: self.update_cashier_store_product_treeview())
        self.cashier_receipt_start_date_var.trace("w", lambda *args: self.update_cashier_receipt_treeview())
        self.cashier_receipt_end_date_var.trace("w", lambda *args: self.update_cashier_receipt_treeview())

        # Bind the window close event to properly close the database connection
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing to ensure the database connection is closed"""
        self.db.close()
        self.root.destroy()

    def create_tab(self, notebook, tab_text, columns):
        frame = tk.Frame(notebook)
        notebook.add(frame, text=tab_text)

        container_frame = tk.Frame(frame)
        container_frame.pack(fill='both', expand=True, padx=10, pady=10)

        button_frame = tk.Frame(container_frame)
        button_frame.pack(side='top', fill='x', pady=(0, 5))

        if tab_text == 'Sale':
            sell_button = tk.Button(container_frame, text="New Sale", font=("Space Mono", 12), command=self.sell_products)
            sell_button.pack(pady=10)
            return

        if tab_text == 'Product':
            name_label = tk.Label(button_frame, text="Search (product_name):")
            name_label.pack(side='left', padx=(5, 0))
            name_entry = tk.Entry(button_frame, textvariable=self.cashier_product_name_var, font=("Space Mono", 12))
            name_entry.pack(side='left', padx=(5, 10))

            category_label = tk.Label(button_frame, text="Search (category_number):")
            category_label.pack(side='left', padx=(5, 0))
            category_entry = tk.Entry(button_frame, textvariable=self.cashier_product_category_var, font=("Space Mono", 12))
            category_entry.pack(side='left', padx=(5, 10))

        if tab_text == 'Store_Product':
            search_label = tk.Label(button_frame, text="Search (UPC):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.cashier_store_product_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10))

            def toggle_promotional():
                self.cashier_show_promotional_only = not self.cashier_show_promotional_only
                self.cashier_show_non_promotional_only = False
                promo_button.config(text="Show All Products" if self.cashier_show_promotional_only else "Show Promotional Products")
                non_promo_button.config(text="Show Non-Promotional Products")
                self.update_cashier_store_product_treeview()

            def toggle_non_promotional():
                self.cashier_show_non_promotional_only = not self.cashier_show_non_promotional_only
                self.cashier_show_promotional_only = False
                non_promo_button.config(text="Show All Products" if self.cashier_show_non_promotional_only else "Show Non-Promotional Products")
                promo_button.config(text="Show Promotional Products")
                self.update_cashier_store_product_treeview()

            promo_button = tk.Button(button_frame, text="Show Promotional Products", font=("Space Mono", 12), command=toggle_promotional)
            promo_button.pack(side='left', padx=(5, 0))

            non_promo_button = tk.Button(button_frame, text="Show Non-Promotional Products", font=("Space Mono", 12), command=toggle_non_promotional)
            non_promo_button.pack(side='left', padx=(5, 0))

            sort_label = tk.Label(button_frame, text="Sort by:")
            sort_label.pack(side='left', padx=(10, 0))
            sort_menu = ttk.OptionMenu(button_frame, self.cashier_promotional_sort_var, "кількість", "кількість", "назва")
            sort_menu.pack(side='left', padx=(5, 10))

        if tab_text == 'Customer_Card':
            search_label = tk.Label(button_frame, text="Search (cust_surname):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.cashier_customer_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10), fill='x', expand=True)

        if tab_text == 'Check':
            start_date_label = tk.Label(button_frame, text="Start Date (YYYY-MM-DD):")
            start_date_label.pack(side='left', padx=(5, 0))
            start_date_entry = tk.Entry(button_frame, textvariable=self.cashier_receipt_start_date_var, font=("Space Mono", 12), width=12)
            start_date_entry.pack(side='left', padx=(5, 10))

            end_date_label = tk.Label(button_frame, text="End Date (YYYY-MM-DD):")
            end_date_label.pack(side='left', padx=(5, 0))
            end_date_entry = tk.Entry(button_frame, textvariable=self.cashier_receipt_end_date_var, font=("Space Mono", 12), width=12)
            end_date_entry.pack(side='left', padx=(5, 10))

        if tab_text == 'Customer_Card':
            add_button = tk.Button(button_frame, text="+", font=("Space Mono", 16, "bold"), width=3, command=lambda t=tab_text: self.add_new_item(t))
            add_button.pack(side='right', padx=(5, 0))
            delete_button = tk.Button(button_frame, text="Delete", font=("Space Mono", 12), command=lambda t=tab_text: self.delete_selected_item(t))
            delete_button.pack(side='right', padx=(5, 0))

        tree_frame = tk.Frame(container_frame)
        tree_frame.pack(fill='both', expand=True)

        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.treeviews[tab_text] = tree

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        v_scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        h_scrollbar = tk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        if tab_text == 'Product':
            self.update_cashier_product_treeview()
        elif tab_text == 'Store_Product':
            self.update_cashier_store_product_treeview()
        elif tab_text == 'Customer_Card':
            self.update_cashier_customer_treeview()
        elif tab_text == 'Check':
            self.update_cashier_receipt_treeview()

        tree.bind('<Double-1>', lambda event, t=tab_text: self.on_cell_double_click(event, t))

if __name__ == "__main__":
    root = tk.Tk()
    app = CashierDashboard(root, "1")
    root.mainloop()