import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.models import Admin, Customer
from database import cursor
from utils.validators import validate_password_strength
from utils.logger import log_action

class AdminDashboard:
    def __init__(self, root, user, logout_callback):
        self.root = root
        self.user = user
        self.logout_callback = logout_callback
        self.build_ui()

    def build_ui(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Welcome Admin {self.user.name}", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, pady=10)

        # Buttons
        ttk.Button(frame, text="Add Customer", command=self.add_customer).grid(row=1, column=0, pady=5)
        ttk.Button(frame, text="Reset Password", command=self.reset_password).grid(row=1, column=1, pady=5)
        ttk.Button(frame, text="Lock Account", command=self.lock_account).grid(row=1, column=2, pady=5)
        ttk.Button(frame, text="Unlock Account", command=self.unlock_account).grid(row=1, column=3, pady=5)
        ttk.Button(frame, text="Delete User", command=self.delete_user).grid(row=2, column=0, pady=5)
        ttk.Button(frame, text="Logout", command=self.logout).grid(row=2, column=3, pady=5)

        # Customer List Treeview
        ttk.Label(frame, text="Registered Customers:", font=("Arial", 12, "underline")).grid(row=3, column=0, columnspan=4, sticky="w", pady=(10,5))
        self.tree = ttk.Treeview(frame, columns=("ID", "Name", "National ID", "Phone"), show="headings", height=10)
        for col in ("ID", "Name", "National ID", "Phone"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.grid(row=4, column=0, columnspan=4, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=4, column=4, sticky="ns")

        self.populate_users()

        frame.grid_rowconfigure(4, weight=1)
        frame.grid_columnconfigure(3, weight=1)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def populate_users(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        users = self.user.view_all_users()
        for u in users:
            self.tree.insert("", "end", values=(u[0], u[1], u[2], u[3]))

    def add_customer(self):
        dlg = AddCustomerDialog(self.root)
        self.root.wait_window(dlg.top)
        if dlg.result:
            name, nid, phone, password = dlg.result
            if not validate_password_strength(password):
                messagebox.showerror("Weak Password", "Password is not strong enough.")
                return
            new_customer = Customer(name, nid, phone, password)
            try:
                new_customer.save_to_db()
                messagebox.showinfo("Success", "Customer added")
                self.populate_users()  # Refresh the user list after adding
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {e}")

    def reset_password(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select User", "Please select a user to reset password.")
            return
        user_id = self.tree.item(selected_item, "values")[0]
        new_password = simpledialog.askstring("Reset Password", "Enter new password:")
        if new_password:
            if validate_password_strength(new_password):
                try:
                    cursor.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
                    messagebox.showinfo("Success", "Password reset successfully.")
                    log_action(f"Admin {self.user.name} reset password for user ID {user_id}.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset password: {e}")
            else:
                messagebox.showerror("Weak Password", "Password is not strong enough.")

    def lock_account(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select User", "Please select a user to lock account.")
            return
        user_id = self.tree.item(selected_item, "values")[0]
        try:
            cursor.execute("UPDATE users SET is_locked=1 WHERE id=?", (user_id,))
            messagebox.showinfo("Success", "Account locked successfully.")
            log_action(f"Admin {self.user.name} locked account for user ID {user_id}.")
            self.populate_users()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to lock account: {e}")

    def unlock_account(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select User", "Please select a user to unlock account.")
            return
        user_id = self.tree.item(selected_item, "values")[0]
        try:
            cursor.execute("UPDATE users SET is_locked=0 WHERE id=?", (user_id,))
            messagebox.showinfo("Success", "Account unlocked successfully.")
            log_action(f"Admin {self.user.name} unlocked account for user ID {user_id}.")
            self.populate_users()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unlock account: {e}")

    def delete_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select User", "Please select a user to delete.")
            return
        user_id = self.tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?")
        if confirm:
            try:
                cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                messagebox.showinfo("Success", "User deleted successfully.")
                log_action(f"Admin {self.user.name} deleted user ID {user_id}.")
                self.populate_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.logout_callback()

class AddCustomerDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Customer")
        self.top.grab_set()

        # Customer details
        ttk.Label(self.top, text="Name:").grid(row=0, column=0, padx=10, pady=10)
        self.name_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.top, text="National ID:").grid(row=1, column=0, padx=10, pady=10)
        self.nid_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.nid_var).grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.top, text="Phone:").grid(row=2, column=0, padx=10, pady=10)
        self.phone_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.phone_var).grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.top, text="Password:").grid(row=3, column=0, padx=10, pady=10)
        self.password_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.password_var, show="*").grid(row=3, column=1, padx=10, pady=10)

        # Buttons
        ttk.Button(self.top, text="Add", command=self.add_customer).grid(row=4, column=0, padx=10, pady=10)
        ttk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=4, column=1, padx=10, pady=10)

        self.result = None

    def add_customer(self):
        name = self.name_var.get()
        nid = self.nid_var.get()
        phone = self.phone_var.get()
        password = self.password_var.get()
        if name and nid and phone and password:
            self.result = (name, nid, phone, password)
            self.top.destroy()
        else:
            messagebox.showwarning("Incomplete Data", "Please fill in all fields.")
