# Cake Orders Management App

A beginner-friendly Python Flask application to record and manage cake orders using SQLite database.

## Features

- Add new cake orders with date, address, phone, details, amount
- View all orders
- Reports: Total sales, orders by date range, daily/monthly summaries
- Export orders to CSV
- Input validation for date, phone, amount

## Installation

1. Ensure Python 3.7+ is installed.
2. Install dependencies: `pip install -r requirements.txt`

## Running the App

1. Navigate to the app directory: `cd cake_orders_app`
2. Run: `python app.py`
3. Open browser to `http://127.0.0.1:5000/`

## Usage

- Home: Welcome page
- Add Order: Fill form to add new order
- List Orders: View all orders in table
- Reports: Access various reports

## Sample Data

Order Date: 2023-12-12
Customer Address: 123 Main St, City
Phone Number: 1234567890
Order Details: Chocolate cake, large, Happy Birthday message
Order Amount: 50.00

## File Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
- `static/`: Static files (CSS/JS, if added)
- `orders.db`: SQLite database (created automatically)
- `requirements.txt`: Dependencies