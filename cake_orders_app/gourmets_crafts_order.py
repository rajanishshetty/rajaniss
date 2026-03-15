import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gourmets-crafts-secret-key-change-in-prod')

# Initialize database
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    order_date TEXT,
                    customer_address TEXT,
                    phone_number TEXT,
                    order_details TEXT,
                    order_amount REAL
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        order_date = request.form['order_date']
        customer_address = request.form['customer_address']
        phone_number = request.form['phone_number']
        order_details = request.form['order_details']
        order_amount_str = request.form['order_amount']
        
        # Validation
        try:
            datetime.strptime(order_date, '%Y-%m-%d')
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD.", 400
        
        if not phone_number.isdigit():
            return "Phone number must contain only digits.", 400
        
        try:
            order_amount = float(order_amount_str)
        except ValueError:
            return "Order amount must be a number.", 400
        
        # Insert into database
        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        c.execute("INSERT INTO orders (order_date, customer_address, phone_number, order_details, order_amount) VALUES (?, ?, ?, ?, ?)",
                  (order_date, customer_address, phone_number, order_details, order_amount))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))
    return render_template('add_order.html')

@app.route('/orders')
def list_orders():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    orders = c.fetchall()
    conn.close()
    return render_template('list_orders.html', orders=orders)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/total_sales')
def total_sales():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT SUM(order_amount) FROM orders")
    total = c.fetchone()[0] or 0
    conn.close()
    return render_template('total_sales.html', total=total)

@app.route('/orders_by_date', methods=['GET', 'POST'])
def orders_by_date():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE order_date BETWEEN ? AND ?", (start_date, end_date))
        orders = c.fetchall()
        conn.close()
        return render_template('list_orders.html', orders=orders)
    return render_template('date_range.html')

@app.route('/daily_sales')
def daily_sales():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT order_date, SUM(order_amount) FROM orders GROUP BY order_date ORDER BY order_date")
    sales = c.fetchall()
    conn.close()
    return render_template('daily_sales.html', sales=sales)

@app.route('/monthly_sales')
def monthly_sales():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT strftime('%Y-%m', order_date), SUM(order_amount) FROM orders GROUP BY strftime('%Y-%m', order_date) ORDER BY strftime('%Y-%m', order_date)")
    sales = c.fetchall()
    conn.close()
    return render_template('monthly_sales.html', sales=sales)

@app.route('/export_csv')
def export_csv():
    import csv
    from io import StringIO
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    orders = c.fetchall()
    conn.close()
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Order Date', 'Customer Address', 'Phone Number', 'Order Details', 'Order Amount'])
    writer.writerows(orders)
    output = si.getvalue()
    si.close()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=orders.csv'})

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))