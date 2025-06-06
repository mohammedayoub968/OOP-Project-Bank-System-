# models.py
import bcrypt
from database import cursor, conn
import datetime

class User:
    def __init__(self, name, national_id, phone_number, password):
        self.name = name
        self.national_id = national_id
        self.phone_number = phone_number
        self.password = self.hash_password(password)
        self.id = None

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def save_to_db(self, user_type):
        cursor.execute(
            '''INSERT INTO users (name, national_id, phone_number, password, user_type) 
               VALUES (?, ?, ?, ?, ?)''',
            (self.name, self.national_id, self.phone_number, self.password, user_type)
        )
        conn.commit()
        self.id = cursor.lastrowid

class Customer(User):
    def __init__(self, name, national_id, phone_number, password):
        super().__init__(name, national_id, phone_number, password)

    def save_to_db(self):
        super().save_to_db("customer")
        cursor.execute(
            "INSERT INTO customers (user_id, credit, wallet_balance) VALUES (?, ?, ?)",
            (self.id, 0.0, 0.0)
        )
        conn.commit()

    def deposit_to_credit(self, amount):
        cursor.execute("UPDATE customers SET credit = credit + ? WHERE user_id = ?", (amount, self.id))
        self.log_transaction("credit_deposit", amount, "success")
        conn.commit()

    def deposit_to_wallet(self, amount):
        cursor.execute("UPDATE customers SET wallet_balance = wallet_balance + ? WHERE user_id = ?", (amount, self.id))
        self.log_transaction("wallet_deposit", amount, "success")
        conn.commit()

    def withdraw_from_credit(self, amount):
        cursor.execute("SELECT credit FROM customers WHERE user_id = ?", (self.id,))
        current = cursor.fetchone()[0]
        if current >= amount:
            cursor.execute("UPDATE customers SET credit = credit - ? WHERE user_id = ?", (amount, self.id))
            self.log_transaction("credit_withdraw", amount, "success")
            conn.commit()
        else:
            self.log_transaction("credit_withdraw", amount, "failed")

    def withdraw_from_wallet(self, amount):
        cursor.execute("SELECT wallet_balance FROM customers WHERE user_id = ?", (self.id,))
        current = cursor.fetchone()[0]
        if current >= amount:
            cursor.execute("UPDATE customers SET wallet_balance = wallet_balance - ? WHERE user_id = ?", (amount, self.id))
            self.log_transaction("wallet_withdraw", amount, "success")
            conn.commit()
        else:
            self.log_transaction("wallet_withdraw", amount, "failed")

    def transfer_wallet_to_credit(self, amount):
        cursor.execute("SELECT wallet_balance FROM customers WHERE user_id = ?", (self.id,))
        current = cursor.fetchone()[0]
        if current >= amount:
            cursor.execute("UPDATE customers SET wallet_balance = wallet_balance - ?, credit = credit + ? WHERE user_id = ?", (amount, amount, self.id))
            self.log_transaction("wallet_to_credit", amount, "success")
            conn.commit()
        else:
            self.log_transaction("wallet_to_credit", amount, "failed")

    def transfer_credit_to_wallet(self, amount):
        cursor.execute("SELECT credit FROM customers WHERE user_id = ?", (self.id,))
        current = cursor.fetchone()[0]
        if current >= amount:
            cursor.execute("UPDATE customers SET credit = credit - ?, wallet_balance = wallet_balance + ? WHERE user_id = ?", (amount, amount, self.id))
            self.log_transaction("credit_to_wallet", amount, "success")
            conn.commit()
        else:
            self.log_transaction("credit_to_wallet", amount, "failed")

    def log_transaction(self, type, amount, status):
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.id, type, amount, status, timestamp))
        conn.commit()

class Admin(User):
    def __init__(self, name, national_id, phone_number, password):
        super().__init__(name, national_id, phone_number, password)

    def save_to_db(self):
        super().save_to_db("admin")

    def reset_user_password(self, user_id, new_password):
        hashed = self.hash_password(new_password)
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        conn.commit()

    def lock_user_account(self, user_id):
        cursor.execute("UPDATE users SET is_locked = 1 WHERE id = ?", (user_id,))
        conn.commit()

    def unlock_user_account(self, user_id):
        cursor.execute("UPDATE users SET is_locked = 0 WHERE id = ?", (user_id,))
        conn.commit()

    def delete_user(self, user_id):
        cursor.execute("DELETE FROM customers WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    def view_all_users(self):
        cursor.execute("SELECT id, name, national_id, phone_number FROM users WHERE user_type = 'customer'")
        return cursor.fetchall()
