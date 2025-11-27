import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import mysql.connector
from database import (
    get_most_sold_products,
    get_least_sold_products,
    connect_db,
)

# Theme
BG_MAIN = "#050505"
BG_CARD = "#151515"
FG_TEXT = "#FFFFFF"
ACCENT = "#FF3B3B"

# Predefined Categories
CATEGORIES = [
    "Phone",
    "Laptop",
    "Tablets",
    "Gaming Console",
    "Earphone",
    "PC Accessory",
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
        self.title("Oreo POS - Admin Panel")
        self.state("zoomed")
        self.config(bg=BG_MAIN)

        # Logo
        try:
            img = Image.open("OREO.png")
            img = img.resize((80, 80))
            self.logo = ImageTk.PhotoImage(img)
        except Exception:
            self.logo = None

        # Header
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=20, pady=10)

        if self.logo:
            tk.Label(header, image=self.logo, bg=BG_MAIN).pack(side="left")

        tk.Label(
            header,
            text="Oreo POS - Admin",
            font=("Arial", 22, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(side="left", padx=10)

        tk.Button(
            header,
            text="Exit",
            bg=ACCENT,
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.destroy,
        ).pack(side="right")

        # Buttons
        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Add Product",
            bg=ACCENT,
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.add_product_window,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Update Product",
            bg="#B8860B",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.update_product_window,
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame,
            text="Delete Product",
            bg="#8B0000",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.delete_product_window,
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            btn_frame,
            text="Manage Members",
            bg="#1E90FF",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.open_members_window,
        ).grid(row=0, column=3, padx=10)

        tk.Button(
            btn_frame,
            text="Manage Staff",
            bg="#4B0082",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.open_staff_window,
        ).grid(row=0, column=4, padx=10)

        tk.Button(
            btn_frame,
            text="Insights Dashboard",
            bg="#2E8B57",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.open_insights_window,
        ).grid(row=0, column=5, padx=10)

        # Product Table
        table_frame = tk.Frame(self, bg=BG_MAIN)
        table_frame.pack(fill="both", expand=True, padx=20)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Price", "Stock"),
            show="headings",
            height=20,
        )
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
        win.config(bg=BG_MAIN)

        tk.Label(
            win,
            text="Add Product",
            font=("Arial", 16, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(pady=10)

        fields = ["Name", "Description", "Price", "Stock", "Image URL"]
        entries = {}

        for f in fields:
            tk.Label(win, text=f, bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
            e = tk.Entry(win, width=35, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
            e.pack(pady=3, padx=20)
            entries[f] = e

        # Category Radio Buttons
        tk.Label(
            win,
            text="Category",
            font=("Arial", 12, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(pady=10, anchor="w", padx=20)

        category_var = tk.StringVar(value=CATEGORIES[0])
        for c in CATEGORIES:
            tk.Radiobutton(
                win,
                text=c,
                variable=category_var,
                value=c,
                bg=BG_MAIN,
                fg=FG_TEXT,
                selectcolor=BG_CARD,
            ).pack(anchor="w", padx=20)

        def save():
            name, description, price, stock, image_url = [entries[f].get() for f in fields]

            if name == "" or price == "" or stock == "":
                messagebox.showerror("Error", "Name, Price, and Stock are required!")
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

            cursor.execute(
                """
                INSERT INTO product (name, description, price, stock, category_id, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (name, description, price_val, stock_val, category_id, image_url),
            )

            db.commit()
            db.close()

            messagebox.showinfo("Success", "Product Added Successfully")
            win.destroy()
            self.load_products()

        tk.Button(
            win,
            text="Add Product",
            bg=ACCENT,
            fg="white",
            font=("Arial", 12, "bold"),
            command=save,
            relief="flat",
        ).pack(pady=20)

    # ---------- UPDATE PRODUCT ----------
    def update_product_window(self):
        win = tk.Toplevel(self)
        win.title("Update Product")
        win.geometry("450x580")
        win.config(bg=BG_MAIN)

        tk.Label(
            win,
            text="Enter Product ID to Update",
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(pady=5)
        id_row = tk.Frame(win, bg=BG_MAIN)
        id_row.pack(pady=5)
        id_entry = tk.Entry(id_row, width=18, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
        id_entry.pack(side="left", padx=(0, 8))
        load_btn = tk.Button(id_row, text="Load Details", bg=ACCENT, fg="white", relief="flat")
        load_btn.pack(side="left")

        fields = ["Name", "Description", "Price", "Stock", "Image URL"]
        entries = {}

        for f in fields:
            tk.Label(win, text=f, bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
            e = tk.Entry(win, width=35, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
            e.pack(pady=3, padx=20)
            entries[f] = e

        # Category Radio Buttons
        tk.Label(
            win,
            text="Category",
            font=("Arial", 12, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(pady=10, anchor="w", padx=20)

        category_var = tk.StringVar(value=CATEGORIES[0])
        for c in CATEGORIES:
            tk.Radiobutton(
                win,
                text=c,
                variable=category_var,
                value=c,
                bg=BG_MAIN,
                fg=FG_TEXT,
                selectcolor=BG_CARD,
            ).pack(anchor="w", padx=20)

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
                entries["Name"].delete(0, tk.END)
                entries["Name"].insert(0, name or "")
                entries["Description"].delete(0, tk.END)
                entries["Description"].insert(0, description or "")
                entries["Price"].delete(0, tk.END)
                entries["Price"].insert(0, str(price))
                entries["Stock"].delete(0, tk.END)
                entries["Stock"].insert(0, str(stock))
                entries["Image URL"].delete(0, tk.END)
                entries["Image URL"].insert(0, image_url or "")

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

            cursor.execute(
                """
                UPDATE product
                SET name=%s, description=%s, price=%s, stock=%s, category_id=%s, image_url=%s
                WHERE product_id=%s
            """,
                (name, description, price_val, stock_val, category_id, image_url, pid),
            )

            db.commit()
            db.close()

            messagebox.showinfo("Updated", "Product Updated Successfully")
            win.destroy()
            self.load_products()

        tk.Button(
            win,
            text="Update Product",
            bg="#B8860B",
            fg="white",
            font=("Arial", 12, "bold"),
            command=update,
            relief="flat",
        ).pack(pady=20)

    # ---------- DELETE PRODUCT ----------
    def delete_product_window(self):
        win = tk.Toplevel(self)
        win.title("Delete Product")
        win.geometry("300x200")
        win.config(bg=BG_MAIN)

        tk.Label(win, text="Enter Product ID to Delete", bg=BG_MAIN, fg=FG_TEXT).pack(pady=10)
        id_entry = tk.Entry(win, width=20, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
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

        tk.Button(
            win,
            text="Delete",
            bg="#8B0000",
            fg="white",
            font=("Arial", 12, "bold"),
            command=delete,
            relief="flat",
        ).pack(pady=10)

    # ---------- MEMBERS MANAGEMENT ----------
    def open_members_window(self):
        win = tk.Toplevel(self)
        win.title("Member Management")
        win.geometry("1100x600")
        win.config(bg=BG_MAIN)

        ctrl = tk.Frame(win, bg=BG_MAIN)
        ctrl.pack(fill="x", padx=10, pady=5)

        tk.Button(ctrl, text="Add Member", bg=ACCENT, fg="white", command=lambda: self._add_member(win)).pack(
            side="left", padx=5
        )
        tk.Button(ctrl, text="Edit Selected", bg="#B8860B", fg="white", command=lambda: self._edit_member(tree)).pack(
            side="left", padx=5
        )
        tk.Button(ctrl, text="Delete Selected", bg="#8B0000", fg="white", command=lambda: self._delete_member(tree)).pack(
            side="left", padx=5
        )
        tk.Button(ctrl, text="View Purchase History", bg="#1E90FF", fg="white",
                  command=lambda: self._view_member_history(tree)).pack(side="left", padx=5)
        tk.Button(ctrl, text="Refresh", bg="#444444", fg="white", command=lambda: load_members()).pack(
            side="right", padx=5
        )

        cols = (
            "ID",
            "Name",
            "Member No",
            "Email",
            "Phone",
            "Membership Level",
            "Total Spent",
        )
        tree = ttk.Treeview(win, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("ID", width=60)
        tree.column("Name", width=160)
        tree.column("Member No", width=130)
        tree.column("Email", width=220)
        tree.column("Phone", width=120)
        tree.column("Membership Level", width=130)
        tree.column("Total Spent", width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_members():
            for i in tree.get_children():
                tree.delete(i)
            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute(
                    """
                    SELECT user_id,
                           username,
                           COALESCE(member_number,''),
                           email,
                           COALESCE(phone,''),
                           COALESCE(membership_level,'Bronze'),
                           COALESCE(total_spent,0)
                    FROM users
                    WHERE role='member'
                    ORDER BY user_id ASC
                    """
                )
                rows = cur.fetchall()
                db.close()
                for r in rows:
                    uid, uname, member_no, email, phone, level, spent = r
                    tree.insert(
                        "",
                        tk.END,
                        values=(uid, uname, member_no, email, phone, level, f"${float(spent):.2f}"),
                    )
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))

        load_members()

    def _add_member(self, parent):
        win = tk.Toplevel(parent)
        win.title("Add Member")
        win.geometry("400x450")
        win.config(bg=BG_MAIN)

        fields = ["Name", "Email", "Phone", "Address", "Member Number"]
        entries = {}

        tk.Label(win, text="Add Member", bg=BG_MAIN, fg=FG_TEXT, font=("Arial", 14, "bold")).pack(pady=10)

        form = tk.Frame(win, bg=BG_MAIN)
        form.pack(pady=5, fill="x")

        for f in fields:
            tk.Label(form, text=f, bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
            e = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
            e.pack(pady=3, padx=20)
            entries[f] = e

        tk.Label(form, text="Initial Membership Level", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        level_var = tk.StringVar(value="Bronze")
        level_box = ttk.Combobox(form, textvariable=level_var, values=["Bronze", "Silver", "Gold"], state="readonly")
        level_box.pack(pady=3, padx=20)

        def save():
            name = entries["Name"].get().strip()
            email = entries["Email"].get().strip()
            phone = entries["Phone"].get().strip()
            address = entries["Address"].get().strip()
            member_no = entries["Member Number"].get().strip()
            level = level_var.get()

            if not name or not email or not member_no:
                messagebox.showerror("Error", "Name, Email and Member Number are required.")
                return

            db = connect_db()
            cur = db.cursor()
            try:
                cur.execute(
                    """
                    INSERT INTO users (username, email, password, phone, address, role, member_number, membership_level)
                    VALUES (%s, %s, %s, %s, %s, 'member', %s, %s)
                    """,
                    (name, email, "member", phone, address, member_no, level),
                )
                db.commit()
                messagebox.showinfo("Success", "Member added successfully.")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))
            finally:
                db.close()

        tk.Button(win, text="Save Member", bg=ACCENT, fg="white", font=("Arial", 12, "bold"),
                  command=save, relief="flat").pack(pady=20)

    def _edit_member(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Member", "Please select a member to edit.")
            return

        item = tree.item(selected[0])
        uid, name, member_no, email, phone, level, spent = item["values"]

        win = tk.Toplevel(tree)
        win.title("Edit Member")
        win.geometry("400x450")
        win.config(bg=BG_MAIN)

        fields = ["Name", "Email", "Phone", "Address", "Member Number"]
        entries = {}

        tk.Label(win, text="Edit Member", bg=BG_MAIN, fg=FG_TEXT, font=("Arial", 14, "bold")).pack(pady=10)

        form = tk.Frame(win, bg=BG_MAIN)
        form.pack(pady=5, fill="x")

        # Preload from DB to get address too
        db = connect_db()
        cur = db.cursor()
        cur.execute("SELECT address FROM users WHERE user_id=%s", (uid,))
        row = cur.fetchone()
        addr_val = row[0] if row else ""

        # Name
        tk.Label(form, text="Name", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        e_name = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
        e_name.pack(pady=3, padx=20)
        e_name.insert(0, name)
        entries["Name"] = e_name

        # Email
        tk.Label(form, text="Email", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        e_email = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
        e_email.pack(pady=3, padx=20)
        e_email.insert(0, email)
        entries["Email"] = e_email

        # Phone
        tk.Label(form, text="Phone", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        e_phone = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
        e_phone.pack(pady=3, padx=20)
        e_phone.insert(0, phone)
        entries["Phone"] = e_phone

        # Address
        tk.Label(form, text="Address", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        e_addr = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
        e_addr.pack(pady=3, padx=20)
        e_addr.insert(0, addr_val or "")
        entries["Address"] = e_addr

        # Member Number
        tk.Label(form, text="Member Number", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        e_mem = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
        e_mem.pack(pady=3, padx=20)
        e_mem.insert(0, member_no)
        entries["Member Number"] = e_mem

        # Level
        tk.Label(form, text="Membership Level", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        level_var = tk.StringVar(value=level)
        level_box = ttk.Combobox(form, textvariable=level_var, values=["Bronze", "Silver", "Gold"], state="readonly")
        level_box.pack(pady=3, padx=20)

        def save():
            name_val = entries["Name"].get().strip()
            email_val = entries["Email"].get().strip()
            phone_val = entries["Phone"].get().strip()
            address_val = entries["Address"].get().strip()
            mem_no_val = entries["Member Number"].get().strip()
            level_val = level_var.get()

            if not name_val or not email_val or not mem_no_val:
                messagebox.showerror("Error", "Name, Email and Member Number are required.")
                return

            db2 = connect_db()
            c2 = db2.cursor()
            try:
                c2.execute(
                    """
                    UPDATE users
                    SET username=%s, email=%s, phone=%s, address=%s,
                        member_number=%s, membership_level=%s
                    WHERE user_id=%s
                    """,
                    (name_val, email_val, phone_val, address_val, mem_no_val, level_val, uid),
                )
                db2.commit()
                messagebox.showinfo("Success", "Member updated successfully.")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))
            finally:
                db2.close()

        tk.Button(win, text="Save Changes", bg=ACCENT, fg="white", font=("Arial", 12, "bold"),
                  command=save, relief="flat").pack(pady=20)

    def _delete_member(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Member", "Please select a member to delete.")
            return

        item = tree.item(selected[0])
        uid = item["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this member?"):
            db = connect_db()
            cur = db.cursor()
            try:
                cur.execute("DELETE FROM users WHERE user_id=%s AND role='member'", (uid,))
                db.commit()
                messagebox.showinfo("Deleted", "Member deleted.")
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))
            finally:
                db.close()

    def _view_member_history(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Member", "Please select a member first.")
            return

        item = tree.item(selected[0])
        uid, name, member_no, _, _, _, _ = item["values"]

        win = tk.Toplevel(tree)
        win.title(f"Purchase History - {name}")
        win.geometry("800x500")
        win.config(bg=BG_MAIN)

        tk.Label(
            win,
            text=f"Purchase History - {name} ({member_no})",
            bg=BG_MAIN,
            fg=FG_TEXT,
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        cols = ("Order ID", "Date", "Total", "Discount", "Net", "Status")
        tree_orders = ttk.Treeview(win, columns=cols, show="headings", height=15)
        for c in cols:
            tree_orders.heading(c, text=c)

        tree_orders.column("Order ID", width=80)
        tree_orders.column("Date", width=150)
        tree_orders.column("Total", width=100)
        tree_orders.column("Discount", width=100)
        tree_orders.column("Net", width=100)
        tree_orders.column("Status", width=120)
        tree_orders.pack(fill="both", expand=True, padx=10, pady=10)

        db = connect_db()
        cur = db.cursor()
        try:
            cur.execute(
                """
                SELECT order_id, order_date, total_amount, discount_amount, net_amount, status
                FROM orders
                WHERE member_id=%s
                ORDER BY order_date DESC
                """,
                (uid,),
            )
            rows = cur.fetchall()
            for r in rows:
                oid, dt, total, disc, net, status = r
                tree_orders.insert(
                    "",
                    tk.END,
                    values=(
                        oid,
                        str(dt),
                        f"${float(total or 0):.2f}",
                        f"${float(disc or 0):.2f}",
                        f"${float(net or 0):.2f}",
                        status,
                    ),
                )
        finally:
            db.close()

    # ---------- STAFF MANAGEMENT ----------
    def open_staff_window(self):
        win = tk.Toplevel(self)
        win.title("Staff Management")
        win.geometry("900x600")
        win.config(bg=BG_MAIN)

        ctrl = tk.Frame(win, bg=BG_MAIN)
        ctrl.pack(fill="x", padx=10, pady=5)

        tk.Button(ctrl, text="Add Staff", bg=ACCENT, fg="white", command=lambda: self._add_staff(win)).pack(
            side="left", padx=5
        )
        tk.Button(ctrl, text="Edit Selected", bg="#B8860B", fg="white", command=lambda: self._edit_staff(tree)).pack(
            side="left", padx=5
        )
        tk.Button(ctrl, text="Delete Selected", bg="#8B0000", fg="white", command=lambda: self._delete_staff(tree)).pack(
            side="left", padx=5
        )
        tk.Button(ctrl, text="Refresh", bg="#444444", fg="white", command=lambda: load_staff()).pack(
            side="right", padx=5
        )

        cols = ("ID", "Name", "Role", "Email", "Phone")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("ID", width=60)
        tree.column("Name", width=180)
        tree.column("Role", width=100)
        tree.column("Email", width=220)
        tree.column("Phone", width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_staff():
            for i in tree.get_children():
                tree.delete(i)
            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute(
                    """
                    SELECT user_id, username, role, email, COALESCE(phone,'')
                    FROM users
                    WHERE role IN ('admin','employee')
                    ORDER BY role DESC, user_id ASC
                    """
                )
                rows = cur.fetchall()
                db.close()
                for r in rows:
                    uid, uname, role, email, phone = r
                    tree.insert("", tk.END, values=(uid, uname, role, email, phone))
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))

        load_staff()

    def _add_staff(self, parent):
        win = tk.Toplevel(parent)
        win.title("Add Staff")
        win.geometry("400x380")
        win.config(bg=BG_MAIN)

        tk.Label(win, text="Add Staff", bg=BG_MAIN, fg=FG_TEXT, font=("Arial", 14, "bold")).pack(pady=10)

        form = tk.Frame(win, bg=BG_MAIN)
        form.pack(pady=5, fill="x")

        def add_field(label):
            tk.Label(form, text=label, bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
            e = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
            e.pack(pady=3, padx=20)
            return e

        name_entry = add_field("Name")
        email_entry = add_field("Email")
        pass_entry = add_field("Password")
        phone_entry = add_field("Phone")

        tk.Label(form, text="Role", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        role_var = tk.StringVar(value="employee")
        role_box = ttk.Combobox(form, textvariable=role_var, values=["admin", "employee"], state="readonly")
        role_box.pack(pady=3, padx=20)

        def save():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            pwd = pass_entry.get().strip()
            phone = phone_entry.get().strip()
            role = role_var.get()

            if not name or not email or not pwd:
                messagebox.showerror("Error", "Name, Email and Password are required.")
                return

            db = connect_db()
            cur = db.cursor()
            try:
                cur.execute(
                    """
                    INSERT INTO users (username, email, password, phone, address, role)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (name, email, pwd, phone, "", role),
                )
                db.commit()
                messagebox.showinfo("Success", "Staff added successfully.")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))
            finally:
                db.close()

        tk.Button(win, text="Save Staff", bg=ACCENT, fg="white", font=("Arial", 12, "bold"),
                  command=save, relief="flat").pack(pady=20)

    def _edit_staff(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Staff", "Please select a staff record to edit.")
            return

        item = tree.item(selected[0])
        uid, name, role_val, email, phone = item["values"]

        win = tk.Toplevel(tree)
        win.title("Edit Staff")
        win.geometry("400x380")
        win.config(bg=BG_MAIN)

        tk.Label(win, text="Edit Staff", bg=BG_MAIN, fg=FG_TEXT, font=("Arial", 14, "bold")).pack(pady=10)

        form = tk.Frame(win, bg=BG_MAIN)
        form.pack(pady=5, fill="x")

        def add_field(label, initial=""):
            tk.Label(form, text=label, bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
            e = tk.Entry(form, width=30, bg=BG_CARD, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0)
            e.pack(pady=3, padx=20)
            e.insert(0, initial)
            return e

        name_entry = add_field("Name", name)
        email_entry = add_field("Email", email)
        phone_entry = add_field("Phone", phone)

        tk.Label(form, text="Role", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        role_var = tk.StringVar(value=role_val)
        role_box = ttk.Combobox(form, textvariable=role_var, values=["admin", "employee"], state="readonly")
        role_box.pack(pady=3, padx=20)

        def save():
            name_v = name_entry.get().strip()
            email_v = email_entry.get().strip()
            phone_v = phone_entry.get().strip()
            role_v = role_var.get()

            if not name_v or not email_v:
                messagebox.showerror("Error", "Name and Email are required.")
                return

            db = connect_db()
            cur = db.cursor()
            try:
                cur.execute(
                    """
                    UPDATE users
                    SET username=%s, email=%s, phone=%s, role=%s
                    WHERE user_id=%s AND role IN ('admin','employee')
                    """,
                    (name_v, email_v, phone_v, role_v, uid),
                )
                db.commit()
                messagebox.showinfo("Success", "Staff updated successfully.")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))
            finally:
                db.close()

        tk.Button(win, text="Save Changes", bg=ACCENT, fg="white", font=("Arial", 12, "bold"),
                  command=save, relief="flat").pack(pady=20)

    def _delete_staff(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Staff", "Please select a staff record to delete.")
            return

        item = tree.item(selected[0])
        uid = item["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this staff account?"):
            db = connect_db()
            cur = db.cursor()
            try:
                cur.execute("DELETE FROM users WHERE user_id=%s AND role IN ('admin','employee')", (uid,))
                db.commit()
                messagebox.showinfo("Deleted", "Staff account deleted.")
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))
            finally:
                db.close()

    # ---------- INSIGHTS DASHBOARD ----------
    def open_insights_window(self):
        win = tk.Toplevel(self)
        win.title("Insights Dashboard")
        win.geometry("1100x700")
        win.config(bg=BG_MAIN)

        container = tk.Frame(win, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Layout frames
        top_frame = tk.Frame(container, bg=BG_MAIN)
        top_frame.pack(fill="x")
        bottom_frame = tk.Frame(container, bg=BG_MAIN)
        bottom_frame.pack(fill="both", expand=True)

        # Canvases for charts
        most_canvas = tk.Canvas(
            top_frame,
            width=520,
            height=260,
            bg="#101010",
            highlightthickness=1,
            highlightbackground="#444444",
        )
        least_canvas = tk.Canvas(
            top_frame,
            width=520,
            height=260,
            bg="#101010",
            highlightthickness=1,
            highlightbackground="#444444",
        )
        most_canvas.pack(side="left", padx=10, pady=10)
        least_canvas.pack(side="left", padx=10, pady=10)

        revenue_canvas = tk.Canvas(
            bottom_frame,
            width=1060,
            height=260,
            bg="#101010",
            highlightthickness=1,
            highlightbackground="#444444",
        )
        revenue_canvas.pack(padx=10, pady=10)

        # Inventory table (low stock)
        inv_frame = tk.Frame(bottom_frame, bg=BG_MAIN)
        inv_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(
            inv_frame,
            text="Low Stock (Top 10)",
            font=("Arial", 12, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(anchor="w")
        inv_tree = ttk.Treeview(inv_frame, columns=("ID", "Name", "Stock"), show="headings", height=8)
        for c in ("ID", "Name", "Stock"):
            inv_tree.heading(c, text=c)
        inv_tree.column("ID", width=80)
        inv_tree.column("Name", width=500)
        inv_tree.column("Stock", width=120)
        inv_tree.pack(fill="x", padx=2, pady=5)

        # Refresh button
        tk.Button(
            container,
            text="Refresh",
            bg="#444444",
            fg="white",
            command=lambda: refresh(),
        ).pack(anchor="ne", padx=10)

        def draw_bar_chart(canvas, title, data):
            canvas.delete("all")
            w = int(canvas["width"])
            h = int(canvas["height"])
            pad = 30
            canvas.create_text(
                pad,
                15,
                anchor="w",
                text=title,
                font=("Arial", 12, "bold"),
                fill="white",
            )
            if not data:
                canvas.create_text(
                    w // 2,
                    h // 2,
                    text="No data",
                    font=("Arial", 12, "italic"),
                    fill="white",
                )
                return
            labels = [d[0] for d in data]
            values = [max(0, float(d[1])) for d in data]
            max_val = max(values) if any(values) else 1.0
            bar_w = max(20, (w - pad * 2) // max(1, len(values)))
            for i, (label, val) in enumerate(zip(labels, values)):
                x0 = pad + i * bar_w + 10
                x1 = x0 + bar_w - 20
                bh = int((h - pad * 2) * (val / max_val))
                y1 = h - pad
                y0 = y1 - bh
                canvas.create_rectangle(x0, y0, x1, y1, fill=ACCENT, outline="")
                short = label if len(label) <= 10 else label[:9] + "…"
                canvas.create_text(
                    (x0 + x1) // 2,
                    y1 + 10,
                    text=short,
                    anchor="n",
                    font=("Arial", 9),
                    fill="white",
                )
                canvas.create_text(
                    (x0 + x1) // 2,
                    y0 - 5,
                    text=f"{val:.0f}",
                    anchor="s",
                    font=("Arial", 9),
                    fill="white",
                )

        def draw_line_chart(canvas, title, data_points):
            canvas.delete("all")
            w = int(canvas["width"])
            h = int(canvas["height"])
            pad = 40
            canvas.create_text(
                pad,
                15,
                anchor="w",
                text=title,
                font=("Arial", 12, "bold"),
                fill="white",
            )
            if not data_points:
                canvas.create_text(
                    w // 2,
                    h // 2,
                    text="No data",
                    font=("Arial", 12, "italic"),
                    fill="white",
                )
                return
            labels = [d[0] for d in data_points]
            values = [max(0.0, float(d[1])) for d in data_points]
            max_val = max(values) if any(values) else 1.0
            # Axes
            canvas.create_line(pad, h - pad, w - pad, h - pad, fill="#CCCCCC")
            canvas.create_line(pad, h - pad, pad, pad, fill="#CCCCCC")
            # Plot points
            n = len(values)
            if n == 1:
                xs = [pad + (w - 2 * pad) // 2]
            else:
                xs = [pad + i * (w - 2 * pad) // (n - 1) for i in range(n)]
            ys = [h - pad - int((h - 2 * pad) * (v / max_val)) for v in values]
            # Lines
            for i in range(1, n):
                canvas.create_line(xs[i - 1], ys[i - 1], xs[i], ys[i], fill=ACCENT, width=2)
            # Points
            for x, y, v in zip(xs, ys, values):
                canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=ACCENT, outline="")
                canvas.create_text(x, y - 8, text=f"{v:.0f}", font=("Arial", 9), fill="white")
            # X labels
            for x, lab in zip(xs, labels):
                canvas.create_text(x, h - pad + 10, text=str(lab), anchor="n", font=("Arial", 9), fill="white")

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
                    SELECT DATE(order_date) as d, SUM(net_amount) as total
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
            draw_line_chart(revenue_canvas, "Net Revenue (Last up to 7 Days)", data_points)

        refresh()


if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
