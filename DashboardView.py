import tkinter as tk
from tkinter import font


class DashboardView:
    """Dashboard window that opens after successful login"""

    def __init__(self, root, username):
        self.root = root
        self.root.title("Dashboard")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Welcome message
        welcome_font = font.Font(family="Avenir Next", size=18, weight="bold")
        self.welcome_label = tk.Label(
            self.main_frame,
            text=f"Welcome, {username}!",
            font=welcome_font
        )
        self.welcome_label.pack(pady=20)

        # Dashboard content
        content_font = font.Font(family="Avenir Next", size=12)
        self.content_label = tk.Label(
            self.main_frame,
            text="You have successfully logged in to the system.",
            font=content_font
        )
        self.content_label.pack(pady=10)

        # Logout button
        self.logout_button = tk.Button(
            self.main_frame,
            text="Logout",
            font=content_font,
            command=self.logout
        )
        self.logout_button.pack(pady=30)

    def logout(self):
        """Handle logout action"""
        self.root.destroy()

        # Create new login window
        self.create_login_window()

    def create_login_window(self):
        """Create a new login window"""
        # Import here to avoid circular imports
        import tkinter as tk
        from LoginView import LoginPage

        root = tk.Tk()
        app = LoginPage(root)
        root.mainloop()


# For testing purposes only - this allows running this file directly
if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardView(root, "Test User")
    root.mainloop()