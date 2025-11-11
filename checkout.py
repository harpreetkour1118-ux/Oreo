import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
from database import record_order_effects
from datetime import datetime

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

    # Basic payment validation
    def _validate_payment_inputs(self):
        card = (self.card_entry.get() or "").replace(" ", "")
        cvv = (self.cvv_entry.get() or "").strip()
        exp = (self.exp_entry.get() or "").strip()

        if not card.isdigit() or len(card) not in (13, 15, 16):
            messagebox.showerror("Payment Error", "Invalid card number.")
            return False
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            messagebox.showerror("Payment Error", "Invalid CVV.")
            return False
        try:
            mm, yyyy = exp.split("/")
            mm = int(mm)
            yyyy = int(yyyy)
            if mm < 1 or mm > 12:
                raise ValueError
            # Consider card valid through the end of the month
            now = datetime.now()
            if (yyyy < now.year) or (yyyy == now.year and mm < now.month):
                messagebox.showerror("Payment Error", "Card is expired.")
                return False
        except Exception:
            messagebox.showerror("Payment Error", "Expiry must be in mm/yyyy format.")
            return False
        return True

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
        if not self._validate_payment_inputs():
            return

        db = connect_db()
        cursor = db.cursor()
        try:
            # Use transaction
            db.start_transaction()

            # Refresh latest cart from DB and verify stock
            cursor.execute(
                """
                SELECT c.product_id, c.quantity, p.name, p.price, p.stock
                FROM cart c
                JOIN product p ON c.product_id = p.product_id
                WHERE c.user_id = %s FOR UPDATE
                """,
                (self.user_id,),
            )
            items = cursor.fetchall()
            if not items:
                raise Exception("Cart became empty.")

            # Stock check
            insufficient = []
            order_total = 0.0
            for pid, qty, name, price, stock in items:
                if qty > (stock or 0):
                    insufficient.append(f"{name} (have {stock}, need {qty})")
                order_total += float(price) * int(qty)
            if insufficient:
                raise Exception("Insufficient stock for: \n- " + "\n- ".join(insufficient))

            # Create order (status Processing after payment)
            cursor.execute(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'Pending')",
                (self.user_id, order_total),
            )
            order_id = cursor.lastrowid

            # Insert order_items and decrement stock
            for pid, qty, name, price, stock in items:
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, pid, qty, price),
                )
                cursor.execute(
                    "UPDATE product SET stock = stock - %s WHERE product_id=%s",
                    (qty, pid),
                )

            # Payment record (assume completed for demo)
            cursor.execute(
                """
                INSERT INTO payment (order_id, payment_method, amount, status)
                VALUES (%s, 'Card', %s, 'Completed')
                """,
                (order_id, order_total),
            )

            # Clear cart
            cursor.execute("DELETE FROM cart WHERE user_id=%s", (self.user_id,))

            # Mark order Processing to indicate payment captured
            cursor.execute("UPDATE orders SET status='Processing' WHERE order_id=%s", (order_id,))

            db.commit()

            # Update analytics outside transaction
            try:
                record_order_effects(order_id)
            except Exception:
                pass

            messagebox.showinfo("Success", f"Order #{order_id} placed successfully!")
            self.destroy()
        except Exception as err:
            try:
                db.rollback()
            except Exception:
                pass
            messagebox.showerror("Checkout Failed", str(err))
        finally:
            db.close()
