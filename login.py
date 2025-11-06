import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
def login_window(on_success):
    # ---------- Database Connection ----------
    def connect_db():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="mkkapri",
            database="oreo"
        )
    # ---------- Main Window ----------
    root = tk.Tk()
    root.title("Oreo Login")
    root.state("zoomed")
    root.config(bg="white")
    # ---------- Load Logo ----------
    try:
        logo_img = Image.open("OREO.png")
        logo_img = logo_img.resize((120, 120))
        logo = ImageTk.PhotoImage(logo_img)
    except:
        logo = None
    # ---------- Switch Frames ----------
    def open_register():
        login_frame.pack_forget()
        register_frame.pack(pady=20)
    def open_login():
        register_frame.pack_forget()
        login_frame.pack(pady=20)
    # ---------- Login Function ----------
    def login_user():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, username FROM users WHERE username=%s AND password=%s",
                       (username, password))
        user = cursor.fetchone()
        db.close()
        if user:
            user_id, username = user
            root.destroy()  # Close login window
            on_success(user_id, username)  # Call Dashboard callback
        else:
            messagebox.showerror("Error", "Invalid username or password")
    # ---------- Register Function ----------
    def register_user():
        fullname = full_name_entry.get()
        address = address_entry.get()
        phone = phone_entry.get()
        password = reg_password_entry.get()
        email = email_entry.get()
        if not fullname or not address or not phone or not password:
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password, phone, address) VALUES (%s, %s, %s, %s, %s)",
                (fullname, email, password, phone, address)
            )
            db.commit()
            messagebox.showinfo("Success", "Registration Successful! You can now log in.")
            open_login()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")
        finally:
            db.close()
    # ---------- Login Frame ----------
    login_frame = tk.Frame(root, bg="white")
    if logo:
        tk.Label(login_frame, image=logo, bg="white").pack(pady=10)

    tk.Label(login_frame, text="Oreo Login", font=("Arial", 20, "bold"), bg="white").pack(pady=10)
    tk.Label(login_frame, text="Username:", font=("Arial", 10, "bold"), bg="white").pack()
    username_entry = tk.Entry(login_frame, width=30, bd=2, relief="flat", bg="#ddd")
    username_entry.pack(pady=5)

    tk.Label(login_frame, text="Password:", font=("Arial", 10, "bold"), bg="white").pack()
    password_entry = tk.Entry(login_frame, show="*", width=30, bd=2, relief="flat", bg="#ddd")
    password_entry.pack(pady=5)

    tk.Button(login_frame, text="Login", bg="#7B0000", fg="white", font=("Arial", 10, "bold"),
              width=20, relief="flat", command=login_user).pack(pady=10)
    tk.Button(login_frame, text="Register", bg="white", fg="#7B0000", font=("Arial", 10, "bold"),
              relief="flat", command=open_register).pack(pady=5)
    login_frame.pack(pady=20)
    # ---------- Register Frame ----------
    register_frame = tk.Frame(root, bg="white")
    if logo:
        tk.Label(register_frame, image=logo, bg="white").pack(pady=10)

    tk.Label(register_frame, text="Oreo Registration", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

    tk.Label(register_frame, text="Full Name:", font=("Arial", 10, "bold"), bg="white").pack()
    full_name_entry = tk.Entry(register_frame, width=30, bd=2, relief="flat", bg="#ddd")
    full_name_entry.pack(pady=5)

    tk.Label(register_frame, text="Email:", font=("Arial", 10, "bold"), bg="white").pack()
    email_entry = tk.Entry(register_frame, width=30, bd=2, relief="flat", bg="#ddd")
    email_entry.pack(pady=5)

    tk.Label(register_frame, text="Password:", font=("Arial", 10, "bold"), bg="white").pack()
    reg_password_entry = tk.Entry(register_frame, show="*", width=30, bd=2, relief="flat", bg="#ddd")
    reg_password_entry.pack(pady=5)

    tk.Label(register_frame, text="Address:", font=("Arial", 10, "bold"), bg="white").pack()
    address_entry = tk.Entry(register_frame, width=30, bd=2, relief="flat", bg="#ddd")
    address_entry.pack(pady=5)

    tk.Label(register_frame, text="Phone No:", font=("Arial", 10, "bold"), bg="white").pack()
    phone_entry = tk.Entry(register_frame, width=30, bd=2, relief="flat", bg="#ddd")
    phone_entry.pack(pady=5)

    tk.Button(register_frame, text="Register", bg="#7B0000", fg="white", font=("Arial", 10, "bold"),
              width=20, relief="flat", command=register_user).pack(pady=10)
    tk.Button(register_frame, text="Back to Login", bg="white", fg="#7B0000", font=("Arial", 10, "bold"),
              relief="flat", command=open_login).pack()
    root.mainloop()
