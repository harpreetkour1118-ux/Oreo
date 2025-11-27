import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from database import get_product_rating, add_or_update_rating, connect_db
from cart import CartWindow
import os
from login import login_window

# Theme
BG_MAIN = "#050505"
BG_CARD = "#151515"
FG_TEXT = "#FFFFFF"
FG_MUTED = "#AAAAAA"
ACCENT = "#FF3B3B"
ACCENT_SOFT = "#FF7777"


# ---------- Dashboard (POS Screen) ----------
class Dashboard(tk.Tk):
    def __init__(self, user_id, username):
        super().__init__()
        self.title("Oreo POS - Dashboard")
        self.state("zoomed")
        self.config(bg=BG_MAIN)
        self.username = username
        self.user_id = user_id  # staff id

        # Logo
        try:
            img = Image.open("oreo.png")
            img = img.resize((80, 80))
            self.logo = ImageTk.PhotoImage(img)
        except Exception:
            self.logo = None

        # Header
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", pady=10, padx=20)

        if self.logo:
            tk.Label(header, image=self.logo, bg=BG_MAIN).pack(side="left")

        tk.Label(
            header,
            text=f"Oreo POS  |  Staff: {username}",
            bg=BG_MAIN,
            fg=FG_TEXT,
            font=("Arial", 16, "bold"),
        ).pack(side="left", padx=10)

        cart_btn = tk.Button(
            header,
            text="🛒 Cart",
            bg=BG_MAIN,
            fg=ACCENT,
            font=("Arial", 12, "bold"),
            relief="flat",
            command=self.open_cart,
        )
        cart_btn.pack(side="right", padx=10)

        logout_btn = tk.Button(
            header,
            text="Log Out",
            bg=ACCENT,
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            command=self.logout,
        )
        logout_btn.pack(side="right", padx=10)

        # ---------- Scrollable Products Frame ----------
        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(fill="both", expand=True, pady=20, padx=20)

        self.canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.products_frame = tk.Frame(self.canvas, bg=BG_MAIN)

        # Configure scrolling region
        self.products_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Add products_frame to canvas
        self.canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Load products
        self.load_products()

    # ---------- Mousewheel scrolling ----------
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ---------- Load Products ----------
    def load_products(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT product_id, name, description, price, image_url FROM product")
        products = cursor.fetchall()
        db.close()

        for widget in self.products_frame.winfo_children():
            widget.destroy()

        if not products:
            tk.Label(
                self.products_frame,
                text="No products found!",
                bg=BG_MAIN,
                fg=FG_TEXT,
                font=("Arial", 12, "bold"),
            ).pack()
            return

        columns = 5
        for i, product in enumerate(products):
            frame = tk.Frame(self.products_frame, bg=BG_CARD, padx=20, pady=20, bd=0, relief="flat")
            frame.grid(row=i // columns, column=i % columns, padx=10, pady=10)

            # --- Load Image  ---
            try:
                if product[4] and os.path.exists(product[4]):
                    img = Image.open(product[4])
                else:
                    raise Exception("No image provided")
                img = img.resize((150, 150))
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image for {product[1]}: {e}")
                img = Image.new("RGB", (150, 150), color="grey")
                photo = ImageTk.PhotoImage(img)

            lbl_img = tk.Label(frame, image=photo, bg=BG_CARD)
            lbl_img.image = photo
            lbl_img.pack()
            lbl_img.bind("<Button-1>", lambda e, p=product: self.open_product_detail(p))

            name_lbl = tk.Label(
                frame,
                text=product[1],
                bg=BG_CARD,
                fg=FG_TEXT,
                font=("Arial", 10, "bold"),
            )
            name_lbl.pack(pady=2)
            name_lbl.bind("<Button-1>", lambda e, p=product: self.open_product_detail(p))

            tk.Label(
                frame,
                text=f"${product[3]:.2f}",
                bg=BG_CARD,
                fg=ACCENT_SOFT,
                font=("Arial", 10, "bold"),
            ).pack()

            view_btn = tk.Button(
                frame,
                text="View",
                font=("Arial", 10, "bold"),
                bg="#252525",
                fg=FG_TEXT,
                relief="flat",
                command=lambda p=product: self.open_product_detail(p),
            )
            view_btn.pack(pady=2, fill="x")

            add_btn = tk.Button(
                frame,
                text="Add to Cart 🛒",
                font=("Arial", 10, "bold"),
                bg=ACCENT,
                fg="white",
                relief="flat",
                command=lambda p=product: self.add_to_cart(p),
            )
            add_btn.pack(pady=3, fill="x")

    # ---------- Product Detail ----------
    def open_product_detail(self, product):
        pid, name, description, price, image_url = product

        win = tk.Toplevel(self)
        win.title(name)
        win.geometry("800x600")
        win.config(bg=BG_MAIN)

        # Header
        header = tk.Frame(win, bg=BG_MAIN)
        header.pack(fill="x", padx=20, pady=10)
        tk.Label(
            header,
            text=name,
            font=("Arial", 18, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(side="left")
        tk.Label(
            header,
            text=f"${price:.2f}",
            font=("Arial", 14),
            bg=BG_MAIN,
            fg=ACCENT_SOFT,
        ).pack(side="right")

        # Top section with image + description
        top = tk.Frame(win, bg=BG_MAIN)
        top.pack(fill="x", padx=20)

        # Image
        try:
            if image_url and os.path.exists(image_url):
                img = Image.open(image_url)
            else:
                raise Exception("No image provided")
            img = img.resize((250, 250))
            photo = ImageTk.PhotoImage(img)
        except Exception:
            img = Image.new("RGB", (250, 250), color="grey")
            photo = ImageTk.PhotoImage(img)
        img_lbl = tk.Label(top, image=photo, bg=BG_MAIN)
        img_lbl.image = photo
        img_lbl.pack(side="left", padx=10, pady=10)

        desc = tk.Text(
            top,
            height=12,
            width=60,
            wrap="word",
            bg=BG_CARD,
            fg=FG_TEXT,
            bd=0,
        )
        desc.insert("1.0", description or "No description available.")
        desc.config(state="disabled")
        desc.pack(side="left", padx=10, pady=10, fill="x")

        # Ratings and reviews section
        section = tk.Frame(win, bg=BG_MAIN)
        section.pack(fill="both", expand=True, padx=20, pady=10)

        meta_frame = tk.Frame(section, bg=BG_MAIN)
        meta_frame.pack(fill="x")

        avg_var = tk.StringVar(value="Loading rating...")
        avg_lbl = tk.Label(
            meta_frame,
            textvariable=avg_var,
            font=("Arial", 12, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_SOFT,
        )
        avg_lbl.pack(side="left")

        def refresh_rating_and_reviews():
            try:
                avg, cnt = get_product_rating(pid)
                avg_var.set(f"Average rating: {avg:.1f} / 5  ({cnt} review{'s' if cnt != 1 else ''})")
            except Exception:
                avg_var.set("Average rating: N/A")

            # Load latest reviews
            for w in reviews_frame.winfo_children():
                w.destroy()

            try:
                db = connect_db()
                cur = db.cursor()
                cur.execute(
                    """
                    SELECT u.username, r.rating, COALESCE(r.comment,''), r.created_at
                    FROM ratings r
                    JOIN users u ON u.user_id = r.user_id
                    WHERE r.product_id=%s
                    ORDER BY r.created_at DESC
                    LIMIT 10
                    """,
                    (pid,),
                )
                rows = cur.fetchall()
                db.close()
            except Exception:
                rows = []

            if not rows:
                tk.Label(
                    reviews_frame,
                    text="No reviews yet.",
                    bg=BG_MAIN,
                    fg=FG_MUTED,
                    font=("Arial", 11, "italic"),
                ).pack(anchor="w")
            else:
                for username, rating, comment, created_at in rows:
                    tk.Label(
                        reviews_frame,
                        text=f"{username} - {rating}/5",
                        bg=BG_MAIN,
                        fg=FG_TEXT,
                        font=("Arial", 11, "bold"),
                    ).pack(anchor="w")
                    if comment:
                        tk.Label(
                            reviews_frame,
                            text=comment,
                            bg=BG_MAIN,
                            fg=FG_MUTED,
                            wraplength=700,
                            justify="left",
                            font=("Arial", 11),
                        ).pack(anchor="w", pady=(0, 6))

        reviews_frame = tk.Frame(section, bg=BG_MAIN)
        reviews_frame.pack(fill="both", expand=True, pady=10)

        # Rating submission form
        form = tk.Frame(section, bg=BG_CARD)
        form.pack(fill="x", pady=5)

        tk.Label(
            form,
            text="Your rating (1-5):",
            bg=BG_CARD,
            fg=FG_TEXT,
            font=("Arial", 11, "bold"),
        ).pack(side="left", padx=10, pady=10)
        rating_var = tk.IntVar(value=5)
        rating_spin = tk.Spinbox(
            form,
            from_=1,
            to=5,
            width=5,
            textvariable=rating_var,
            bg="#222222",
            fg="white",
            insertbackground="white",
        )
        rating_spin.pack(side="left")

        tk.Label(
            form,
            text="Comment:",
            bg=BG_CARD,
            fg=FG_TEXT,
            font=("Arial", 11, "bold"),
        ).pack(side="left", padx=(20, 5))
        comment_entry = tk.Entry(
            form,
            width=60,
            bg="#222222",
            fg="white",
            insertbackground="white",
        )
        comment_entry.pack(side="left", padx=5)

        def submit_rating():
            try:
                r = int(rating_var.get())
            except Exception:
                messagebox.showerror("Error", "Rating must be a number between 1 and 5")
                return
            cmt = comment_entry.get().strip()
            try:
                add_or_update_rating(self.user_id, pid, r, cmt if cmt else None)
                messagebox.showinfo("Thanks!", "Your rating has been submitted.")
                comment_entry.delete(0, tk.END)
                refresh_rating_and_reviews()
            except Exception as err:
                messagebox.showerror("Error", f"Unable to submit rating: {err}")

        tk.Button(
            form,
            text="Submit",
            bg=ACCENT,
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            command=submit_rating,
        ).pack(side="left", padx=10)

        # Initial load
        refresh_rating_and_reviews()

    # ---------- Add to Cart ----------
    def add_to_cart(self, product):
        product_id = product[0]
        db = connect_db()
        cursor = db.cursor()
        try:
            db.start_transaction()
            # Check and lock product stock
            cursor.execute(
                "SELECT stock, name FROM product WHERE product_id=%s FOR UPDATE",
                (product_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise Exception("Product not found.")
            stock, pname = row
            if (stock or 0) <= 0:
                raise Exception(f"{pname} is out of stock.")

            # Decrement stock to reserve one unit
            cursor.execute(
                "UPDATE product SET stock = stock - 1 WHERE product_id=%s",
                (product_id,),
            )

            # Upsert into cart (lock the row if exists)
            cursor.execute(
                "SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s FOR UPDATE",
                (self.user_id, product_id),
            )
            result = cursor.fetchone()
            if result:
                cursor.execute(
                    "UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s",
                    (self.user_id, product_id),
                )
            else:
                cursor.execute(
                    "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (self.user_id, product_id, 1),
                )

            db.commit()
            messagebox.showinfo("Cart", f"Added {product[1]} to cart!")
        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass
            messagebox.showerror("Cart", str(e))
        finally:
            db.close()

    # ---------- Open Cart ----------
    def open_cart(self):
        CartWindow(self, self.user_id)

    # ---------- Logout ----------
    def logout(self):
        self.destroy()


def start_dashboard(user_id, username):
    app = Dashboard(user_id, username)
    app.mainloop()


if __name__ == "__main__":
    login_window(on_success=start_dashboard)
