from tkinter import *
from tkinter import messagebox

# ---------------- Data Storage ----------------
accounts = {}
account_number = 1001

# ---------------- Main Window ----------------
root = Tk()
root.title("Bank Management System")
root.geometry("500x470")
root.config(bg="#cfe8ff")

# ---------------- Functions ----------------

def show_create_account():
    main_frame.pack_forget()
    create_frame.pack()

def show_services():
    main_frame.pack_forget()
    service_frame.pack()

def show_deposit():
    service_frame.pack_forget()
    deposit_frame.pack()

def show_withdraw():
    service_frame.pack_forget()
    withdraw_frame.pack()

def show_balance():
    service_frame.pack_forget()
    balance_frame.pack()

def go_back():
    create_frame.pack_forget()
    service_frame.pack_forget()
    deposit_frame.pack_forget()
    withdraw_frame.pack_forget()
    balance_frame.pack_forget()
    main_frame.pack()

def back_to_services():
    deposit_frame.pack_forget()
    withdraw_frame.pack_forget()
    balance_frame.pack_forget()
    service_frame.pack()

# ---------------- Create Account ----------------

def create_account():
    global account_number

    name = name_entry.get()
    deposit = deposit_entry.get()

    if name == "" or deposit == "":
        messagebox.showwarning("Warning", "Please fill all fields")
        return

    accounts[str(account_number)] = {
        "name": name,
        "balance": int(deposit)
    }

    messagebox.showinfo("Account Created",
                        f"Account Number: {account_number}")

    account_number += 1

    name_entry.delete(0, END)
    deposit_entry.delete(0, END)

# ---------------- Deposit ----------------

def deposit_money():

    acc = acc_entry.get()
    amount = amount_entry.get()

    if acc == "" or amount == "":
        messagebox.showwarning("Warning","Please fill all fields")
        return

    if acc in accounts:
        accounts[acc]["balance"] += int(amount)

        messagebox.showinfo("Success","Money Deposited")

        acc_entry.delete(0, END)
        amount_entry.delete(0, END)

    else:
        messagebox.showerror("Error","Account Not Found")

# ---------------- Withdraw ----------------

def withdraw_money():

    acc = w_acc_entry.get()
    amount = w_amount_entry.get()

    if acc == "" or amount == "":
        messagebox.showwarning("Warning","Please fill all fields")
        return

    if acc in accounts:

        amount = int(amount)

        if accounts[acc]["balance"] >= amount:

            accounts[acc]["balance"] -= amount

            messagebox.showinfo("Success","Money Withdrawn")

            w_acc_entry.delete(0, END)
            w_amount_entry.delete(0, END)

        else:
            messagebox.showwarning("Warning","Insufficient Balance")

    else:
        messagebox.showerror("Error","Account Not Found")

# ---------------- Check Balance ----------------

def check_balance():

    acc = bal_acc_entry.get()

    if acc == "":
        messagebox.showwarning("Warning","Enter account number")
        return

    if acc in accounts:

        balance = accounts[acc]["balance"]

        messagebox.showinfo("Balance",
                            f"Current Balance: {balance}")

        bal_acc_entry.delete(0, END)

    else:
        messagebox.showerror("Error","Account Not Found")

# ---------------- Welcome Screen ----------------

main_frame = Frame(root, bg="#cfe8ff")
main_frame.pack()

Label(main_frame,
      text="Welcome to Simple Bank System",
      font=("Arial",20,"bold"),
      bg="#cfe8ff",
      fg="#003366").pack(pady=40)

Button(main_frame,
       text="Already Have an Account",
       font=("Arial",12,"bold"),
       bg="#ffb347",
       width=25,
       height=2,
       command=show_services).pack(pady=10)

Button(main_frame,
       text="Create New Account",
       font=("Arial",12,"bold"),
       bg="#4CAF50",
       fg="white",
       width=25,
       height=2,
       command=show_create_account).pack(pady=10)

# ---------------- Create Account Screen ----------------


create_frame = Frame(root, bg="#fff4cc")

Label(create_frame,
      text="Create New Bank Account",
      font=("Arial",18,"bold"),
      bg="#fff4cc").pack(pady=20)

