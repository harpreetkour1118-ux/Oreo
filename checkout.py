import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import io, requests, os

# DB Connect
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mkkapri",
        database="oreo"
    )

class CheckoutWindow(tk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.title("Checkout")
        self.geometry("1000x600")
        self.config(bg="white")
        self.user_id = user_id

        tk.Label(self, text="Checkout 🛒", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        tk.Button(self, text="Close", bg="#7B0000", fg="white", font=("Arial", 10, "bold"),
                  relief="flat", command=self.destroy).place(x=900, y=10)

        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(expand=True, fill="both", padx=20)

        # Receipt Panel
        receipt_frame = tk.Frame(main_frame, bg="#E5E5E5", width=450, height=500)
        receipt_frame.pack(side="left", padx=10, pady=10)
        receipt_frame.pack_propagate(False)

        tk.Label(receipt_frame, text="Receipt", bg="#E5E5E5", font=("Arial", 14, "bold")).pack(pady=10)

        self.items_box = tk.Frame(receipt_frame, bg="#E5E5E5")
        self.items_box.pack(anchor="nw", padx=20)

        self.total_label = tk.Label(receipt_frame, text="Total: $0.00",
                                    bg="#E5E5E5", font=("Arial", 14, "bold"))
        self.total_label.pack(side="bottom", pady=20)

        # Payment Panel
        pay_frame = tk.Frame(main_frame, bg="white")
        pay_frame.pack(side="left", padx=40)

        tk.Label(pay_frame, text="Payment Method", bg="white", font=("Arial", 14, "bold")).pack(anchor="nw")

        # Card Image
        try:
            img = Image.open("visa.png").resize((120, 80))
            card_img = ImageTk.PhotoImage(img)
        except:
            img = Image.new("RGB", (120, 80), "lightgrey")
            card_img = ImageTk.PhotoImage(img)

        tk.Label(pay_frame, image=card_img, bg="white").pack(pady=10)
        self.card_img = card_img

        # Card Inputs
        self.card_entry = tk.Entry(pay_frame, width=30, bg="#D3D3D3")
        self.card_entry.insert(0, "Card Number")
        self.card_entry.pack(pady=5)

        self.cvv_entry = tk.Entry(pay_frame, width=10, bg="#D3D3D3")
        self.cvv_entry.insert(0, "CVV")
        self.cvv_entry.pack(side="left", padx=5, pady=5)

        self.exp_entry = tk.Entry(pay_frame, width=15, bg="#D3D3D3")
        self.exp_entry.insert(0, "mm/yyyy")
        self.exp_entry.pack(side="left", padx=5)

        tk.Button(pay_frame, text="Checkout", bg="green", fg="white",
                  font=("Arial", 12, "bold"), relief="flat",
                  command=self.process_checkout).pack(pady=20)

        self.load_cart()

    # Load cart data
    def load_cart(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.name, p.price 
            FROM cart c JOIN product p 
            ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (self.user_id,))
        self.cart_items = cursor.fetchall()
        db.close()

        total = 0
        for p in self.cart_items:
            pid, qty, name, price = p
            total += price * qty
            tk.Label(self.items_box, text=f"{name} x {qty} ...... ${price*qty:.2f}",
                     bg="#E5E5E5", font=("Arial", 12)).pack(anchor="w")

        self.total = total
        self.total_label.config(text=f"Total: ${total:.2f}")

    # Process checkout
    def process_checkout(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return

        db = connect_db()
        cursor = db.cursor()

        # Insert order
        cursor.execute("INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'Pending')",
                       (self.user_id, self.total))
        order_id = cursor.lastrowid

        # Move cart items to order_items
        for p in self.cart_items:
            pid, qty, name, price = p
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, pid, qty, price))

        # Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id=%s", (self.user_id,))
        db.commit()
        db.close()

        messagebox.showinfo("Success", "Order placed successfully!")
        self.destroy()
