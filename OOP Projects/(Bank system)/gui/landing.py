import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.models import Customer, Admin, User
from database import create_tables, cursor

create_tables()

class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nile Valley Bank System")
        self.current_user = None
        self.build_role_selection()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_role_selection(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()
        ttk.Label(frame, text="Welcome to Nile Valley Bank System", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Admin", width=20, command=self.build_admin_choice).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(frame, text="Customer", width=20, command=self.build_customer_signin).grid(row=1, column=1, padx=10, pady=5)

    def build_admin_choice(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()
        ttk.Label(frame, text="Admin Portal", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Sign Up", width=20, command=self.build_admin_signup).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(frame, text="Sign In", width=20, command=self.build_admin_signin).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(frame, text="Back", width=20, command=self.build_role_selection).grid(row=2, column=0, columnspan=2, pady=10)

    def build_admin_signup(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()
        ttk.Label(frame, text="Admin Sign Up", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        labels = ["Name", "National ID", "Phone Number", "Password"]
        entries = []
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label+":").grid(row=i+1, column=0, sticky="e", pady=5)
            entry = ttk.Entry(frame, show="*" if label=="Password" else None)
            entry.grid(row=i+1, column=1, pady=5)
            entries.append(entry)
        def signup_action():
            name, nid, phone, password = [e.get() for e in entries]
            if not all([name, nid, phone, password]):
                messagebox.showerror("Error", "All fields are required.")
                return
            try:
                admin = Admin(name, nid, phone, password)
                admin.save_to_db()
                messagebox.showinfo("Success", "Admin registered successfully!")
                self.build_admin_signin()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to register admin: {e}")
        ttk.Button(frame, text="Sign Up", command=signup_action).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Back", command=self.build_admin_choice).grid(row=6, column=0, columnspan=2)

    def build_admin_signin(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()
        ttk.Label(frame, text="Admin Sign In", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="Name:").grid(row=1, column=0, sticky="e", pady=5)
        name_entry = ttk.Entry(frame)
        name_entry.grid(row=1, column=1, pady=5)
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        password_entry = ttk.Entry(frame, show="*")
        password_entry.grid(row=2, column=1, pady=5)
        def signin_action():
            name = name_entry.get()
            password = password_entry.get()
            cursor.execute("SELECT * FROM users WHERE name=? AND user_type='admin'", (name,))
            row = cursor.fetchone()
            if row and Admin.verify_password(password, row[4]):
                self.current_user = Admin(row[1], row[2], row[3], row[4])
                self.current_user.id = row[0]
                self.load_admin_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials.")
        ttk.Button(frame, text="Sign In", command=signin_action).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Back", command=self.build_admin_choice).grid(row=4, column=0, columnspan=2)

    def build_customer_signin(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()
        ttk.Label(frame, text="Customer Sign In", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="Name:").grid(row=1, column=0, sticky="e", pady=5)
        name_entry = ttk.Entry(frame)
        name_entry.grid(row=1, column=1, pady=5)
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        password_entry = ttk.Entry(frame, show="*")
        password_entry.grid(row=2, column=1, pady=5)
        def signin_action():
            name = name_entry.get()
            password = password_entry.get()
            cursor.execute("SELECT * FROM users WHERE name=? AND user_type='customer'", (name,))
            row = cursor.fetchone()
            if row and Customer.verify_password(password, row[4]):
                self.current_user = Customer(row[1], row[2], row[3], row[4])
                self.current_user.id = row[0]
                self.load_customer_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials.")
        ttk.Button(frame, text="Sign In", command=signin_action).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Back", command=self.build_role_selection).grid(row=4, column=0, columnspan=2)

    def load_admin_dashboard(self):
        from gui.admin_views import AdminDashboard
        self.clear_window()
        AdminDashboard(self.root, self.current_user, self.build_role_selection)

    def load_customer_dashboard(self):
        from gui.customer_views import CustomerDashboard
        self.clear_window()
        CustomerDashboard(self.root, self.current_user, self.build_role_selection)

if __name__ == '__main__':
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()
