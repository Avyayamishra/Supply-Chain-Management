import pymysql  
import customtkinter as ctk
import tabulate 

window = ctk.CTk()
window.geometry("800x600")
window.title("Supply Chain Management System")

cnxn = pymysql.connect(
    host='localhost',
    user='root',
    password='tiger',
    database='supply_chain'
)
cursor = cnxn.cursor()

x = ctk.CTkButton(window, text="Login", command=lambda: login())
x.pack(pady=20)

def login():
    username = ctk.CTkEntry(window, placeholder_text="Username")
    username.pack(pady=10)
    password = ctk.CTkEntry(window, placeholder_text="Password", show='*')
    password.pack(pady=10)

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()

    if result:
        ctk.CTkLabel(window, text="Login Successful!").pack(pady=20)
        cursor.execute("SELECT role FROM users WHERE username=%s", (username,))
        data = cursor.fetchone()
        if data == 'Admin':
            admin_panel()
        elif data == 'Manager':
            manager_panel()
        elif data == 'Operator':
            operator_panel()
        elif data == 'Viewer':
            viewer_panel()
    else:
        ctk.CTkLabel(window, text="Login Failed!").pack(pady=20)

window.mainloop()