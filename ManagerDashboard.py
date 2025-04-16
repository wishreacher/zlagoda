import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font, simpledialog


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
        self.entity_columns = {
            'Продукти': ['назва', 'id продукту', 'id категорії', 'Опис'],
            'Продукти в магазині': ['UPC', 'id продукту', 'ціна', 'наявність', 'акційнний товар'],
            'Категорії': ['назва', 'номер категорії'],
            'Працівники': ['id працівника', 'ПІБ', 'посада', 'зарплата', 'дата народження', 'дата початку', 'адреса'],
            'Картки лояльності': ['номер картки', 'ПІБ', 'номер телефону', 'адреса', 'відсоток знижки'],
        }

        # Store treeviews for later reference
        self.treeviews = {}

        # Mock data for the Treeviews
        self.mock_data = {
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

        # Create tabs for each entity
        for entity, columns in self.entity_columns.items():
            self.create_tab(self.notebook, entity, columns)

    def create_tab(self, notebook, tab_text, columns):
        # Create a frame for the tab
        frame = tk.Frame(notebook)
        notebook.add(frame, text=tab_text)

        # Create a container frame that will hold the button and treeview
        container_frame = tk.Frame(frame)
        container_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Add the + button at the top right of the container
        add_button = tk.Button(
            container_frame,
            text="+",
            font=("Space Mono", 16, "bold"),
            width=3,
            command=lambda t=tab_text: self.add_new_item(t)
        )
        add_button.pack(side='top', anchor='ne', pady=(0, 5))

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

        # Insert mock data into the Treeview
        for row in self.mock_data.get(tab_text, []):
            tree.insert("", "end", values=row)

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

            # Add the new item to the treeview
            self.treeviews[tab_name].insert("", "end", values=new_values)

            # Also add to our mock data (in a real app, this would save to a database)
            self.mock_data[tab_name].append(new_values)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardView(root, "username")
    root.mainloop()