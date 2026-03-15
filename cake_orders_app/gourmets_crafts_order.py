import sqlite3
import os
import calendar
from flask import Flask, render_template, request, redirect, url_for, Response, flash
from datetime import datetime, date
from urllib.parse import quote as url_quote

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gourmets-crafts-secret-key-change-in-prod')

@app.template_filter('urlencode')
def urlencode_filter(s):
    return url_quote(str(s))

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
                    order_amount REAL,
                    status TEXT DEFAULT 'pending'
                )''')
    # Migration: add status column to existing databases
    try:
        c.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'pending'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Backfill any rows missing a status
    c.execute("UPDATE orders SET status = 'pending' WHERE status IS NULL")
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

        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        c.execute("INSERT INTO orders (order_date, customer_address, phone_number, order_details, order_amount, status) VALUES (?, ?, ?, ?, ?, 'pending')",
                  (order_date, customer_address, phone_number, order_details, order_amount))
        conn.commit()
        conn.close()

        flash('Order added successfully!', 'success')
        return redirect(url_for('list_orders'))
    return render_template('add_order.html')

@app.route('/orders')
def list_orders():
    status_filter = request.args.get('status', '')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    if status_filter in ('pending', 'complete', 'cancelled'):
        c.execute("SELECT * FROM orders WHERE status = ? ORDER BY id DESC", (status_filter,))
    else:
        c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    return render_template('list_orders.html', orders=orders, status_filter=status_filter)

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    if request.method == 'POST':
        order_date = request.form['order_date']
        customer_address = request.form['customer_address']
        phone_number = request.form['phone_number']
        order_details = request.form['order_details']
        order_amount_str = request.form['order_amount']

        try:
            datetime.strptime(order_date, '%Y-%m-%d')
        except ValueError:
            conn.close()
            return "Invalid date format. Use YYYY-MM-DD.", 400

        if not phone_number.isdigit():
            conn.close()
            return "Phone number must contain only digits.", 400

        try:
            order_amount = float(order_amount_str)
        except ValueError:
            conn.close()
            return "Order amount must be a number.", 400

        c.execute(
            "UPDATE orders SET order_date=?, customer_address=?, phone_number=?, order_details=?, order_amount=? WHERE id=?",
            (order_date, customer_address, phone_number, order_details, order_amount, order_id)
        )
        conn.commit()
        conn.close()
        flash('Order #' + str(order_id) + ' updated successfully.', 'success')
        return redirect(url_for('list_orders'))

    c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = c.fetchone()
    conn.close()
    if order is None:
        return "Order not found.", 404
    return render_template('edit_order.html', order=order)

@app.route('/complete_order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status = 'complete' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    flash('Order #' + str(order_id) + ' marked as complete!', 'success')
    return redirect(url_for('list_orders'))

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    flash('Order #' + str(order_id) + ' has been cancelled.', 'success')
    return redirect(url_for('list_orders'))

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/total_sales')
def total_sales():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT SUM(order_amount) FROM orders WHERE status != 'cancelled'")
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
        c.execute("SELECT * FROM orders WHERE order_date BETWEEN ? AND ? ORDER BY id DESC", (start_date, end_date))
        orders = c.fetchall()
        conn.close()
        return render_template('list_orders.html', orders=orders, status_filter='')
    return render_template('date_range.html')

@app.route('/daily_sales')
def daily_sales():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT order_date, SUM(order_amount) FROM orders WHERE status != 'cancelled' GROUP BY order_date ORDER BY order_date")
    sales = c.fetchall()
    conn.close()
    return render_template('daily_sales.html', sales=sales)

@app.route('/monthly_sales')
def monthly_sales():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT strftime('%Y-%m', order_date), SUM(order_amount) FROM orders WHERE status != 'cancelled' GROUP BY strftime('%Y-%m', order_date) ORDER BY strftime('%Y-%m', order_date)")
    sales = c.fetchall()
    conn.close()
    return render_template('monthly_sales.html', sales=sales)

@app.route('/export_csv')
def export_csv():
    import csv
    from io import StringIO
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Order Date', 'Customer Address', 'Phone Number', 'Order Details', 'Order Amount', 'Status'])
    writer.writerows(orders)
    output = si.getvalue()
    si.close()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=orders.csv'})

@app.route('/calendar')
def order_calendar():
    today = date.today()
    year  = int(request.args.get('year',  today.year))
    month = int(request.args.get('month', today.month))

    # Clamp month to valid range
    if month < 1:  month = 12; year -= 1
    if month > 12: month = 1;  year += 1

    # Fetch all orders for this month
    month_str = f"{year}-{month:02d}"
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT id, order_date, customer_address, order_amount, status FROM orders WHERE order_date LIKE ? ORDER BY order_date", (month_str + '%',))
    rows = c.fetchall()
    conn.close()

    # Group by day: {day_int: [order, ...]}
    orders_by_day = {}
    for row in rows:
        day = int(row[1].split('-')[2])
        orders_by_day.setdefault(day, []).append(row)

    # Build calendar grid (list of weeks, each week is 7 day numbers or 0 for padding)
    cal = calendar.monthcalendar(year, month)

    # Prev / next month
    prev_month = month - 1 if month > 1 else 12
    prev_year  = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year  = year if month < 12 else year + 1

    month_name = calendar.month_name[month]

    return render_template('calendar.html',
        year=year, month=month, month_name=month_name,
        cal=cal, orders_by_day=orders_by_day,
        today=today,
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
