import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font, messagebox
from database import Database
from treeview_updater import (
    update_cashier_product_treeview,
    update_cashier_store_product_treeview,
    update_cashier_customer_treeview,
    update_cashier_receipt_treeview,
)
from item_operations import add_new_item, delete_selected_item, on_cell_double_click, show_receipt_items, sell_products
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

class DashboardView:
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
        self.root.title("Панель касира")
        self.root.geometry("1200x800")
        self.cashier_id = cashier_id
        self.db = Database()

        custom_font = font.Font(family="Space Mono", size=12)
        self.root.option_add("*Font", custom_font)

        cashier_info = self.db.fetch_filtered("SELECT * FROM Employee WHERE id_employee = ?", (cashier_id,))
        cashier_info = cashier_info[0] if cashier_info else None
        if cashier_info:
            cashier_text = (f"Касир: {cashier_info[1]} {cashier_info[2]} {cashier_info[3]}\n"
                           f"ID: {cashier_info[0]} | Посада: {cashier_info[4]} | Зарплата: {cashier_info[5]}\n"
                           f"Дата народження: {cashier_info[6]} | Дата початку: {cashier_info[7]} | Адреса: {cashier_info[8]} | Телефон: {cashier_info[10]}")
        else:
            cashier_text = "Касира не знайдено"

        role_label = tk.Label(self.root, text=cashier_text, anchor="w", justify="left")
        role_label.pack(anchor="nw", padx=10, pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Treeview", font=("Space Mono", 12))
        style.configure("Treeview.Heading", font=("Space Mono", 12))
        style.configure("TNotebook.Tab", font=("Space Mono", 12))

        self.entity_columns = {
            'Продукти': ['ID продукта', 'назва', 'категорія', 'опис', 'виробник'],
            'Продукти у магазині': ['UPC', 'ID продукта', 'назва', 'ціна', 'кількість', 'наявність знижки'],
            'Постійні клієнти': ['номер картки', 'прізвище', 'імʼя', 'по-батькові', 'номер телефона', 'адреса', 'індекс', 'відсоток знижки'],
            'Чеки': ['номер чека', 'касир', 'дата видачі', 'сума'],
            'Продажі': [],
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

        if tab_text == 'Продажі':
            sell_button = tk.Button(container_frame, text="Новий продаж", font=("Space Mono", 12), command=self.sell_products)
            sell_button.pack(pady=10)
            return

        if tab_text == 'Продукти':
            name_label = tk.Label(button_frame, text="Пошук по назві продукта:")
            name_label.pack(side='left', padx=(5, 0))
            name_entry = tk.Entry(button_frame, textvariable=self.cashier_product_name_var, font=("Space Mono", 12))
            name_entry.pack(side='left', padx=(5, 10))

            category_label = tk.Label(button_frame, text="Пошук по номеру категорії")
            category_label.pack(side='left', padx=(5, 0))
            category_entry = tk.Entry(button_frame, textvariable=self.cashier_product_category_var, font=("Space Mono", 12))
            category_entry.pack(side='left', padx=(5, 10))

        if tab_text == 'Продукти у магазині':
            search_label = tk.Label(button_frame, text="Пошук за UPC")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.cashier_store_product_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10))

            def toggle_promotional():
                self.cashier_show_promotional_only = not self.cashier_show_promotional_only
                self.cashier_show_non_promotional_only = False
                promo_button.config(text="Усі продукти" if self.cashier_show_promotional_only else "Продукти по акції")
                non_promo_button.config(text="Продукти без акцій")
                self.update_cashier_store_product_treeview()

            def toggle_non_promotional():
                self.cashier_show_non_promotional_only = not self.cashier_show_non_promotional_only
                self.cashier_show_promotional_only = False
                non_promo_button.config(text="Усі продукти" if self.cashier_show_non_promotional_only else "Продукти без акцій")
                promo_button.config(text="Продукти по акції")
                self.update_cashier_store_product_treeview()

            promo_button = tk.Button(button_frame, text="Продукти по акції", font=("Space Mono", 12), command=toggle_promotional)
            promo_button.pack(side='left', padx=(5, 0))

            non_promo_button = tk.Button(button_frame, text="Продукти без акцій", font=("Space Mono", 12), command=toggle_non_promotional)
            non_promo_button.pack(side='left', padx=(5, 0))

            sort_label = tk.Label(button_frame, text="Сортувати за:")
            sort_label.pack(side='left', padx=(10, 0))
            sort_menu = ttk.OptionMenu(button_frame, self.cashier_promotional_sort_var, "кількість", "кількість", "назва")
            sort_menu.pack(side='left', padx=(5, 10))

        if tab_text == 'Постійні клієнти':
            search_label = tk.Label(button_frame, text="Шукати за прізвищем")
            search_label.pack(side='left', padx=(5, 0))
            search_entry = tk.Entry(button_frame, textvariable=self.cashier_customer_search_var, font=("Space Mono", 12))
            search_entry.pack(side='left', padx=(5, 10), fill='x', expand=True)

        if tab_text == 'Чеки':
            start_date_label = tk.Label(button_frame, text="Дата початку (РРРР-ММ-ДД):")
            start_date_label.pack(side='left', padx=(5, 0))
            start_date_entry = tk.Entry(button_frame, textvariable=self.cashier_receipt_start_date_var, font=("Space Mono", 12), width=12)
            start_date_entry.pack(side='left', padx=(5, 10))

            end_date_label = tk.Label(button_frame, text="End Date (РРРР-ММ-ДД):")
            end_date_label.pack(side='left', padx=(5, 0))
            end_date_entry = tk.Entry(button_frame, textvariable=self.cashier_receipt_end_date_var, font=("Space Mono", 12), width=12)
            end_date_entry.pack(side='left', padx=(5, 10))

            print_button = tk.Button(
                button_frame,
                text="Надрукувати чек",
                font=("Space Mono", 12),
                command=self.print_receipt
            )
            print_button.pack(side='right', padx=(5, 0))

            details_button = tk.Button(
                button_frame,
                text="Деталі",
                font=("Space Mono", 12),
                command=lambda: self.show_receipt_details(self.treeviews['Чеки'])
            )
            details_button.pack(side='right', padx=(5, 0))

            today_button = tk.Button(
                button_frame,
                text="Сьогоднішні чеки",
                font=("Space Mono", 12),
                command=self.show_today_receipts
            )
            today_button.pack(side='right', padx=(5, 0))

        if tab_text == 'Постійні клієнти':
            add_button = tk.Button(button_frame, text="+", font=("Space Mono", 16, "bold"), width=3, command=lambda t=tab_text: self.add_new_item(t))
            add_button.pack(side='right', padx=(5, 0))

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

        if tab_text == 'Продукти':
            self.update_cashier_product_treeview()
        elif tab_text == 'Продукти у магазині':
            self.update_cashier_store_product_treeview()
        elif tab_text == 'Постійні клієнти':
            self.update_cashier_customer_treeview()
        elif tab_text == 'Чеки':
            self.update_cashier_receipt_treeview()

        if tab_text == 'Постійні клієнти':
            tree.bind('<Double-1>', lambda event, t=tab_text: self.on_cell_double_click(event, t))

    def show_receipt_details(self, tree):
        """Display detailed information about the selected receipt in a new window"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Виберіть чек для перегляду деталей")
            return

        check_number = tree.item(selected_item, 'values')[0]

        # Fetch basic receipt info
        check_info = self.db.fetch_filtered("SELECT * FROM [Check] WHERE check_number = ?", (check_number,))
        if not check_info:
            messagebox.showerror("Помилка", "Чек не знайдено")
            return

        check_info = check_info[0]
        cashier_id = check_info[1]
        print_date = check_info[3]
        sum_total = check_info[4]

        # Fetch items in the receipt
        items = self.db.fetch_filtered(
            """
            SELECT p.product_name, s.UPC, s.product_number, s.selling_price, (s.product_number * s.selling_price)
            FROM Sale s 
            JOIN Store_Product sp ON s.UPC = sp.UPC
            JOIN Product p ON sp.id_product = p.id_product 
            WHERE s.check_number = ?
            """,
            (check_number,)
        )

        if not items:
            messagebox.showerror("Помилка", "Не знайдено жодного товару для цього чека")
            return

        # Create a new window for receipt details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Деталі чека: {check_number}")
        details_window.geometry("600x400")

        # Display basic receipt info with corrected sum_total formatting
        info_label = tk.Label(details_window, text=f"Номер чека: {check_number}\nID Касира: {cashier_id}\nДата видачі: {print_date}\nСума: {sum_total:.2f}" if isinstance(sum_total, float) else f"Номер чека: {check_number}\nID Касира: {cashier_id}\nДата видачі: {print_date}\nСума: {sum_total}")
        info_label.pack(pady=10)

        # Create a table for items
        columns = ['Назва', 'UPC', 'Кількість', 'Ціна', 'Сума']
        item_tree = ttk.Treeview(details_window, columns=columns, show='headings')
        for col in columns:
            item_tree.heading(col, text=col)
            item_tree.column(col, width=100)

        # Populate the table with items
        for item in items:
            item_tree.insert('', 'end', values=item)

        item_tree.pack(fill='both', expand=True)


    def show_today_receipts(self):
        """Set the start and end date filters to today's date to show all receipts for today"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.cashier_receipt_start_date_var.set(today)
        self.cashier_receipt_end_date_var.set(today)

    def transliterate(self, text):
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z',
            'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
            'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ь': '', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z',
            'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
            'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
            'Ь': '', 'Ю': 'Yu', 'Я': 'Ya',
        }
        return ''.join(translit_dict.get(char, char) for char in text)

    def print_receipt(self):
        """Generate a PDF report for the selected receipt that looks like a real receipt"""
        tree = self.treeviews['Чеки']
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть чек для друку")
            return

        check_number = tree.item(selected_item, 'values')[0]

        # Fetch basic receipt info
        check_info = self.db.fetch_filtered("SELECT * FROM [Check] WHERE check_number = ?", (check_number,))
        if not check_info:
            messagebox.showerror("Помилка", "Чек не знайдено")
            return

        check_info = check_info[0]
        cashier_id = check_info[1]
        print_date = check_info[3]
        sum_total = check_info[4]

        # Fetch items in the receipt
        items = self.db.fetch_filtered(
            """
            SELECT p.product_name, s.UPC, s.product_number, s.selling_price, (s.product_number * s.selling_price)
            FROM Sale s 
            JOIN Store_Product sp ON s.UPC = sp.UPC
            JOIN Product p ON sp.id_product = p.id_product 
            WHERE s.check_number = ?
            """,
            (check_number,)
        )

        if not items:
            messagebox.showerror("Помилка", "Не знайдено жодного товару для цього чека")
            return


        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'DejaVuSans'
        styles['Title'].fontName = 'DejaVuSans'
        # Create PDF
        filename = f"receipt_{check_number}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']

        # Header
        elements.append(Paragraph("Check", title_style))
        elements.append(Paragraph(f"Check number: {check_number}", normal_style))
        elements.append(Paragraph(f"Date: {print_date}", normal_style))
        elements.append(Paragraph(f"Cashier: {cashier_id}", normal_style))
        elements.append(Paragraph("<br/>", normal_style))  # Empty line

        # Table data
        data = [["Product", "UPC", "Quantity", "Price", "Total"]]
        for item in items:
            product_name = item[0]
            product_name_translit = self.transliterate(product_name)
            data.append([product_name_translit, item[1], item[2], f"{item[3]:.2f}", f"{item[4]:.2f}"])

        # Create table
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Total
        pdv = sum_total * 0.2
        total_row = ["", "", "", "Total:", f"{sum_total:.2f}"]
        pdv_row = ["", "", "", "PDV:", f"{pdv:.2f}"]
        total_table = Table([total_row, pdv_row], colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])

        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(total_table)
        elements.append(Paragraph("<br/>", normal_style))  # Empty line

        # Footer
        elements.append(Paragraph("<br/>", normal_style))  # Empty line
        elements.append(Paragraph(f"Print time: {datetime.date.today().strftime('%Y-%m-%d')}", normal_style))

        # Build PDF
        doc.build(elements)
        messagebox.showinfo("Успіх", f"Чек збережено як {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardView(root, "1")
    root.mainloop()