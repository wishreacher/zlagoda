import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font


class DashboardView:
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
        entity_columns = {
            'Продукти': ['назва', 'id продукту', 'id категорії', 'Опис'],
            'Продукти в магазині': ['UPC', 'id продукту', 'ціна', 'наявність', 'акційнний товар'],
            'Категорії': ['назва', 'номер категорії'],
            'Працівники': ['id працівника', 'ПІБ', 'посада', 'зарплата', 'дата народження', 'дата початку', 'адреса'],
            'Картки лояльності': ['номер картки', 'ПІБ', 'номер телефону', 'адреса', 'відсоток знижки'],
        }

        # Create tabs for each entity
        for entity, columns in entity_columns.items():
            self.create_tab(self.notebook, entity, columns)

    def create_tab(self, notebook, tab_text, columns):
        # Create a frame for the tab
        frame = tk.Frame(notebook)
        notebook.add(frame, text=tab_text)

        # Create the Treeview with specified columns
        tree = ttk.Treeview(frame, columns=columns, show='headings')

        # Set column headings and default width
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # Add scrollbars
        v_scrollbar = tk.Scrollbar(frame, orient='vertical', command=tree.yview)
        h_scrollbar = tk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Layout the Treeview and scrollbars using grid
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure the frame to expand the Treeview
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Mock data for the Treeview
        mock_data = {
            'Продукти': [
                ('Хліб', '101', '1', 'Свіжий хліб'),
                ('Молоко', '102', '2', '2% жирності'),
            ],
            'Продукти в магазині': [
                ('123456789012', '101', '20.50', '100', 'Ні'),
                ('123456789013', '102', '25.00', '50', 'Так'),
            ],
            'Категорії': [
                ('Харчові продукти', '1'),
                ('Напої', '2'),
            ],
            'Працівники': [
                ('1', 'Іван Іванов', 'Касир', '15000', '1990-01-01', '2020-05-01', 'Київ'),
                ('2', 'Петро Петренко', 'Менеджер', '25000', '1985-03-15', '2018-09-10', 'Львів'),
            ],
            'Картки лояльності': [
                ('1001', 'Олена Оленова', '0987654321', 'Одеса', '5%'),
                ('1002', 'Марія Марієнко', '0976543210', 'Харків', '10%'),
            ],
        }

        # Insert mock data into the Treeview
        for row in mock_data.get(tab_text, []):
            tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardView(root, "username")
    root.mainloop()