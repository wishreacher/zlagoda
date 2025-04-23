import tkinter as tk
from tkinter import messagebox, font
import sqlite3
from hashlib import sha256

from DatabaseHelper import DatabaseHelper


class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизація")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Initialize database helper
        self.db_helper = DatabaseHelper()

        # Ensure password field exists in database
        self.db_helper.create_password_field()

        custom_font = font.Font(family="Space Mono", size=12)
        title_font = font.Font(family="Space Mono", size=18, weight="bold")
        small_font = font.Font(family="Space Mono", size=10)

        self.login_frame = tk.Frame(root)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.title_label = tk.Label(
            self.login_frame,
            text="Авторизація",
            font=title_font
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        self.username_label = tk.Label(
            self.login_frame,
            text="Логін:",
            font=custom_font
        )
        self.username_label.grid(row=1, column=0, sticky="w", pady=5)

        self.username_entry = tk.Entry(
            self.login_frame,
            font=custom_font,
            width=20,
            bd=1
        )
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)

        self.password_label = tk.Label(
            self.login_frame,
            text="Пароль:",
            font=custom_font
        )
        self.password_label.grid(row=2, column=0, sticky="w", pady=5)

        self.password_entry = tk.Entry(
            self.login_frame,
            font=custom_font,
            width=20,
            show="*",
            bd=1
        )
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)

        self.login_button = tk.Button(
            self.login_frame,
            text="Увійти",
            font=custom_font,
            width=15,
            command=self.validate_login
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=20)

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Validation
        if not username:
            messagebox.showerror("Помилка", "Логін не може бути порожнім")
            return

        if not password:
            messagebox.showerror("Помилка", "Пароль не може бути порожньою")
            return

        # Authenticate using database
        user_data = self.db_helper.validate_login(username, password)

        if user_data:
            role = user_data["role"]
            if role.lower() == "cashier":
                self.open_cashier_dashboard(username)
            elif role.lower() == "manager":
                self.open_manager_dashboard(username)
            else:
                messagebox.showerror("Помилка", "Невідома роль")
        else:
            messagebox.showerror("Помилка", "Неправильний логін або пароль")

    def open_cashier_dashboard(self, username):
        self.root.destroy()
        from CashierDashboard import DashboardView
        dashboard_root = tk.Tk()
        dashboard_app = DashboardView(dashboard_root, username)
        dashboard_root.mainloop()

    def open_manager_dashboard(self, username):
        self.root.destroy()
        from ManagerDashboard import ManagerDashboard
        dashboard_root = tk.Tk()
        dashboard_app = ManagerDashboard(dashboard_root, username)
        dashboard_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginPage(root)
    root.mainloop()