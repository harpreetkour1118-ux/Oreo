import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
from database import get_most_sold_products, get_least_sold_products

# ---------- DB Connection ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mkkapri",
        database="oreo"
    )

# Predefined Categories
CATEGORIES = [
    "Phone",
    "Laptop",
    "Tablets",
    "Gaming Console",
    "Earphone",
    "PC Accessory"
]

# Fetch or Create Category ID
def get_category_id(category_name):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT category_id FROM category WHERE name=%s", (category_name,))
    row = cursor.fetchone()

    if row:
        db.close()
        return row[0]

    # Create new category
    cursor.execute("INSERT INTO category(name) VALUES(%s)", (category_name,))
    db.commit()
    new_id = cursor.lastrowid

    db.close()
    return new_id



# ---------- ADMIN PANEL ----------
class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Oreo Admin Panel")
        self.state("zoomed")
        self.config(bg="white")

        # Logo
        try:
            img = Image.open("OREO.png")
            img = img.resize((80, 80))
            self.logo = ImageTk.PhotoImage(img)
        except:
            self.logo = None

        # Header
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=20, pady=10)

        if self.logo:
            tk.Label(header, image=self.logo, bg="white").pack(side="left")

        tk.Label(header, text="Oreo Admin", font=("Arial", 22, "bold"),
                 bg="white").pack(side="left", padx=10)

        tk.Button(header, text="Exit", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=self.destroy).pack(side="right")

        # Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Product", bg="green", fg="white",
                  font=("Arial", 12, "bold"), command=self.add_product_window).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Update Product", bg="#B8860B", fg="white",
                  font=("Arial", 12, "bold"), command=self.update_product_window).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Delete Product", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=self.delete_product_window).grid(row=0, column=2, padx=10)

        tk.Button(btn_frame, text="Manage Users", bg="#1E90FF", fg="white",
                  font=("Arial", 12, "bold"), command=self.open_users_window).grid(row=0, column=3, padx=10)

        tk.Button(btn_frame, text="Insights Dashboard", bg="#2E8B57", fg="white",
                  font=("Arial", 12, "bold"), command=self.open_insights_window).grid(row=0, column=4, padx=10)

        # Product Table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Price", "Stock"),
                                 show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Stock", text="Stock")

        self.tree.column("ID", width=60)
        self.tree.column("Name", width=300)
        self.tree.column("Price", width=120)
        self.tree.column("Stock", width=120)

        self.tree.pack(fill="both", pady=10)
        self.load_products()



    # Load Products in Table
    def load_products(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT product_id, name, price, stock FROM product")
        rows = cursor.fetchall()
        db.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)



    # ---------- ADD PRODUCT ----------
    def add_product_window(self):
        win = tk.Toplevel(self)
        win.title("Add Product")
        win.geometry("450x580")

        tk.Label(win, text="Add Product", font=("Arial", 16, "bold")).pack(pady=10)

        fields = ["Name", "Description", "Price", "Stock", "Image URL"]
        entries = {}

        for f in fields:
            tk.Label(win, text=f).pack()
            e = tk.Entry(win, width=35)
            e.pack(pady=3)
            entries[f] = e

        # Category Radio Buttons
        tk.Label(win, text="Category", font=("Arial", 12, "bold")).pack(pady=10)

        category_var = tk.StringVar(value=CATEGORIES[0])
        for c in CATEGORIES:
            tk.Radiobutton(win, text=c, variable=category_var, value=c).pack(anchor="w")

        def save():
            name, description, price, stock, image_url = [entries[f].get() for f in fields]

            if name == "" or price == "" or stock == "":
                messagebox.showerror("Error", "Name, Price, and Stock are required!")
                return

            category_id = get_category_id(category_var.get())

            db = connect_db()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO product (name, description, price, stock, category_id, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, description, price, stock, category_id, image_url))

            db.commit()
            db.close()

            messagebox.showinfo("Success", "Product Added Successfully")
            win.destroy()
            self.load_products()

        tk.Button(win, text="Add Product", bg="green", fg="white",
                  font=("Arial", 12, "bold"), command=save).pack(pady=20)



    # ---------- UPDATE PRODUCT ----------
    def update_product_window(self):
        win = tk.Toplevel(self)
        win.title("Update Product")
        win.geometry("450x580")

        tk.Label(win, text="Enter Product ID to Update").pack(pady=5)
        id_row = tk.Frame(win)
        id_row.pack(pady=5)
        id_entry = tk.Entry(id_row, width=18)
        id_entry.pack(side="left", padx=(0, 8))
        load_btn = tk.Button(id_row, text="Load Details")
        load_btn.pack(side="left")

        fields = ["Name", "Description", "Price", "Stock", "Image URL"]
        entries = {}

        for f in fields:
            tk.Label(win, text=f).pack()
            e = tk.Entry(win, width=35)
            e.pack(pady=3)
            entries[f] = e

        # Category Radio Buttons
        tk.Label(win, text="Category", font=("Arial", 12, "bold")).pack(pady=10)

        category_var = tk.StringVar(value=CATEGORIES[0])
        for c in CATEGORIES:
            tk.Radiobutton(win, text=c, variable=category_var, value=c).pack(anchor="w")

        def load_product():
            pid = id_entry.get().strip()
            if pid == "":
                messagebox.showerror("Error", "Product ID Required")
                return
            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute(
                    "SELECT name, description, price, stock, image_url, category_id FROM product WHERE product_id=%s",
                    (pid,),
                )
                row = cur.fetchone()
                if not row:
                    db.close()
                    messagebox.showerror("Not Found", f"No product with ID {pid}")
                    return
                name, description, price, stock, image_url, category_id = row
                # Populate fields
                entries["Name"].delete(0, tk.END); entries["Name"].insert(0, name or "")
                entries["Description"].delete(0, tk.END); entries["Description"].insert(0, description or "")
                entries["Price"].delete(0, tk.END); entries["Price"].insert(0, str(price))
                entries["Stock"].delete(0, tk.END); entries["Stock"].insert(0, str(stock))
                entries["Image URL"].delete(0, tk.END); entries["Image URL"].insert(0, image_url or "")

                # Resolve category name
                cat_name = None
                if category_id:
                    try:
                        cur.execute("SELECT name FROM category WHERE category_id=%s", (category_id,))
                        c = cur.fetchone()
                        if c and c[0] in CATEGORIES:
                            cat_name = c[0]
                    except Exception:
                        pass
                category_var.set(cat_name or CATEGORIES[0])
                db.close()
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))

        load_btn.config(command=load_product)
        id_entry.bind("<Return>", lambda e: load_product())

        def update():
            pid = id_entry.get()
            if pid == "":
                messagebox.showerror("Error", "Product ID Required")
                return

            name, description, price, stock, image_url = [entries[f].get() for f in fields]
            # Basic validation
            if name.strip() == "" or price.strip() == "" or stock.strip() == "":
                messagebox.showerror("Error", "Name, Price and Stock are required")
                return
            try:
                price_val = float(price)
                stock_val = int(stock)
            except ValueError:
                messagebox.showerror("Error", "Price must be a number and Stock must be an integer")
                return
            category_id = get_category_id(category_var.get())

            db = connect_db()
            cursor = db.cursor()

            cursor.execute("""
                UPDATE product
                SET name=%s, description=%s, price=%s, stock=%s, category_id=%s, image_url=%s
                WHERE product_id=%s
            """, (name, description, price_val, stock_val, category_id, image_url, pid))

            db.commit()
            db.close()

            messagebox.showinfo("Updated", "Product Updated Successfully")
            win.destroy()
            self.load_products()

        tk.Button(win, text="Update Product", bg="#B8860B", fg="white",
                  font=("Arial", 12, "bold"), command=update).pack(pady=20)



    # ---------- DELETE PRODUCT ----------
    def delete_product_window(self):
        win = tk.Toplevel(self)
        win.title("Delete Product")
        win.geometry("300x200")

        tk.Label(win, text="Enter Product ID to Delete").pack(pady=10)
        id_entry = tk.Entry(win, width=20)
        id_entry.pack(pady=10)

        def delete():
            pid = id_entry.get()
            if pid == "":
                messagebox.showerror("Error", "Product ID Required")
                return

            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM product WHERE product_id=%s", (pid,))
            db.commit()
            db.close()

            messagebox.showinfo("Deleted", "Product Deleted Successfully")
            win.destroy()
            self.load_products()

        tk.Button(win, text="Delete", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=delete).pack(pady=10)

    # ---------- USERS MANAGEMENT ----------
    def open_users_window(self):
        win = tk.Toplevel(self)
        win.title("User Management")
        win.geometry("1000x600")
        win.config(bg="white")

        # Controls
        ctrl = tk.Frame(win, bg="white")
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Button(ctrl, text="Refresh", command=lambda: load_users()).pack(side="left")

        # Table
        cols = ("ID", "Username", "Email", "Phone", "Login Count", "Total Spent", "Last Login")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("ID", width=60)
        tree.column("Username", width=180)
        tree.column("Email", width=220)
        tree.column("Phone", width=120)
        tree.column("Login Count", width=120)
        tree.column("Total Spent", width=120)
        tree.column("Last Login", width=180)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_users():
            for i in tree.get_children():
                tree.delete(i)
            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute(
                    """
                    SELECT user_id, username, email, COALESCE(phone,''),
                           COALESCE(login_count,0), COALESCE(total_spent,0), last_login
                    FROM users
                    ORDER BY user_id ASC
                    """
                )
                rows = cur.fetchall()
                db.close()
                for r in rows:
                    uid, uname, email, phone, logins, spent, last_login = r
                    tree.insert("", tk.END, values=(uid, uname, email, phone, logins, f"${float(spent):.2f}", str(last_login) if last_login else "-"))
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))

        load_users()

    # ---------- INSIGHTS DASHBOARD ----------
    def open_insights_window(self):
        win = tk.Toplevel(self)
        win.title("Insights Dashboard")
        win.geometry("1100x700")
        win.config(bg="white")

        container = tk.Frame(win, bg="white")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Layout frames
        top_frame = tk.Frame(container, bg="white")
        top_frame.pack(fill="x")
        bottom_frame = tk.Frame(container, bg="white")
        bottom_frame.pack(fill="both", expand=True)

        # Canvases for charts
        most_canvas = tk.Canvas(top_frame, width=520, height=260, bg="#FAFAFA", highlightthickness=1, highlightbackground="#DDD")
        least_canvas = tk.Canvas(top_frame, width=520, height=260, bg="#FAFAFA", highlightthickness=1, highlightbackground="#DDD")
        most_canvas.pack(side="left", padx=10, pady=10)
        least_canvas.pack(side="left", padx=10, pady=10)

        revenue_canvas = tk.Canvas(bottom_frame, width=1060, height=260, bg="#FAFAFA", highlightthickness=1, highlightbackground="#DDD")
        revenue_canvas.pack(padx=10, pady=10)

        # Inventory table (low stock)
        inv_frame = tk.Frame(bottom_frame, bg="white")
        inv_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(inv_frame, text="Low Stock (Top 10)", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        inv_tree = ttk.Treeview(inv_frame, columns=("ID","Name","Stock"), show="headings", height=8)
        for c in ("ID","Name","Stock"):
            inv_tree.heading(c, text=c)
        inv_tree.column("ID", width=80)
        inv_tree.column("Name", width=500)
        inv_tree.column("Stock", width=120)
        inv_tree.pack(fill="x", padx=2, pady=5)

        # Refresh button
        tk.Button(container, text="Refresh", command=lambda: refresh()).pack(anchor="ne", padx=10)

        def draw_bar_chart(canvas, title, data):
            canvas.delete("all")
            w = int(canvas["width"])
            h = int(canvas["height"])
            pad = 30
            canvas.create_text(pad, 15, anchor="w", text=title, font=("Arial", 12, "bold"))
            if not data:
                canvas.create_text(w//2, h//2, text="No data", font=("Arial", 12, "italic"))
                return
            labels = [d[0] for d in data]
            values = [max(0, float(d[1])) for d in data]
            max_val = max(values) if any(values) else 1.0
            bar_w = max(20, (w - pad*2) // max(1, len(values)))
            for i, (label, val) in enumerate(zip(labels, values)):
                x0 = pad + i * bar_w + 10
                x1 = x0 + bar_w - 20
                bh = int((h - pad*2) * (val / max_val))
                y1 = h - pad
                y0 = y1 - bh
                canvas.create_rectangle(x0, y0, x1, y1, fill="#7B0000")
                short = (label if len(label) <= 10 else label[:9] + "…")
                canvas.create_text((x0+x1)//2, y1+10, text=short, anchor="n", font=("Arial", 9))
                canvas.create_text((x0+x1)//2, y0-5, text=f"{val:.0f}", anchor="s", font=("Arial", 9))

        def draw_line_chart(canvas, title, data_points):
            canvas.delete("all")
            w = int(canvas["width"])
            h = int(canvas["height"])
            pad = 40
            canvas.create_text(pad, 15, anchor="w", text=title, font=("Arial", 12, "bold"))
            if not data_points:
                canvas.create_text(w//2, h//2, text="No data", font=("Arial", 12, "italic"))
                return
            labels = [d[0] for d in data_points]
            values = [max(0.0, float(d[1])) for d in data_points]
            max_val = max(values) if any(values) else 1.0
            # Axes
            canvas.create_line(pad, h-pad, w-pad, h-pad, fill="#333")
            canvas.create_line(pad, h-pad, pad, pad, fill="#333")
            # Plot points
            n = len(values)
            if n == 1:
                xs = [pad + (w - 2*pad)//2]
            else:
                xs = [pad + i * (w - 2*pad) // (n-1) for i in range(n)]
            ys = [h - pad - int((h - 2*pad) * (v / max_val)) for v in values]
            # Lines
            for i in range(1, n):
                canvas.create_line(xs[i-1], ys[i-1], xs[i], ys[i], fill="#2E8B57", width=2)
            # Points
            for x, y, v in zip(xs, ys, values):
                canvas.create_oval(x-3, y-3, x+3, y+3, fill="#2E8B57", outline="")
                canvas.create_text(x, y-8, text=f"{v:.0f}", font=("Arial", 9))
            # X labels
            for x, lab in zip(xs, labels):
                canvas.create_text(x, h-pad+10, text=str(lab), anchor="n", font=("Arial", 9))

        def refresh():
            # Top sold
            try:
                most = get_most_sold_products(5)
                most_pairs = [(name, qty) for (_pid, name, qty) in most]
            except Exception:
                most_pairs = []
            draw_bar_chart(most_canvas, "Top 5 Most Sold", most_pairs)

            # Least sold
            try:
                least = get_least_sold_products(5)
                least_pairs = [(name, qty) for (_pid, name, qty) in least]
            except Exception:
                least_pairs = []
            draw_bar_chart(least_canvas, "Top 5 Least Sold", least_pairs)

            # Low stock table
            for i in inv_tree.get_children():
                inv_tree.delete(i)
            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute("SELECT product_id, name, stock FROM product ORDER BY stock ASC LIMIT 10")
                rows = cur.fetchall()
                db.close()
                for r in rows:
                    inv_tree.insert("", tk.END, values=r)
            except Exception:
                pass

            # Revenue last 7 days
            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute(
                    """
                    SELECT DATE(order_date) as d, SUM(total_amount) as total
                    FROM orders
                    GROUP BY d
                    ORDER BY d ASC
                    LIMIT 7
                    """
                )
                rows = cur.fetchall()
                db.close()
                data_points = [(str(d), float(t or 0)) for (d, t) in rows]
            except Exception:
                data_points = []
            draw_line_chart(revenue_canvas, "Revenue (Last up to 7 Days)", data_points)

        refresh()

# Run Panel
if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
