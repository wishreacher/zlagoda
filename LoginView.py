import tkinter as tk
from tkinter import messagebox, font
import re


class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login System")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Register custom font with tkinter
        custom_font = font.Font(family="Avenir Next", size=12)
        title_font = font.Font(family="Avenir Next", size=18, weight="bold")
        small_font = font.Font(family="Avenir Next", size=10)

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

        # Remember me checkbox with custom font
        self.remember_var = tk.IntVar()
        self.remember_checkbutton = tk.Checkbutton(
            self.login_frame,
            text="Remember me",
            variable=self.remember_var,
            font=small_font
        )
        self.remember_checkbutton.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        # Login button with custom font
        self.login_button = tk.Button(
            self.login_frame,
            text="Login",
            font=custom_font,
            width=15,
            command=self.validate_login
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Register link with custom font
        self.register_link = tk.Label(
            self.login_frame,
            text="Don't have an account? Register here",
            font=small_font,
            fg="blue",
            cursor="hand2"
        )
        self.register_link.grid(row=5, column=0, columnspan=2)
        self.register_link.bind("<Button-1>", self.register)

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Simple validation
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        if not password:
            messagebox.showerror("Error", "Password cannot be empty")
            return

        # Check for valid username format (alphanumeric)
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            messagebox.showerror("Error", "Username must be alphanumeric")
            return

        # Check password length
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        # For demo purposes only - in a real app you would check against a database
        if username == "admin" and password == "password123":
            self.open_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_dashboard(self, username):
        """Open the dashboard window after successful login"""
        # Close the login window
        self.root.destroy()

        # Import here to avoid circular imports
        from DashboardView import DashboardView

        # Create and open the dashboard window
        dashboard_root = tk.Tk()
        dashboard_app = DashboardView(dashboard_root, username)
        dashboard_root.mainloop()

    def register(self, event):
        messagebox.showinfo("Register", "Registration functionality not implemented in this demo")


# Only run this if the file is executed directly (not imported)
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginPage(root)
    root.mainloop()