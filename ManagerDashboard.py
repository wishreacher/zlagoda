import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font, messagebox
from database import Database
from treeview_updater import (
    update_employee_treeview,
    update_customer_treeview,
    update_product_treeview,
    update_store_product_treeview,
    update_receipt_treeview,
    update_receipt_reports,
    update_category_treeview
)
from item_operations import add_new_item, delete_selected_item, on_cell_double_click, show_receipt_items
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
import os
import fitz
from PIL import Image, ImageTk
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

class ManagerDashboard:
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
    show_receipt_items = show_receipt_items
    update_category_treeview = update_category_treeview

    def __init__(self, root, username):
        self.root = root
        self.root.title("Manager Dashboard")
        self.root.geometry("1200x800")
        self.username = username
        self.db = Database()  # Initialize the database

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

        # Define the columns for each entity (using Ukrainian labels for display)
        self.entity_columns = {
            'Продукти': ['назва', 'id продукту', 'id категорії', 'Опис', 'виробник'],
            'Продукти в магазині': ['UPC', 'id продукту', 'назва', 'ціна', 'наявність', 'акційнний товар'],
            'Категорії': ['назва', 'номер категорії'],
            'Працівники': ['id працівника', 'прізвище', 'імʼя', 'по-батькові', 'посада', 'зарплата', 'дата народження', 'дата початку', 'адреса', 'телефон', 'пароль'],
            'Постійні клієнти': ['номер картки', 'прізвище', 'імʼя', 'по-батькові', 'номер телефона', 'вулиця', 'індекс', 'відсоток знижки'],
            'Чеки': ['номер чеку', 'касир', 'дата', 'загальна сума'],
            'Статистика': [],  
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

        # Bind the window close event to properly close the database connection
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)



    def on_closing(self):
        """Handle window closing to ensure the database connection is closed"""
        self.db.close()
        self.root.destroy()

    def update_cashier_store_product_treeview(self):
        tree = self.treeviews['Продукти в магазині']
        tree.delete(*tree.get_children())
        query = """
            SELECT sp.UPC, sp.id_product, p.product_name, sp.selling_price, sp.products_number, sp.promotional_product
            FROM Store_Product sp
            JOIN Product p ON sp.id_product = p.id_product
        """
        items = self.db.fetch_filtered(query)
        for item in items:
            tree.insert('', 'end', values=item)


    def create_tab(self, notebook, tab_text, columns):
        # Create a frame for the tab
        frame = tk.Frame(notebook)
        notebook.add(frame, text=tab_text)

        if tab_text == 'Статистика':
            # Create a container frame for the statistics tab
            container_frame = tk.Frame(frame)
            container_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Define queries with descriptions and column names
            queries = [
                {
                    'description': 'Всі касири, які продали хоча б один товар кожної категорії',
                    'query': """
                        SELECT DISTINCT e.id_employee, e.surname, e.name
                        FROM Employee e
                        JOIN [Check] c ON e.id_employee = c.id_employee
                        JOIN Sale s ON c.check_number = s.check_number
                        JOIN Store_Product sp ON s.UPC = sp.UPC
                        JOIN Product p ON sp.id_product = p.id_product
                        WHERE e.role = 'cashier'
                        GROUP BY e.id_employee, e.surname, e.name
                        HAVING COUNT(DISTINCT p.id_category) = (SELECT COUNT(*) FROM Category)
                    """,
                    'columns': ['ID працівника', 'Прізвище', "Ім'я"]
                },
                {
                    'description': 'Топ-5 товарів за кількістю продажів',
                    'query': """
                        SELECT p.product_name, sp.UPC, SUM(s.product_number) as total_sold
                        FROM Sale s
                        JOIN Store_Product sp ON s.UPC = sp.UPC
                        JOIN Product p ON sp.id_product = p.id_product
                        GROUP BY p.product_name, sp.UPC
                        ORDER BY total_sold DESC
                        LIMIT 5
                    """,
                    'columns': ['Назва товару', 'UPC', 'Кількість проданих']
                },
                {
                    'description': 'Касири з найбільшою сумою продажів за останній місяць',
                    'query': """
                        SELECT e.surname, e.name, SUM(c.sum_total) as total_sales
                        FROM Employee e
                        JOIN [Check] c ON e.id_employee = c.id_employee
                        WHERE c.print_date >= date('now', '-1 month')
                        GROUP BY e.id_employee, e.surname, e.name
                        ORDER BY total_sales DESC
                    """,
                    'columns': ['Прізвище', "Ім'я", 'Сума продажів']
                },
                {
                    'description': 'Категорії з найбільшою кількістю проданих товарів',
                    'query': """
                        SELECT c.category_name, SUM(s.product_number) as total_sold
                        FROM Sale s
                        JOIN Store_Product sp ON s.UPC = sp.UPC
                        JOIN Product p ON sp.id_product = p.id_product
                        JOIN Category c ON p.id_category = c.category_number
                        GROUP BY c.category_name
                        ORDER BY total_sold DESC
                    """,
                    'columns': ['Назва категорії', 'Кількість проданих']
                },
                {
                    'description': 'Клієнти з найвищими знижками',
                    'query': """
                        SELECT c.card_number, c.surname, c.name, c.discount_percentage
                        FROM Customer c
                        ORDER BY c.discount_percentage DESC
                        LIMIT 5
                    """,
                    'columns': ['Номер картки', 'Прізвище', "Ім'я", 'Відсоток знижки']
                },
                {
                    'description': 'Чеки з найбільшою кількістю товарів',
                    'query': """
                        SELECT c.check_number, COUNT(s.UPC) as item_count, c.sum_total
                        FROM [Check] c
                        JOIN Sale s ON c.check_number = s.check_number
                        GROUP BY c.check_number, c.sum_total
                        ORDER BY item_count DESC
                        LIMIT 5
                    """,
                    'columns': ['Номер чеку', 'Кількість товарів', 'Загальна сума']
                }
            ]

            # Create a frame for the query list
            query_frame = tk.Frame(container_frame)
            query_frame.pack(fill='x', pady=5)

            # Create a Treeview for displaying query results
            tree_frame = tk.Frame(container_frame)
            tree_frame.pack(fill='both', expand=True)

            tree = ttk.Treeview(tree_frame, show='headings')
            self.treeviews[tab_text] = tree

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

            # Add each query description and button
            for idx, query_info in enumerate(queries):
                query_row_frame = tk.Frame(query_frame)
                query_row_frame.pack(fill='x', pady=2)

                description_label = tk.Label(
                    query_row_frame,
                    text=f"{idx + 1}. {query_info['description']}",
                    font=("Space Mono", 12),
                    anchor='w'
                )
                description_label.pack(side='left', fill='x', expand=True, padx=5)

                show_button = tk.Button(
                    query_row_frame,
                    text="Показати",
                    font=("Space Mono", 12),
                    command=lambda q=query_info['query'], c=query_info['columns']: self.show_query_results(q, c, tree)
                )
                show_button.pack(side='right', padx=5)

            return
        
        # Create a container frame that will hold the buttons and treeview
        container_frame = tk.Frame(frame)
        container_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create a button frame for the top
        button_frame = tk.Frame(container_frame)
        button_frame.pack(side='top', fill='x', pady=(0, 5))

        # Add "Друк звіту" button for all tabs except 'Чеки'
        if tab_text != 'Чеки':
            export_button = tk.Button(
                button_frame,
                text="Друк звіту",
                font=("Space Mono", 12),
                command=lambda t=tab_text: self.export_report(t)
            )
            export_button.pack(side='right', padx=(5, 0))
        else:
            # Add "Друк деталей чеку" button for 'Чеки' tab
            export_receipt_button = tk.Button(
                button_frame,
                text="Друк деталей чеку",
                font=("Space Mono", 12),
                command=lambda: self.export_receipt_details()
            )
            export_receipt_button.pack(side='right', padx=(5, 0))

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
            cashier_data = self.db.fetch_filtered("SELECT id_employee, surname, name FROM Employee WHERE role = 'cashier'")
            cashier_options = ["Всі касири"] + [f"{row[1]} {row[2]}" for row in cashier_data]
            cashier_ids = ["Всі касири"] + [row[0] for row in cashier_data]
            self.cashier_mapping = dict(zip(cashier_options, cashier_ids))  # Map display names to IDs
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

            today_button = tk.Button(
                button_frame,
                text="Сьогоднішні чеки",
                font=("Space Mono", 12),
                command=self.show_today_receipts
            )
            today_button.pack(side='right', padx=(5, 0))

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
            product_data = self.db.fetch_all('Store_Product')
            product_options = [""] + [row[0] for row in product_data]
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
        else:  # Категорії
            query = "SELECT category_name, category_number FROM Category"
            data = self.db.fetch_filtered(query)
            tree.delete(*tree.get_children())
            for row in data:
                tree.insert("", "end", values=row)

        # Bind double-click event for editing cells or viewing receipt details
        tree.bind('<Double-1>', lambda event, t=tab_text: self.on_cell_double_click(event, t))

    def show_pdf_preview(self, filename, report_name):
        """Show a preview of the generated PDF report."""
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Перегляд звіту: {report_name}")
        preview_window.geometry("800x600")

        pdf_doc = fitz.open(filename)
        page = pdf_doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_tk = ImageTk.PhotoImage(img)

        label = tk.Label(preview_window, image=img_tk)
        label.image = img_tk
        label.pack(fill='both', expand=True)

        button_frame = tk.Frame(preview_window)
        button_frame.pack(side='bottom', pady=10)

        print_button = tk.Button(button_frame, text="Друк",
                                 command=lambda: self.finalize_print(filename, preview_window, report_name))
        print_button.pack(side='left', padx=10)

        cancel_button = tk.Button(button_frame, text="Скасувати",
                                  command=lambda: [preview_window.destroy(), os.remove(filename)])
        cancel_button.pack(side='left', padx=10)

    def finalize_print(self, filename, window, report_name):
        """Finalize the PDF report by renaming and saving it."""
        final_filename = f"report_{report_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.rename(filename, final_filename)
        messagebox.showinfo("Успіх", f"Звіт збережено як {final_filename}")
        window.destroy()

    def export_report(self, tab_name):
        """Export the report for the specified tab to a PDF with a formatted table."""
        tree = self.treeviews[tab_name]
        columns = self.entity_columns[tab_name]
        data = [tree.item(item, 'values') for item in tree.get_children()]

        if not data:
            messagebox.showwarning("Попередження", "Немає даних для створення звіту")
            return

        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            filename = temp_file.name

        # Initialize the PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []

        # Set up styles
        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'DejaVuSans'
        styles['Title'].fontName = 'DejaVuSans'

        # Add report title
        elements.append(Paragraph(f"Звіт: {tab_name}", styles['Title']))
        elements.append(Paragraph(f"Дата створення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))

        # Prepare table data
        table_data = [columns]  # Header row
        for row in data:
            table_data.append(list(row))

        # Calculate column widths dynamically based on content
        col_widths = [1.5 * inch] * len(columns)
        if tab_name == 'Працівники':
            col_widths = [1 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
        elif tab_name == 'Постійні клієнти':
            col_widths = [1.2 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1.2 * inch, 1.5 * inch, 1 * inch, 1 * inch]
        elif tab_name == 'Продукти':
            col_widths = [1.5 * inch, 1 * inch, 1 * inch, 2 * inch, 1.5 * inch]
        elif tab_name == 'Продукти в магазині':
            col_widths = [1.2 * inch, 1 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1.2 * inch]
        elif tab_name == 'Категорії':
            col_widths = [2 * inch, 1.5 * inch]

        # Create the table
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Add summary if applicable (e.g., total count)
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph(f"Загальна кількість записів: {len(data)}", styles['Normal']))

        # Add print time
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph(f"Час друку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

        # Build the PDF
        doc.build(elements)

        # Show preview
        self.show_pdf_preview(filename, tab_name)

    def transliterate(text):
            translit_dict = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z',
                'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
                'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh',
                'щ': 'shch',
                'ь': '', 'ю': 'yu', 'я': 'ya',
                'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z',
                'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
                'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh',
                'Щ': 'Shch',
                'Ь': '', 'Ю': 'Yu', 'Я': 'Ya',
            }
            return ''.join(translit_dict.get(char, char) for char in text)


    def export_receipt_details(self):
        """Export details of the selected receipt to a PDF with formatted table."""
        tree = self.treeviews['Чеки']
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Виберіть чек для друку")
            return
        check_number = tree.item(selected_item, 'values')[0]

        check_info = self.db.fetch_filtered("SELECT * FROM [Check] WHERE check_number = ?", (check_number,))
        if not check_info:
            messagebox.showerror("Помилка", "Чек не знайдено")
            return

        check_info = check_info[0]
        cashier_id = check_info[1]
        print_date = check_info[3]
        sum_total = check_info[4]

        items = self.db.fetch_filtered(
            """
            SELECT p.product_name, s.UPC, s.product_number, s.selling_price, (s.product_number * s.selling_price)
            FROM Sale s JOIN Store_Product sp ON s.UPC = sp.UPC
            JOIN Product p ON sp.id_product = p.id_product WHERE s.check_number = ?
            """,
            (check_number,)
        )

        if not items:
            messagebox.showerror("Помилка", "Не знайдено жодного товару для цього чека")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            filename = temp_file.name

        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []

        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'DejaVuSans'
        styles['Title'].fontName = 'DejaVuSans'

        elements.append(Paragraph(f"Чек: {check_number}", styles['Title']))
        elements.append(Paragraph(f"Номер чека: {check_number}", styles['Normal']))
        elements.append(Paragraph(f"Дата: {print_date}", styles['Normal']))
        elements.append(Paragraph(f"Касир: {cashier_id}", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))

        data = [["Назва товару", "UPC", "Кількість", "Ціна", "Сума"]]
        for item in items:
            product_name_translit = self.transliterate(item[0])  # Додано: Транслітерація назви товару
            data.append([product_name_translit, item[1], item[2], f"{item[3]:.2f}", f"{item[4]:.2f}"])

        table = Table(data, colWidths=[2 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        pdv = float(sum_total) * 0.2 if isinstance(sum_total, (int, float)) else 0
        total_row = ["", "", "", "Загальна сума:", f"{sum_total:.2f}"]
        pdv_row = ["", "", "", "ПДВ:", f"{pdv:.2f}"]
        total_table = Table([total_row, pdv_row], colWidths=[2 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(total_table)
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph(f"Час друку: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

        doc.build(elements)

        self.show_pdf_preview(filename, check_number)

    def show_today_receipts(self):
        """Set the start and end date filters to today's date to show all receipts for today"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.receipt_start_date_var.set(today)
        self.receipt_end_date_var.set(today)

if __name__ == "__main__":
    root = tk.Tk()
    app = ManagerDashboard(root, "username")
    root.mainloop()