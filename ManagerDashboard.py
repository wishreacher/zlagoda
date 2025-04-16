import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font, simpledialog, messagebox


class DashboardView:
    show_cashiers_only = False  # Class variable to track the toggle state
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
            'Працівники': ['id працівника', 'прізвище', 'імʼя', 'по-батькові', 'посада', 'зарплата', 'дата народження', 'дата початку', 'адреса'],
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
                ('1', 'Іванов', 'Іван', 'Іванович', 'Касир', '15000', '1990-01-01', '2020-05-01', 'Київ'),
                ('2', 'Петренко', 'Петро', 'Петрович', 'Менеджер', '25000', '1985-03-15', '2018-09-10', 'Львів'),
                ('3', 'Коваленко', 'Анна', 'Сергіївна', 'Касир', '16000', '1995-07-12', '2021-03-15', 'Київ'),
                ('4', 'Шевченко', 'Зоя', 'Олександрівна', 'Консультант', '14000', '1992-11-05', '2022-01-10', 'Одеса'),
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

        # Create a container frame that will hold the buttons and treeview
        container_frame = tk.Frame(frame)
        container_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create a button frame for the top
        button_frame = tk.Frame(container_frame)
        button_frame.pack(side='top', fill='x', pady=(0, 5))

        # Add the toggle button for cashiers (only for Працівники tab)
        if tab_text == 'Працівники':
            self.show_cashiers_only = False  # Toggle state

            def toggle_cashiers():
                self.show_cashiers_only = not self.show_cashiers_only
                toggle_button.config(
                    text="Показати всіх" if self.show_cashiers_only else "Показати касирів"
                )
                update_treeview()

            toggle_button = tk.Button(
                button_frame,
                text="Показати касирів",
                font=("Space Mono", 12),
                command=toggle_cashiers
            )
            toggle_button.pack(side='left', padx=(5, 0))

        # Add the + button (aligned right)
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

        # Function to update the Treeview based on the toggle state
        def update_treeview():
            tree.delete(*tree.get_children())  # Clear existing rows
            data = self.mock_data.get(tab_text, [])
            if self.show_cashiers_only:
                data = [row for row in data if row[4] == 'Касир']  # Filter by "Касир"
            for row in data:
                tree.insert("", "end", values=row)

        # Insert initial data into the Treeview
        update_treeview()

        # Bind double-click event for editing cells
        tree.bind('<Double-1>', lambda event, t=tab_text: self.on_cell_double_click(event, t))

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

            # Resort if we're in the Працівники tab
            if tab_name == 'Працівники':
                pib_index = self.entity_columns[tab_name].index('прізвище')
                self.sort_treeview(tab_name, 'прізвище', pib_index)

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

            # Remove from mock data
            # Convert the tuple from item_values to match the format in mock_data
            item_values_tuple = tuple(item_values)
            if item_values_tuple in self.mock_data[tab_name]:
                self.mock_data[tab_name].remove(item_values_tuple)

    def on_cell_double_click(self, event, tab_name):
        """Handle double-click on a cell to edit its value"""
        tree = self.treeviews[tab_name]

        # Get the clicked region (check if it's on a cell, not a header)
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
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
                old_values_tuple = tree.item(item, 'values')
                if old_values_tuple in self.mock_data[tab_name]:
                    index = self.mock_data[tab_name].index(old_values_tuple)
                    self.mock_data[tab_name][index] = tuple(values)

                # Resort if we're in the Працівники tab and changed the ПІБ field
                if tab_name == 'Працівники' and column_name == 'прізвище':
                    pib_index = self.entity_columns[tab_name].index('прізвище')
                    self.sort_treeview(tab_name, 'прізвище', pib_index)

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
        if tab_name == 'Працівники' and column == 'прізвище':
            data.sort(key=lambda x: x[0][1])  # Sort by прізвище (index 1)
        else:
            data.sort(key=lambda x: x[0][column_index])

        # Rearrange items in the treeview
        for index, (values, item) in enumerate(data):
            tree.move(item, '', index)


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardView(root, "username")
    root.mainloop()