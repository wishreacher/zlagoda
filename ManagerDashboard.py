import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from mock_data import get_mock_data
from treeview_updater import (
    update_employee_treeview,
    update_customer_treeview,
    update_product_treeview,
    update_store_product_treeview,
    update_receipt_treeview,
    update_receipt_reports
)
from item_operations import add_new_item, delete_selected_item, on_cell_double_click, sort_treeview, show_receipt_items

class DashboardView:
    show_cashiers_only = False  # Class variable to track the toggle state
    show_promotional_only = False  # Class variable to track promotional products toggle

    # Bind methods from other modules
    update_employee_treeview = update_employee_treeview
    update_customer_treeview = update_customer_treeview
    update_product_treeview = update_product_treeview
    update_store_product_treeview = update_store_product_treeview
    update_receipt_treeview = update_receipt_treeview
    update_receipt_reports = update_receipt_reports
    add_new_item = add_new_item
    delete_selected_item = delete_selected_item
    on_cell_double_click = on_cell_double_click
    sort_treeview = sort_treeview
    show_receipt_items = show_receipt_items

    def __init__(self, root, username):
        self.root = root
        self.root.title("Manager Dashboard")
        self.root.geometry("1200x800")
        self.username = username

        # Define and apply the custom font globally for standard Tkinter widgets
        custom_font = font.Font(family="Space Mono", size=12)
        self.root.option_add("*Font", custom_font)

        # Role label at the top
        role_label = tk.Label(
            self.root,
            text="Ваша роль: Менеджер",
            anchor="w"
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

        # Define the columns for each entity based on the ERD
        self.entity_columns = {
            'Продукти': ['назва', 'id продукту', 'id категорії', 'Опис'],
            'Продукти в магазині': ['UPC', 'id продукту', 'назва', 'ціна', 'наявність', 'акційнний товар'],
            'Категорії': ['назва', 'номер категорії'],
            'Працівники': ['id працівника', 'прізвище', 'імʼя', 'по-батькові', 'посада', 'зарплата', 'дата народження', 'дата початку', 'адреса'],
            'Постійні клієнти': ['номер картки', 'прізвище', 'імʼя', 'по-батькові', 'номер телефону', 'адреса', 'відсоток знижки'],
            'Чеки': ['номер чеку', 'касир', 'дата', 'загальна сума'],
        }

        # Store treeviews for later reference
        self.treeviews = {}

        # Store search terms for each tab
        self.search_var = tk.StringVar()  # For Працівники (прізвище)
        self.customer_search_var = tk.StringVar()  # For Постійні клієнти (відсоток знижки)
        self.product_search_var = tk.StringVar()  # For Продукти (id категорії)
        self.store_product_search_var = tk.StringVar()  # For Продукти в магазині (UPC)
        self.promotional_sort_var = tk.StringVar(value="кількість")  # For sorting promotional products
        self.receipt_cashier_var = tk.StringVar()  # For Чеки (касир)
        self.receipt_start_date_var = tk.StringVar()  # For Чеки (початкова дата)
        self.receipt_end_date_var = tk.StringVar()  # For Чеки (кінцева дата)
        self.receipt_product_var = tk.StringVar()  # For Чеки (UPC товару для підрахунку)

        # Load mock data
        self.mock_data = get_mock_data()

        # Create tabs for each entity
        for entity, columns in self.entity_columns.items():
            self.create_tab(self.notebook, entity, columns)

        # Set up trace callbacks after tabs are created
        self.search_var.trace("w", lambda *args: self.update_employee_treeview())
        self.customer_search_var.trace("w", lambda *args: self.update_customer_treeview())
        self.product_search_var.trace("w", lambda *args: self.update_product_treeview())
        self.store_product_search_var.trace("w", lambda *args: self.update_store_product_treeview())
        self.promotional_sort_var.trace("w", lambda *args: self.update_store_product_treeview())
        self.receipt_cashier_var.trace("w", lambda *args: self.update_receipt_treeview())
        self.receipt_start_date_var.trace("w", lambda *args: self.update_receipt_treeview())
        self.receipt_end_date_var.trace("w", lambda *args: self.update_receipt_treeview())
        self.receipt_product_var.trace("w", lambda *args: self.update_receipt_reports())

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

        # Add search functionality for Працівники tab
        if tab_text == 'Працівники':
            # Search bar for прізвище
            search_label = tk.Label(button_frame, text="Пошук (прізвище):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10), fill='x', expand=True)

        # Add search functionality for Постійні клієнти tab
        if tab_text == 'Постійні клієнти':
            # Search bar for відсоток знижки
            search_label = tk.Label(button_frame, text="Пошук (відсоток знижки ≥):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.customer_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10), fill='x', expand=True)

        # Add search functionality for Продукти tab
        if tab_text == 'Продукти':
            # Search bar for id категорії
            search_label = tk.Label(button_frame, text="Пошук (id категорії):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.product_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10), fill='x', expand=True)

        # Add search and filter functionality for Продукти в магазині tab
        if tab_text == 'Продукти в магазині':
            # Search bar for UPC
            search_label = tk.Label(button_frame, text="Пошук (UPC):")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.store_product_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10))

            # Toggle button for promotional products
            def toggle_promotional():
                self.show_promotional_only = not self.show_promotional_only
                toggle_button.config(
                    text="Показати всі товари" if self.show_promotional_only else "Показати акційні товари"
                )
                self.update_store_product_treeview()

            toggle_button = tk.Button(
                button_frame,
                text="Показати акційні товари",
                font=("Space Mono", 12),
                command=toggle_promotional
            )
            toggle_button.pack(side='left', padx=(5, 0))

            # Sort option for promotional products
            sort_label = tk.Label(button_frame, text="Сортувати за:")
            sort_label.pack(side='left', padx=(10, 0))
            sort_menu = ttk.OptionMenu(
                button_frame,
                self.promotional_sort_var,
                "кількість",
                "кількість",
                "назва"
            )
            sort_menu.pack(side='left', padx=(5, 10))

        # Add search and filter functionality for Чеки tab
        if tab_text == 'Чеки':
            # Cashier filter
            cashier_label = tk.Label(button_frame, text="Касир:")
            cashier_label.pack(side='left', padx=(5, 0))
            cashier_options = ["Всі касири"] + [worker[0] for worker in self.mock_data['Працівники'] if worker[4] == 'Касир']
            cashier_menu = ttk.OptionMenu(
                button_frame,
                self.receipt_cashier_var,
                cashier_options[0],
                *cashier_options
            )
            cashier_menu.pack(side='left', padx=(5, 10))

            # Start date filter
            start_date_label = tk.Label(button_frame, text="Початкова дата (РРРР-ММ-ДД):")
            start_date_label.pack(side='left', padx=(5, 0))
            start_date_entry = tk.Entry(button_frame, textvariable=self.receipt_start_date_var, font=("Space Mono", 12), width=12)
            start_date_entry.pack(side='left', padx=(5, 10))

            # End date filter
            end_date_label = tk.Label(button_frame, text="Кінцева дата (РРРР-ММ-ДД):")
            end_date_label.pack(side='left', padx=(5, 0))
            end_date_entry = tk.Entry(button_frame, textvariable=self.receipt_end_date_var, font=("Space Mono", 12), width=12)
            end_date_entry.pack(side='left', padx=(5, 10))

        # Add the toggle button for cashiers (only for Працівники tab)
        if tab_text == 'Працівники':
            self.show_cashiers_only = False  # Toggle state

            def toggle_cashiers():
                self.show_cashiers_only = not self.show_cashiers_only
                toggle_button.config(
                    text="Показати всіх" if self.show_cashiers_only else "Показати касирів"
                )
                self.update_employee_treeview()

            toggle_button = tk.Button(
                button_frame,
                text="Показати касирів",
                font=("Space Mono", 12),
                command=toggle_cashiers
            )
            toggle_button.pack(side='left', padx=(5, 0))

        # Add the + button (aligned right, exclude for Чеки)
        if tab_text != 'Чеки':
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

        # Add reports section for Чеки tab
        if tab_text == 'Чеки':
            reports_frame = tk.Frame(container_frame)
            reports_frame.pack(fill='x', pady=(5, 0))

            # Product UPC for quantity calculation
            product_label = tk.Label(reports_frame, text="UPC товару для підрахунку:")
            product_label.pack(side='left', padx=(5, 0))
            product_options = [""] + [item[0] for item in self.mock_data['Продукти в магазині']]
            product_menu = ttk.OptionMenu(
                reports_frame,
                self.receipt_product_var,
                product_options[0],
                *product_options
            )
            product_menu.pack(side='left', padx=(5, 10))

            # Total sales labels
            self.total_sales_specific_label = tk.Label(reports_frame, text="Сума (вибраний касир): 0.00")
            self.total_sales_specific_label.pack(side='left', padx=(10, 0))
            self.total_sales_all_label = tk.Label(reports_frame, text="Сума (всі касири): 0.00")
            self.total_sales_all_label.pack(side='left', padx=(10, 0))
            self.total_quantity_label = tk.Label(reports_frame, text="Кількість товару (UPC не вибрано): 0")
            self.total_quantity_label.pack(side='left', padx=(10, 0))

        # Function to update the Treeview (for tabs without search)
        def update_treeview():
            tree.delete(*tree.get_children())  # Clear existing rows
            data = self.mock_data.get(tab_text, [])
            if self.show_cashiers_only and tab_text == 'Працівники':
                data = [row for row in data if row[4] == 'Касир']  # Filter by "Касир"
            for row in data:
                tree.insert("", "end", values=row)

        # Use the appropriate update function for each tab
        if tab_text == 'Працівники':
            self.update_employee_treeview()
        elif tab_text == 'Постійні клієнти':
            self.update_customer_treeview()
        elif tab_text == 'Продукти':
            self.update_product_treeview()
        elif tab_text == 'Продукти в магазині':
            self.update_store_product_treeview()
        elif tab_text == 'Чеки':
            self.update_receipt_treeview()
        else:
            update_treeview()

        # Bind double-click event for editing cells or viewing receipt details
        tree.bind('<Double-1>', lambda event, t=tab_text: self.on_cell_double_click(event, t))

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardView(root, "username")
    root.mainloop()