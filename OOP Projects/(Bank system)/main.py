from database import create_tables
from gui.landing import BankingApp
import tkinter as tk

if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()
