import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.models import Customer
from database import cursor
from utils.session import SessionManager
from utils.logger import log_action
import datetime

class CustomerDashboard:
    def __init__(self, root, user, logout_callback):
        self.root = root
        self.user = user
        self.logout_callback = logout_callback
        self.session = SessionManager(self.root, self.logout)
        self.build_ui()

    def build_ui(self):
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Welcome, {self.user.name}", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, pady=5)

        # Balance Display
        self.balance_var = tk.StringVar()
        self.update_balances()
        ttk.Label(frame, textvariable=self.balance_var, font=("Arial", 12)).grid(row=1, column=0, columnspan=4, pady=5)

        # Transaction History Table
        ttk.Label(frame, text="Transaction History:", font=("Arial", 12, "underline")).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10,2))
        self.tree = ttk.Treeview(frame, columns=("Type", "Amount", "Status", "Timestamp"), show="headings", height=10)
        for col in ("Type", "Amount", "Status", "Timestamp"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.grid(row=3, column=0, columnspan=4, sticky="nsew")

        self.populate_transactions()

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=3, column=4, sticky="ns")

        # Deposit and Withdraw Buttons with Amount input dialogs
        ttk.Button(frame, text="Deposit to Credit", command=self.deposit_credit).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Deposit to Wallet", command=self.deposit_wallet).grid(row=4, column=1, pady=10)
        ttk.Button(frame, text="Withdraw from Credit", command=self.withdraw_credit).grid(row=4, column=2, pady=10)
        ttk.Button(frame, text="Withdraw from Wallet", command=self.withdraw_wallet).grid(row=4, column=3, pady=10)
        ttk.Button(frame, text="Wallet → Credit", command=self.wallet_to_credit).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Credit → Wallet", command=self.credit_to_wallet).grid(row=5, column=2, columnspan=2, pady=10)
        ttk.Button(frame, text="Logout", command=self.logout).grid(row=6, column=0, columnspan=4, pady=15)

        # Configure grid weights
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        self.session.start()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def update_balances(self):
        cursor.execute("SELECT credit, wallet_balance FROM customers WHERE user_id = ?", (self.user.id,))
        credit, wallet = cursor.fetchone()
        self.balance_var.set(f"Credit: ${credit:.2f} | Wallet: ${wallet:.2f}")

    def populate_transactions(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        cursor.execute("SELECT type, amount, status, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (self.user.id,))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def get_amount(self, prompt):
        try:
            val = simpledialog.askstring("Amount", prompt)
            if val is None:
                return None
            amount = float(val)
            if amount <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive amount.")
                return None
            return amount
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return None

    def deposit_credit(self):
        amount = self.get_amount("Enter amount to deposit to credit:")
        if amount is not None:
            self.user.deposit_to_credit(amount)
            self.update_balances()
            self.populate_transactions()
            log_action(self.user.id, "deposit_to_credit", "success")

    def deposit_wallet(self):
        amount = self.get_amount("Enter amount to deposit to wallet:")
        if amount is not None:
            self.user.deposit_to_wallet(amount)
            self.update_balances()
            self.populate_transactions()
            log_action(self.user.id, "deposit_to_wallet", "success")

    def withdraw_credit(self):
        amount = self.get_amount("Enter amount to withdraw from credit:")
        if amount is not None:
            cursor.execute("SELECT credit FROM customers WHERE user_id = ?", (self.user.id,))
            current = cursor.fetchone()[0]
            if amount > current:
                messagebox.showerror("Insufficient Funds", "You do not have enough credit balance.")
                log_action(self.user.id, "withdraw_from_credit", "failed")
            else:
                self.user.withdraw_from_credit(amount)
                self.update_balances()
                self.populate_transactions()
                log_action(self.user.id, "withdraw_from_credit", "success")

    def withdraw_wallet(self):
        amount = self.get_amount("Enter amount to withdraw from wallet:")
        if amount is not None:
            cursor.execute("SELECT wallet_balance FROM customers WHERE user_id = ?", (self.user.id,))
            current = cursor.fetchone()[0]
            if amount > current:
                messagebox.showerror("Insufficient Funds", "You do not have enough wallet balance.")
                log_action(self.user.id, "withdraw_from_wallet", "failed")
            else:
                self.user.withdraw_from_wallet(amount)
                self.update_balances()
                self.populate_transactions()
                log_action(self.user.id, "withdraw_from_wallet", "success")

    def wallet_to_credit(self):
        amount = self.get_amount("Enter amount to transfer from Wallet to Credit:")
        if amount is not None:
            cursor.execute("SELECT wallet_balance FROM customers WHERE user_id = ?", (self.user.id,))
            wallet_balance = cursor.fetchone()[0]
            if amount > wallet_balance:
                messagebox.showerror("Insufficient Funds", "You do not have enough wallet balance.")
                log_action(self.user.id, "wallet_to_credit", "failed")
            else:
                # Perform the transfer
                cursor.execute("UPDATE customers SET wallet_balance = wallet_balance - ?, credit = credit + ? WHERE user_id = ?", (amount, amount, self.user.id))
                cursor.execute("INSERT INTO transactions (user_id, type, amount, status, timestamp) VALUES (?, 'Transfer to Credit', ?, 'Completed', ?)", (self.user.id, amount, datetime.datetime.now()))
                self.update_balances()
                self.populate_transactions()
                log_action(self.user.id, "wallet_to_credit", "success")

    def credit_to_wallet(self):
        amount = self.get_amount("Enter amount to transfer from Credit to Wallet:")
        if amount is not None:
            cursor.execute("SELECT credit FROM customers WHERE user_id = ?", (self.user.id,))
            credit_balance = cursor.fetchone()[0]
            if amount > credit_balance:
                messagebox.showerror("Insufficient Funds", "You do not have enough credit balance.")
                log_action(self.user.id, "credit_to_wallet", "failed")
            else:
                # Perform the transfer
                cursor.execute("UPDATE customers SET credit = credit - ?, wallet_balance = wallet_balance + ? WHERE user_id = ?", (amount, amount, self.user.id))
                cursor.execute("INSERT INTO transactions (user_id, type, amount, status, timestamp) VALUES (?, 'Transfer to Wallet', ?, 'Completed', ?)", (self.user.id, amount, datetime.datetime.now()))
                self.update_balances()
                self.populate_transactions()
                log_action(self.user.id, "credit_to_wallet", "success")

    def logout(self):
        self.session.stop()
        self.logout_callback()
