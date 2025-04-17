import tkinter as tk
from tkinter import messagebox, font

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login System")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Register custom font with tkinter
        custom_font = font.Font(family="Space Mono", size=12)
        title_font = font.Font(family="Space Mono", size=18, weight="bold")
        small_font = font.Font(family="Space Mono", size=10)

        # Create a frame for the login form
        self.login_frame = tk.Frame(root)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title label with custom font
        self.title_label = tk.Label(
            self.login_frame,
            text="User Login",
            font=title_font
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Username label with custom font
        self.username_label = tk.Label(
            self.login_frame,
            text="Username:",
            font=custom_font
        )
        self.username_label.grid(row=1, column=0, sticky="w", pady=5)

        # Entry field with custom font
        self.username_entry = tk.Entry(
            self.login_frame,
            font=custom_font,
            width=20,
            bd=1
        )
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)

        # Password label with custom font
        self.password_label = tk.Label(
            self.login_frame,
            text="Password:",
            font=custom_font
        )
        self.password_label.grid(row=2, column=0, sticky="w", pady=5)

        # Password entry with custom font
        self.password_entry = tk.Entry(
            self.login_frame,
            font=custom_font,
            width=20,
            show="*",
            bd=1
        )
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)

        # Login button with custom font
        self.login_button = tk.Button(
            self.login_frame,
            text="Login",
            font=custom_font,
            width=15,
            command=self.validate_login
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=20)

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        mock_database = {
            "cash1": {"password": "1", "role": "cashier"},
            "man1": {"password": "1", "role": "manager"}
        }

        # Validation
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        if not password:
            messagebox.showerror("Error", "Password cannot be empty")
            return

        # Check if user exists in the database
        user_data = mock_database.get(username)
        if user_data and user_data["password"] == password:
            role = user_data["role"]
            if role == "cashier":
                self.open_cashier_dashboard(username)
            elif role == "manager":
                self.open_manager_dashboard(username)
            else:
                messagebox.showerror("Error", "Unknown role")
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_cashier_dashboard(self, username):
        """Open the cashier dashboard"""
        self.root.destroy()
        from CashierDashboard import DashboardView
        dashboard_root = tk.Tk()
        dashboard_app = DashboardView(dashboard_root, username)
        dashboard_root.mainloop()

    def open_manager_dashboard(self, username):
        """Open the manager dashboard"""
        self.root.destroy()
        from ManagerDashboard import ManagerDashboard
        dashboard_root = tk.Tk()
        dashboard_app = ManagerDashboard(dashboard_root, username)
        dashboard_root.mainloop()

# Only run this if the file is executed directly (not imported)
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginPage(root)
    root.mainloop()