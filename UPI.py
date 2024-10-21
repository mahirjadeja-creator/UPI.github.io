from flask import Flask, request, jsonify
import sqlite3
import random  # type: ignore
import string # type: ignore

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    
    # Create table to store orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            food_item TEXT NOT NULL,
            upi_id TEXT NOT NULL,
            payment_status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Simulate food item selection and generating an order ID
def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    food_item = data.get('food_item')
    upi_id = data.get('upi_id')
    
    if not food_item or not upi_id:
        return jsonify({"error": "Food item and UPI ID are required"}), 400

    order_id = generate_order_id()
    
    # Insert order into the database with 'pending' payment status
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (order_id, food_item, upi_id, payment_status)
        VALUES (?, ?, ?, ?)
    ''', (order_id, food_item, upi_id, 'pending'))
    conn.commit()
    conn.close()

    return jsonify({"message": "Order created successfully", "order_id": order_id})

# Simulate UPI payment verification (in real-world, this would be an actual API call)
def verify_upi_payment(upi_id, order_id):
    # Simulate a success/failure scenario
    return random.choice([True, False])

@app.route('/payment', methods=['POST'])
def process_payment():
    data = request.json
    order_id = data.get('order_id')
    upi_id = data.get('upi_id')

    if not order_id or not upi_id:
        return jsonify({"error": "Order ID and UPI ID are required"}), 400

    # Check if the order exists and has pending payment
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = ? AND upi_id = ? AND payment_status = ?', (order_id, upi_id, 'pending'))
    order = cursor.fetchone()

    if not order:
        return jsonify({"error": "No pending order found for this UPI ID and Order ID"}), 404
    
    # Simulate payment verification
    payment_success = verify_upi_payment(upi_id, order_id)
    
    if payment_success:
        # Update payment status to 'completed'
        cursor.execute('UPDATE orders SET payment_status = ? WHERE order_id = ?', ('completed', order_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Payment successful", "order_id": order_id, "food_item": order[1]})
    else:
        conn.close()
        return jsonify({"message": "Payment failed"}), 400

# Get order status
@app.route('/order/status/<order_id>', methods=['GET'])
def get_order_status(order_id):
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()

    if order:
        return jsonify({
            "order_id": order[0],
            "food_item": order[1],
            "upi_id": order[2],
            "payment_status": order[3]
        })
    else:
        return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
