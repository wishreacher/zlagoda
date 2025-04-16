import tkinter as tk

class DashboardView:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Cashier Dashboard")
        self.root.geometry("1200x800")
        self.username = username

        role_label = tk.Label(
            self.root,
            text="Ваша роль: Кассир",
            font=("Space Mono", 12),
            anchor="w"
        )
        role_label.pack(anchor="nw", padx=10, pady=10)