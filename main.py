import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import database
from db.database import insert_medicine, get_all_medicines, update_medicine, delete_medicine
import datetime
from tkinter import messagebox

from collections import defaultdict
import csv

# Root window
root = tk.Tk()
root.title("Madina Pharmacy - Inventory")
root.geometry("1000x700")
root.configure(bg="#f8f9fa")

# Notebook tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# ------------------ TAB 1: Medicines ------------------ #
medicines_tab = ttk.Frame(notebook)
notebook.add(medicines_tab, text="💊 Medicines")

form_frame = tk.LabelFrame(medicines_tab, text="Add / Edit Medicine", bg="#ffffff", padx=20, pady=20)
form_frame.pack(pady=10, padx=20, fill="x")

tk.Label(form_frame, text="Medicine Name:", bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_name = tk.Entry(form_frame, width=30)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Quantity:", bg="#ffffff").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_quantity = tk.Entry(form_frame, width=30)
entry_quantity.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Price (PKR):", bg="#ffffff").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_price = tk.Entry(form_frame, width=30)
entry_price.grid(row=2, column=1, padx=5, pady=5)

def clear_fields():
    entry_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_price.delete(0, tk.END)

def load_medicines():
    tree.delete(*tree.get_children())
    for row in get_all_medicines():
        tree.insert("", "end", values=row)

def refresh_medicine_treeview():
    load_medicines()

def add_medicine():
    name = entry_name.get()
    quantity = entry_quantity.get()
    price = entry_price.get()
    if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
        insert_medicine(name, int(quantity), float(price))
        load_medicines()
        clear_fields()
        messagebox.showinfo("Success", "Medicine added/updated!")
    else:
        messagebox.showerror("Error", "Invalid input!")

def update_selected():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "Select a row to update.")
        return
    item = tree.item(selected)
    id = item['values'][0]
    name = entry_name.get()
    quantity = entry_quantity.get()
    price = entry_price.get()
    if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
        update_medicine(id, name, int(quantity), float(price))
        load_medicines()
        clear_fields()
        messagebox.showinfo("Updated", "Medicine updated!")
    else:
        messagebox.showerror("Error", "Invalid input!")

def delete_selected():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "Select a row to delete.")
        return
    id = tree.item(selected)['values'][0]
    delete_medicine(id)
    load_medicines()
    clear_fields()
    messagebox.showinfo("Deleted", "Medicine deleted!")

btn_frame = tk.Frame(form_frame, bg="#ffffff")
btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

tk.Button(btn_frame, text="➕ Add", command=add_medicine, width=12, bg="#28a745", fg="white").grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="🖊️ Update Selected", command=update_selected, width=18, bg="#ffc107", fg="black").grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="❌ Delete Selected", command=delete_selected, width=18, bg="#dc3545", fg="white").grid(row=0, column=2, padx=10)

tree_frame = tk.Frame(medicines_tab)
tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

cols = ("ID", "Name", "Quantity", "Price")
tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(side="left", fill="both", expand=True)

scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
scroll.pack(side="right", fill="y")

def on_row_select(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected)['values']
        entry_name.delete(0, tk.END)
        entry_name.insert(0, values[1])
        entry_quantity.delete(0, tk.END)
        entry_quantity.insert(0, values[2])
        entry_price.delete(0, tk.END)
        entry_price.insert(0, values[3])

tree.bind("<<TreeviewSelect>>", on_row_select)
load_medicines()

# ------------------ TAB 2: Search & Update ------------------ #
search_tab = ttk.Frame(notebook)
notebook.add(search_tab, text="🔍 Search & Update")

search_frame = tk.LabelFrame(search_tab, text="Search / Update Medicine", bg="#ffffff", padx=20, pady=20)
search_frame.pack(pady=10, padx=20, fill="x")

