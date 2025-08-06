import sqlite3

def connect_db():
    return sqlite3.connect('pharmacy.db')

# ------------------ Medicine Operations ------------------

def insert_medicine(name, quantity, price):
    conn = connect_db()
    c = conn.cursor()

    # Create medicines table
    c.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER,
            price REAL
        )
    ''')

    # Create cart table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL
        )
    ''')

    # Check if medicine exists
    c.execute("SELECT id, quantity FROM medicines WHERE LOWER(name)=LOWER(?)", (name,))
    result = c.fetchone()
    if result:
        med_id, existing_qty = result
        new_qty = existing_qty + quantity
        c.execute("UPDATE medicines SET quantity=?, price=? WHERE id=?", (new_qty, price, med_id))
    else:
        c.execute("INSERT INTO medicines (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))

    conn.commit()
    conn.close()

def get_all_medicines():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM medicines")
    rows = c.fetchall()
    conn.close()
    return rows

def get_medicine_by_name(name):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM medicines WHERE LOWER(name)=LOWER(?)", (name,))
    result = c.fetchone()
    conn.close()
    return result

def update_medicine(med_id, name, quantity, price):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE medicines SET name=?, quantity=?, price=? WHERE id=?",
                   (name, quantity, price, med_id))
    conn.commit()
    conn.close()

def delete_medicine(med_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    conn.commit()
    conn.close()

# ------------------ Stock & Cart Operations ------------------

def reduce_stock(name, sold_qty):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT quantity FROM medicines WHERE LOWER(name)=LOWER(?)", (name,))
    result = c.fetchone()
    if result:
        current_qty = result[0]
        new_qty = max(0, current_qty - sold_qty)
        c.execute("UPDATE medicines SET quantity=? WHERE LOWER(name)=LOWER(?)", (new_qty, name))
    conn.commit()
    conn.close()

def restock_medicine(name, qty):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE medicines SET quantity = quantity + ? WHERE LOWER(name)=LOWER(?)", (qty, name))
    conn.commit()
    conn.close()

# ------------------ Cart Functions ------------------

def add_to_cart(name, qty):
    conn = connect_db()
    c = conn.cursor()

    med = get_medicine_by_name(name)
    if med and med[2] >= qty:  # [2] is quantity
        price = med[3]
        subtotal = price * qty

        # Check if already in cart
        c.execute("SELECT id, quantity FROM cart WHERE LOWER(name)=LOWER(?)", (name,))
        existing = c.fetchone()
        if existing:
            cart_id, existing_qty = existing
            new_qty = existing_qty + qty
            new_subtotal = new_qty * price
            c.execute("UPDATE cart SET quantity=?, subtotal=? WHERE id=?", (new_qty, new_subtotal, cart_id))
        else:
            c.execute("INSERT INTO cart (name, quantity, price, subtotal) VALUES (?, ?, ?, ?)",
                      (name, qty, price, subtotal))

        reduce_stock(name, qty)
        conn.commit()
    conn.close()

def get_cart_items():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cart")
    rows = c.fetchall()
    conn.close()
    return rows

def update_cart_item(cart_id, new_qty):
    conn = connect_db()
    c = conn.cursor()

    # Get current item
    c.execute("SELECT name, quantity, price FROM cart WHERE id=?", (cart_id,))
    item = c.fetchone()
    if item:
        name, old_qty, price = item
        diff = new_qty - old_qty

        # Update cart
        new_subtotal = new_qty * price
        c.execute("UPDATE cart SET quantity=?, subtotal=? WHERE id=?", (new_qty, new_subtotal, cart_id))

        # Update stock accordingly
        if diff > 0:
            reduce_stock(name, diff)
        else:
            restock_medicine(name, -diff)

    conn.commit()
    conn.close()

def delete_cart_item(cart_id):
    conn = connect_db()
    c = conn.cursor()

    # Restock when removing from cart
    c.execute("SELECT name, quantity FROM cart WHERE id=?", (cart_id,))
    item = c.fetchone()
    if item:
        name, qty = item
        restock_medicine(name, qty)

    c.execute("DELETE FROM cart WHERE id=?", (cart_id,))
    conn.commit()
    conn.close()

def clear_cart():
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM cart")
    conn.commit()
    conn.close()

def calculate_total():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT SUM(subtotal) FROM cart")
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0