Label(create_frame,text="Customer Name",bg="#fff4cc").pack()

name_entry = Entry(create_frame)
name_entry.pack(pady=5)

Label(create_frame,text="Initial Deposit Amount",bg="#fff4cc").pack()

deposit_entry = Entry(create_frame)
deposit_entry.pack(pady=5)

Button(create_frame,
       text="Create Account",
       bg="#4CAF50",
       fg="white",
       width=20,
       command=create_account).pack(pady=15)

Button(create_frame,
       text="Back",
       bg="#ff6666",
       fg="white",
       width=15,
       command=go_back).pack()

# ---------------- Services Screen ----------------

service_frame = Frame(root, bg="#e6ffe6")

Label(service_frame,
      text="Bank Services",
      font=("Arial",18,"bold"),
      bg="#e6ffe6").pack(pady=30)

Button(service_frame,
       text="Deposit Money",
       font=("Arial",12,"bold"),
       bg="#4CAF50",
       fg="white",
       width=20,
       height=2,
       command=show_deposit).pack(pady=10, padx=60)

Button(service_frame,
       text="Withdraw Money",
       font=("Arial",12,"bold"),
       bg="#ff704d",
       fg="white",
       width=20,
       height=2,
       command=show_withdraw).pack(pady=10, padx=60)

Button(service_frame,
       text="Check Balance",
       font=("Arial",12,"bold"),
       bg="#4da6ff",
       fg="white",
       width=20,
       height=2,
       command=show_balance).pack(pady=10, padx=60)

Button(service_frame,
       text="Back",
       font=("Arial",12,"bold"),
       bg="#ff6666",
       fg="white",
       width=15,
       command=go_back).pack(pady=20)

# ---------------- Deposit Screen ----------------

deposit_frame = Frame(root, bg="#fff0e6")

Label(deposit_frame,
      text="Deposit Money",
      font=("Arial",18,"bold"),
      bg="#fff0e6").pack(pady=25)

Label(deposit_frame,text="Account Number",bg="#fff0e6").pack()

acc_entry = Entry(deposit_frame)
acc_entry.pack(pady=5)

Label(deposit_frame,text="Amount",bg="#fff0e6").pack()

amount_entry = Entry(deposit_frame)
amount_entry.pack(pady=5)

Button(deposit_frame,
       text="Deposit",
       bg="#4CAF50",
       fg="white",
       width=20,
       command=deposit_money).pack(pady=15)

Button(deposit_frame,
       text="Back",
       bg="#ff6666",
       fg="white",
       width=15,
       command=back_to_services).pack()

# ---------------- Withdraw Screen ----------------

withdraw_frame = Frame(root, bg="#ffe6e6")

Label(withdraw_frame,
      text="Withdraw Money",
      font=("Arial",18,"bold"),
      bg="#ffe6e6").pack(pady=25)

Label(withdraw_frame,text="Account Number",bg="#ffe6e6").pack()

w_acc_entry = Entry(withdraw_frame)
w_acc_entry.pack(pady=5)

Label(withdraw_frame,text="Amount",bg="#ffe6e6").pack()

w_amount_entry = Entry(withdraw_frame)
w_amount_entry.pack(pady=5)

Button(withdraw_frame,
       text="Withdraw",
       bg="#ff704d",
       fg="white",
       width=20,
       command=withdraw_money).pack(pady=15)

Button(withdraw_frame,
       text="Back",
       bg="#ff6666",
       fg="white",
       width=15,
       command=back_to_services).pack()

# ---------------- Balance Screen ----------------

balance_frame = Frame(root, bg="#e6f2ff")

Label(balance_frame,
      text="Check Balance",
      font=("Arial",18,"bold"),
      bg="#e6f2ff").pack(pady=25)

Label(balance_frame,text="Account Number",bg="#e6f2ff").pack()

bal_acc_entry = Entry(balance_frame)
bal_acc_entry.pack(pady=5)

Button(balance_frame,
       text="Check Balance",
       bg="#4da6ff",
       fg="white",
       width=20,
       command=check_balance).pack(pady=15)

Button(balance_frame,
       text="Back",
       bg="#ff6666",
       fg="white",
       width=15,
       command=back_to_services).pack()

root.mainloop()