tk.Label(search_frame, text="Search by Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.grid(row=0, column=1, padx=5, pady=5)

result_frame = tk.Frame(search_tab)
result_frame.pack(padx=20, pady=10, fill="both", expand=True)

result_tree = ttk.Treeview(result_frame, columns=cols, show="headings")
for col in cols:
    result_tree.heading(col, text=col)
    result_tree.column(col, width=150)
result_tree.pack(side="left", fill="both", expand=True)

scroll2 = ttk.Scrollbar(result_frame, orient="vertical", command=result_tree.yview)
result_tree.configure(yscrollcommand=scroll2.set)
scroll2.pack(side="right", fill="y")

tk.Label(search_frame, text="Name:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
edit_name = tk.Entry(search_frame, width=30)
edit_name.grid(row=1, column=1, padx=5, pady=5)

tk.Label(search_frame, text="Quantity:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
edit_quantity = tk.Entry(search_frame, width=30)
edit_quantity.grid(row=2, column=1, padx=5, pady=5)

tk.Label(search_frame, text="Price:", bg="#ffffff").grid(row=3, column=0, padx=5, pady=5)
edit_price = tk.Entry(search_frame, width=30)
edit_price.grid(row=3, column=1, padx=5, pady=5)

selected_id = None

def on_result_select(event):
    global selected_id
    selected = result_tree.focus()
    if selected:
        values = result_tree.item(selected)['values']
        selected_id = values[0]
        edit_name.delete(0, tk.END)
        edit_name.insert(0, values[1])
        edit_quantity.delete(0, tk.END)
        edit_quantity.insert(0, values[2])
        edit_price.delete(0, tk.END)
        edit_price.insert(0, values[3])

result_tree.bind("<<TreeviewSelect>>", on_result_select)

def update_result():
    if selected_id:
        name = edit_name.get()
        quantity = edit_quantity.get()
        price = edit_price.get()
        if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
            update_medicine(selected_id, name, int(quantity), float(price))
            messagebox.showinfo("Success", "Medicine updated!")
            search_by_name()
            refresh_medicine_treeview()
        else:
            messagebox.showerror("Error", "Invalid input!")

tk.Button(search_frame, text="🔄 Update Selected", command=update_result, bg="#ffc107", fg="black", width=20).grid(row=4, column=1, pady=10)

def search_by_name(*args):
    keyword = search_var.get().lower()
    result_tree.delete(*result_tree.get_children())
    for row in get_all_medicines():
        if keyword in row[1].lower():
            result_tree.insert("", "end", values=row)

search_var.trace("w", search_by_name)

# -------------------- TAB 3: Cart & Billing -------------------- #
cart_tab = ttk.Frame(notebook)
notebook.add(cart_tab, text='🛒 Cart + Billing')

cart_tree = ttk.Treeview(cart_tab, columns=("Name", "Price", "Qty", "Total"), show="headings")
cart_tree.heading("Name", text="Name")
cart_tree.heading("Price", text="Price")
cart_tree.heading("Qty", text="Quantity")
cart_tree.heading("Total", text="Total")
cart_tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

cart = []

def refresh_cart():
    for row in cart_tree.get_children():
        cart_tree.delete(row)
    for item in cart:
        total = item['price'] * item['quantity']
        cart_tree.insert("", "end", values=(item['name'], item['price'], item['quantity'], total))

def add_to_cart():
    name = cart_name_entry.get()
    if not name:
        return
    try:
        qty = int(cart_qty_entry.get())
    except:
        messagebox.showerror("Error", "Quantity must be a number.")
        return

    all_meds = get_all_medicines()
    selected = next((m for m in all_meds if m[1].lower() == name.lower()), None)

    if not selected:
        messagebox.showerror("Error", "Medicine not found.")
        return

    stock_qty = selected[2]
    price = selected[3]

    if qty > stock_qty:
        messagebox.showerror("Error", "Not enough stock.")
        return

    existing = next((item for item in cart if item['name'].lower() == name.lower()), None)
    if existing:
        existing['quantity'] += qty
    else:
        cart.append({'name': name, 'price': price, 'quantity': qty})

    refresh_cart()
    cart_name_entry.delete(0, tk.END)
    cart_qty_entry.delete(0, tk.END)

def remove_from_cart():
    selected = cart_tree.selection()
    if not selected:
        return
    name = cart_tree.item(selected[0])['values'][0]
    cart[:] = [item for item in cart if item['name'] != name]
    refresh_cart()

def reduce_stock():
    for item in cart:
        database.reduce_stock(item['name'], item['quantity'])

def generate_pharmacy_bill(cart_items, customer_name):
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    bill_text = f"==== Madina Pharmacy ====\n"
    bill_text += f"Customer: {customer_name}\n"
    bill_text += f"Date/Time: {formatted_datetime}\n\n"
    bill_text += f"{'Name':15}{'Qty':>5}{'Price':>10}{'Total':>10}\n"
    bill_text += "-" * 45 + "\n"

    grand_total = 0
    for item in cart_items:
        total = item['quantity'] * item['price']
        bill_text += f"{item['name']:15}{item['quantity']:>5}{item['price']:>10}{total:>10}\n"
        grand_total += total

    bill_text += "-" * 45 + "\n"
    bill_text += f"{'Grand Total':>35} Rs. {grand_total}\n"
    bill_text += "=" * 45

    # Show the bill
    messagebox.showinfo("Bill", bill_text)

    # Save the bill to a text file
    with open(f"Bill_{customer_name}.txt", "w") as f:
        f.write(bill_text)

    # ✅ Save sales to CSV
    try:
        with open("sales_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for item in cart_items:
                writer.writerow([item['name'], item['quantity'], item['price'], current_datetime])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save sales log: {e}")

    # Reduce stock
    reduce_stock()

def generate_bill():
    if not cart:
        messagebox.showwarning("Cart Empty", "Add items to cart first.")
        return
    name = simpledialog.askstring("Customer Name", "Enter customer name:")
    if not name:
        return
    generate_pharmacy_bill(cart, name)
    cart.clear()
    refresh_cart()
    refresh_stock()

tk.Label(cart_tab, text="Medicine Name:").grid(row=1, column=0, padx=5, pady=5)
cart_name_entry = tk.Entry(cart_tab)
cart_name_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(cart_tab, text="Quantity:").grid(row=1, column=2, padx=5, pady=5)
cart_qty_entry = tk.Entry(cart_tab)
cart_qty_entry.grid(row=1, column=3, padx=5, pady=5)

tk.Button(cart_tab, text="Add to Cart", command=add_to_cart, bg="blue", fg="white").grid(row=2, column=1, pady=10)
tk.Button(cart_tab, text="Remove Selected", command=remove_from_cart, bg="red", fg="white").grid(row=2, column=2)
tk.Button(cart_tab, text="Generate Bill", command=generate_bill, bg="green", fg="white").grid(row=2, column=3)

def refresh_stock():
    tree.delete(*tree.get_children())
    for med in get_all_medicines():
        tree.insert("", "end", values=med)

# Initial load
refresh_stock()




# -------------------- TAB 4: Sales Review -------------------- #
sales_review_tab = ttk.Frame(notebook)
notebook.add(sales_review_tab, text="📊 Sales Review")

tk.Label(sales_review_tab, text="Top 5 Selling Products (This Month)", font=("Helvetica", 14, "bold")).pack(pady=10)

# Treeview for Top Products
columns = ("Product", "Quantity Sold")
sales_tree = ttk.Treeview(sales_review_tab, columns=columns, show="headings", height=6)
sales_tree.heading("Product", text="Product")
sales_tree.heading("Quantity Sold", text="Quantity Sold")
sales_tree.pack(pady=10)

# Monthly Total Sales Label
monthly_total_label = tk.Label(sales_review_tab, text="", font=("Helvetica", 12, "bold"))
monthly_total_label.pack(pady=10)

def generate_sales_review():
    from datetime import datetime
    sales_data = defaultdict(int)
    total_sales = 0

    try:
        with open("sales_log.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 4:
                    continue
                name, qty, price, timestamp = row
                try:
                    sale_date = datetime.strptime(timestamp.strip(), "%Y-%m-%d %H:%M:%S.%f")
                except:
                    sale_date = datetime.strptime(timestamp.strip(), "%Y-%m-%d %H:%M:%S")

                now = datetime.now()
                if sale_date.year == now.year and sale_date.month == now.month:
                    qty = int(qty)
                    price = float(price)
                    sales_data[name] += qty
                    total_sales += qty * price

        sales_tree.delete(*sales_tree.get_children())
        top_sales = sorted(sales_data.items(), key=lambda x: x[1], reverse=True)[:5]
        for product, qty in top_sales:
            sales_tree.insert("", "end", values=(product, qty))

        monthly_total_label.config(text=f"Total Monthly Sales: Rs. {total_sales:.2f}")
    except FileNotFoundError:
        monthly_total_label.config(text="No sales data available yet.")

tk.Button(sales_review_tab, text="Generate Sales Review", command=generate_sales_review, bg="purple", fg="white").pack(pady=10)

root.mainloop()

