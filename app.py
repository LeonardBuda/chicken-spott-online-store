from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import random
import requests
import time
from firebase_admin import credentials, initialize_app, firestore

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Add custom floatformat filter for Jinja2
def floatformat(value, decimal_places=2):
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['floatformat'] = floatformat

# Initialize Firebase
firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_credentials:
    cred = credentials.Certificate(json.loads(firebase_credentials))
else:
    cred_path = 'chicken-spott-firebase-adminsdk-fbsvc-978ce982ec.json'
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        raise FileNotFoundError(f"Firebase credentials file '{cred_path}' not found.")
firebase_app = initialize_app(cred)
db = firestore.client()

# Menu data
menu = {
    "Chicken Menu": {
        "Meals": [
            {"name": "1/4 Chicken", "price": 35.00},
            {"name": "1/2 Chicken", "price": 65.00},
            {"name": "Full Chicken", "price": 120.00}
        ],
        "Plates": [
            {"name": "1/4 Chicken Plate", "price": 60.00},
            {"name": "1/2 Chicken Plate", "price": 90.00},
            {"name": "Full Chicken Plate", "price": 160.00}
        ],
        "Combos": [
            {"name": "1/4 Chicken Plate + 440ml Coke", "price": 77.00},
            {"name": "1/4 Chicken Plate + 500ml Bon Aqua Still", "price": 70.00},
            {"name": "1/2 Chicken Plate + 440ml Coke", "price": 107.00},
            {"name": "Full Chicken Plate + 2L Coke", "price": 190.00},
            {"name": "1/4 Chicken Plate + 330ml Cappy Juice", "price": 76.00}
        ]
    },
    "Kota Menu": {
        "Kotas": [
            {"name": "Chips, Secret Dressing, Jalapeño, Cheese, Egg, Chicken Burger", "price": 50.00},
            {"name": "Chips, Secret Dressing, Jalapeño, Cheese, Egg, Russian", "price": 60.00},
            {"name": "Chips, Secret Dressing, Jalapeño, Cheese, Egg, Beef Burger, Bacon", "price": 70.00},
            {"name": "Chips, Secret Dressing, Jalapeño, Cheese, Egg, Chicken Burger, Russian", "price": 75.00}
        ],
        "Slices": [
            {"name": "Chips, Secret Dressing, Egg, Cheese, Chicken Burger", "price": 50.00},
            {"name": "Chips, Secret Dressing, Egg, Cheese, Beef Burger, Bacon", "price": 70.00},
            {"name": "Chips, Secret Dressing, Egg, Cheese, Chicken Burger, Russian", "price": 75.00},
            {"name": "Chips, Secret Dressing, Egg, Cheese, Boneless Rib, Russian", "price": 85.00}
        ],
        "Babalazi Chips": [
            {"name": "Small Chips, Chakalaka, 1x Russian", "price": 50.00},
            {"name": "Medium Chips, Chakalaka, 2x Russian", "price": 95.00},
            {"name": "Large Chips, Chakalaka, 4x Russian", "price": 135.00},
            {"name": "Small Chips + Quarter Chicken + Chakalaka", "price": 70.00},
            {"name": "Small Chips + Quarter Chicken + Full Russian + Chakalaka", "price": 90.00},
            {"name": "Medium Chips + Half Chicken + Chakalaka", "price": 90.00},
            {"name": "Medium Chips + Half Chicken + 2x Russian + Chakalaka", "price": 130.00},
            {"name": "Large Chips + Full Chicken + Chakalaka", "price": 160.00},
            {"name": "Large Chips + Full Chicken + 4x Russian + Chakalaka", "price": 250.00}
        ]
    },
    "010 Cafe Menu": {
        "Kotas": [
            {"name": "Egg, Cheese, Polony, Special", "price": 30.00},
            {"name": "Egg, Cheese, Vienna, Polony, Special", "price": 39.00},
            {"name": "Egg, Cheese, Russian, Polony, Special", "price": 50.00},
            {"name": "Egg, Cheese, Vienna, Chicken Burger, Polony, Special", "price": 52.00},
            {"name": "Egg, Cheese, Russian, Chicken Burger, Polony, Special", "price": 60.00},
            {"name": "Egg, Cheese, Russian, Chicken Burger, Vienna, Polony, Special", "price": 65.00},
            {"name": "Egg, Cheese, Russian, Beef Burger, Vienna, Polony, Special", "price": 78.00}
        ],
        "Rib Kotas": [
            {"name": "Egg, Cheese, Boneless Rib", "price": 60.00},
            {"name": "Egg, Cheese, Boneless Rib, Chicken Burger", "price": 70.00},
            {"name": "Egg, Cheese, Boneless Rib, Bacon", "price": 75.00},
            {"name": "Egg, Cheese, Boneless Rib, Chicken Burger, Bacon", "price": 90.00},
            {"name": "Egg, Cheese, Boneless Rib, Chicken Burger, Russian", "price": 115.00}
        ],
        "Kream Dala Kream": [
            {"name": "Slices Topped with Cheese/Beef Burger, Chips, Cheese, Special, Bacon and Beef", "price": 75.00},
            {"name": "Slices Topped with Cheese/Beef Burger, Pieces, Chips, Cheese, Special, Egg, Russian and Beef", "price": 65.00}
        ],
        "Burgers": [
            {"name": "Chicken Burger with Chips (Lettuce, Tomato, Cheese, Egg, Chicken Patty)", "price": 50.00},
            {"name": "Beef Burger (Lettuce, Tomato, Cheese, Egg, Beef Patty)", "price": 65.00},
            {"name": "Boneless Rib Burger (Lettuce, Tomato, Cheese, Egg, Boneless Rib Patty)", "price": 75.00}
        ],
        "Dagwoods": [
            {"name": "Boring Dagwood (Lettuce, Tomato, Egg, 2x Beef, 2x Cheese)", "price": 65.00},
            {"name": "Proper Dagwood (Lettuce, Tomato, Egg, Cheese, Boneless Rib, Chicken Burger, Russian)", "price": 115.00}
        ],
        "Slices": [
            {"name": "Egg, Cheese, Chicken Burger, Polony, Special", "price": 40.00},
            {"name": "Egg, Cheese, Russian, Polony, Special", "price": 50.00},
            {"name": "Egg, Cheese, Vienna, Chicken Burger, Polony, Special", "price": 52.00},
            {"name": "Egg, Cheese, Russian, Chicken Burger, Polony, Special", "price": 60.00},
            {"name": "Egg, Cheese, Russian, Chicken Burger, Vienna, Polony, Special", "price": 65.00},
            {"name": "Egg, Cheese, Russian, Beef Burger, Vienna, Polony, Special", "price": 78.00}
        ]
    },
    "Weighed Meat": [
        {"name": "Heart"},
        {"name": "Liver"},
        {"name": "Kidneys"},
        {"name": "Short Ribs"},
        {"name": "Steak"},
        {"name": "Wors"}
    ],
    "Sides Menu": [
        {"name": "Small Pap", "price": 10.00},
        {"name": "Medium Pap", "price": 20.00},
        {"name": "Large Pap", "price": 30.00},
        {"name": "Chakalaka Mild", "price": 15.00},
        {"name": "Chakalaka Hot", "price": 15.00},
        {"name": "Salad Mix (Onion + Green Pepper)", "price": 10.00},
        {"name": "Extra Chakalaka (small bottle)", "price": 15.00},
        {"name": "Salad Mix (extra)", "price": 20.00},
        {"name": "Chicken Feet", "price": 2.00},
        {"name": "Chicken Gizzards", "price": 6.00}
    ],
    "Drinks Menu": [
        {"name": "330ml Coke (or other available flavours)", "price": 12.00},
        {"name": "440ml Coke (or other available flavours)", "price": 15.00},
        {"name": "500ml Bon Aqua Still Water", "price": 10.00},
        {"name": "330ml Cappy Juice", "price": 15.00},
        {"name": "2L Coke", "price": 21.00}
    ],
    "Specials": [
        {"name": "1/4 Chicken Plate + 440ml Coke", "price": 70.00},
        {"name": "1/2 Chicken Plate + (2x 440ml Coke)", "price": 100.00},
        {"name": "Pensioner’s Special (1/4 Chicken Plate + 440ml Coke)", "price": 60.00}
    ]
}

# Global variables
used_order_numbers = set()
next_order_number = 1  # Reset to start at #0001 and increment sequentially
remembered_customer = {}  # Initialize remembered_customer as an empty dictionary

# Generate unique order number
def generate_order_number():
    global next_order_number
    order_number = f"#{next_order_number:04d}"
    next_order_number += 1
    return order_number

# Send Telegram notification
def send_telegram_notification(order_number, cart, total, customer_details, delivery_address=None, payment_method=None):
    bot_token = "7984570465:AAEOci3s55Pg07REgZR74W-8SrtqsG4GLPE"
    chat_id = "-1002522817592"
    message = f"Order Number: {order_number}\n\nCustomer Details:\nName: {customer_details['name']}\nSurname: {customer_details.get('surname', 'N/A')}\nPhone: {customer_details['phone']}\nEmail: {customer_details['email']}\n\nOrder Details:\n"
    for item in cart:
        if 'quantity' in item:
            message += f"{item['name']} - R{item['amount']:.2f} x {item['quantity']} = R{item['total']:.2f}\n"
        else:
            message += f"{item['name']} - R{item['amount']:.2f}\n"
    if delivery_address:
        delivery_fee = total - sum(item['total'] for item in cart if 'total' in item)
        message += f"\nDelivery Address: {delivery_address}\nDelivery Fee: R{delivery_fee:.2f}\n"
    message += f"\nPayment Method: {payment_method}\n"
    message += f"Total: R{total:.2f} 💸\nTime: {time.strftime('%I:%M %p SAST, %B %d, %Y')} ⏰"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=params, timeout=10)
        if response.status_code == 200 and response.json().get("ok"):
            print("Notification sent successfully! ✅")
        else:
            print(f"Failed to send notification: {response.text} ⚠️")
    except Exception as e:
        print(f"Failed to send notification: {e} ⚠️")

# Placeholder payment processing
def process_payment(total, payment_method, order_number):
    print(f"Processing payment of R{total:.2f} via {payment_method} for order {order_number}... 💳")
    return True

# Calculate distance
def calculate_distance(origin, destination, api_key):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {"origins": origin, "destinations": destination, "mode": "driving", "key": api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data["status"] == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
            distance_meters = data["rows"][0]["elements"][0]["distance"]["value"]
            return distance_meters / 1000
        else:
            print(f"Distance Matrix API Error: {data.get('error_message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Distance calculation request failed: {e}")
        return None

# Add fixed-price item with flavor
def add_fixed_price_item(item, quantity, flavor):
    flavored_name = f"{item['name']} ({flavor})" if flavor != "All-In-One" else item['name']
    total = item["price"] * quantity
    cart_ref = db.collection('carts').document()
    cart_ref.set({"name": flavored_name, "amount": item["price"], "quantity": quantity, "total": total})
    return f"Added {quantity} x {flavored_name} to cart! 🍽️"

# Add fixed-price item without flavor
def add_fixed_price_item_no_flavor(item, quantity):
    total = item["price"] * quantity
    cart_ref = db.collection('carts').document()
    cart_ref.set({"name": item["name"], "amount": item["price"], "quantity": quantity, "total": total})
    return f"Added {quantity} x {item['name']} to cart! 🍽️"

# Add weighed item
def add_weighed_item(item, amount):
    cart_ref = db.collection('carts').document()
    cart_ref.set({"name": item["name"], "amount": amount})
    return f"Added {item['name']} worth R{amount:.2f} to cart! 🥩"

# Add Kream Dala Kream item
def add_kream_dala_kream(item, quantity, burger_type):
    flavored_name = f"{item['name']} ({burger_type} Burger)"
    total = item["price"] * quantity
    cart_ref = db.collection('carts').document()
    cart_ref.set({"name": flavored_name, "amount": item["price"], "quantity": quantity, "total": total})
    return f"Added {quantity} x {flavored_name} to cart! 🍔"

# Remove item from cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        item_name = request.form.get('name')
        if not item_name:
            return jsonify({"error": "Item name is required"}), 400
        cart_items = [doc for doc in db.collection('carts').where('name', '==', item_name).get()]
        if not cart_items:
            return jsonify({"error": "Item not found in cart"}), 404
        for doc in cart_items:
            doc.reference.delete()
        return jsonify({"message": f"Removed {item_name} from cart!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to remove item: {str(e)}"}), 500

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/store_location')
def store_location():
    return render_template('store_location.html')

@app.route('/menus')
def menus():
    return render_template('menus.html', menu=menu)

@app.route('/chicken_menu')
def chicken_menu():
    return render_template('chicken_menu.html', menu=menu["Chicken Menu"])

@app.route('/kota_menu')
def kota_menu():
    return render_template('kota_menu.html', menu=menu["Kota Menu"])

@app.route('/010_cafe_menu')
def cafe_menu():
    return render_template('010_cafe_menu.html', menu=menu["010 Cafe Menu"])

@app.route('/weighed_meat')
def weighed_meat():
    return render_template('weighed_meat.html', menu=menu["Weighed Meat"])

@app.route('/sides_menu')
def sides_menu():
    return render_template('sides_menu.html', menu=menu["Sides Menu"])

@app.route('/drinks_menu')
def drinks_menu():
    return render_template('drinks_menu.html', menu=menu["Drinks Menu"])

@app.route('/specials')
def specials():
    return render_template('specials.html', menu=menu["Specials"])

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.form
    item_name = data.get('name')
    quantity = int(data.get('quantity', 1))
    flavor = data.get('flavor', 'All-In-One')
    burger_type = data.get('burger_type', 'Cheese')
    amount = float(data.get('amount', 0))

    item = None
    category_name = None
    subcat = None
    for cat_name, category in menu.items():
        if isinstance(category, dict):
            for sub, items in category.items():
                for i in items:
                    if i['name'] == item_name:
                        item = i
                        category_name = cat_name
                        subcat = sub
                        break
                if item:
                    break
        else:
            for i in category:
                if i['name'] == item_name:
                    item = i
                    category_name = cat_name
                    break
            if item:
                break

    if not item:
        return jsonify({"error": "Item not found in menu"}), 404

    try:
        if quantity <= 0 and amount <= 0:
            return jsonify({"error": "Quantity or amount must be positive"}), 400

        # Apply flavor to all relevant categories
        if category_name in ["Chicken Menu", "Specials"] or (category_name == "Kota Menu" and subcat == "Babalazi Chips" and "Chakalaka" in item_name and item_name not in ["Small Chips, Chakalaka, 1x Russian", "Medium Chips, Chakalaka, 2x Russian", "Large Chips, Chakalaka, 4x Russian"]) or (category_name == "Sides Menu" and item_name in ["Chicken Feet", "Chicken Gizzards"]):
            message = add_fixed_price_item(item, quantity, flavor)
        elif category_name == "010 Cafe Menu" and subcat == "Kream Dala Kream":
            message = add_kream_dala_kream(item, quantity, burger_type)
        elif category_name == "Weighed Meat":
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
            message = add_weighed_item(item, amount)
        else:
            message = add_fixed_price_item_no_flavor(item, quantity)

        return jsonify({"message": message}), 200
    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/view_cart')
def view_cart():
    try:
        cart_items = [doc.to_dict() for doc in db.collection('carts').get()]
        total = sum(item['total'] if 'total' in item else item['amount'] for item in cart_items)
        return render_template('cart.html', cart_items=cart_items, total=total)
    except Exception as e:
        return jsonify({"error": f"Failed to load cart: {str(e)}"}), 500

@app.route('/clear_cart')
def clear_cart():
    try:
        for doc in db.collection('carts').get():
            doc.reference.delete()
        return redirect(url_for('view_cart'))
    except Exception as e:
        return jsonify({"error": f"Failed to clear cart: {str(e)}"}), 500

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            phone = request.form['phone'].strip()
            email = request.form['email'].strip()
            surname = request.form.get('surname', '').strip() or 'N/A'
            address = request.form.get('address', '').strip()
            delivery = request.form.get('delivery') == 'true'
            payment_method = request.form.get('payment_method')
            remember = bool(request.form.get('remember'))

            if not name or not phone or not email:
                return jsonify({"error": "Name, phone, and email are required"}), 400
            if not payment_method:
                return jsonify({"error": "Payment method is required"}), 400
            if payment_method not in ["Cash on delivery", "Cash on collection", "Card on delivery", "Card on collection", "In-App"]:
                return jsonify({"error": "Invalid payment method"}), 400
            if payment_method == "In-App":
                return jsonify({"error": "In-App payment is coming soon and not available yet"}), 400

            if remember:
                remembered_customer.update({"name": name, "surname": surname, "phone": phone, "email": email, "remembered": True})

            customer_details = {"name": name, "surname": surname, "phone": phone, "email": email}
            cart_items = [doc.to_dict() for doc in db.collection('carts').get()]
            base_total = sum(item['total'] if 'total' in item else item['amount'] for item in cart_items)

            if not cart_items:
                return jsonify({"error": "Cart is empty"}), 400

            if delivery and address:
                distance_km = calculate_distance("30558 Heald Street, Esihlahleni, Daveyton 1520, South Africa", address, "AIzaSyCJWK5ofMwuWcadVHGyGoMwmz7akNR3av0")
                if distance_km is None:
                    return jsonify({"error": "Could not calculate delivery distance"}), 500
                delivery_fee = distance_km * 6.00
                final_total = base_total + delivery_fee
                order_number = generate_order_number()
                send_telegram_notification(order_number, cart_items, final_total, customer_details, address, payment_method)
                process_payment(final_total, payment_method, order_number)
                for doc in db.collection('carts').get():
                    doc.reference.delete()
                return jsonify({"message": f"Delivery order {order_number} placed! Total: R{final_total:.2f} (Delivery Fee: R{delivery_fee:.2f}, {distance_km:.2f} km)", "stay": True}), 200
            else:
                order_number = generate_order_number()
                send_telegram_notification(order_number, cart_items, base_total, customer_details, None, payment_method)
                process_payment(base_total, payment_method, order_number)
                for doc in db.collection('carts').get():
                    doc.reference.delete()
                return jsonify({"message": f"Collection order {order_number} placed! Total: R{base_total:.2f}", "stay": True}), 200
        except ValueError as ve:
            return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Checkout failed: {str(e)}"}), 500

    try:
        cart_items = [doc.to_dict() for doc in db.collection('carts').get()]
        total = sum(item['total'] if 'total' in item else item['amount'] for item in cart_items)
        return render_template('checkout.html', total=total, remembered_customer=remembered_customer)
    except Exception as e:
        return jsonify({"error": f"Failed to load checkout: {str(e)}"}), 500

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/rate_us', methods=['GET', 'POST'])
def rate_us():
    if request.method == 'POST':
        try:
            rating = request.form.get('rating')
            comment = request.form.get('comment', '')
            if not rating:
                return jsonify({"error": "Rating is required"}), 400
            db.collection('ratings').document().set({"rating": int(rating), "comment": comment, "timestamp": time.time()})
            return jsonify({"message": "Thank you for your rating!"}), 200
        except ValueError as ve:
            return jsonify({"error": f"Invalid rating: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Rating submission failed: {str(e)}"}), 500
    return render_template('rate_us.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            message = request.form['message'].strip()
            if not name or not email or not message:
                return jsonify({"error": "All fields are required"}), 400
            db.collection('contacts').document().set({"name": name, "email": email, "message": message, "timestamp": time.time()})
            bot_token = "7984570465:AAEOci3s55Pg07REgZR74W-8SrtqsG4GLPE"
            chat_id = "-1002522817592"
            notification_message = f"New Contact Message 📬\nName: {name} 🌟\nEmail: {email} ✉️\nMessage: {message} 📝\nTime: {time.strftime('%I:%M %p SAST, %B %d, %Y')} ⏰"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            params = {"chat_id": chat_id, "text": notification_message}
            response = requests.post(url, data=params, timeout=10)
            if response.status_code != 200 or not response.json().get("ok"):
                print(f"Failed to send contact notification: {response.text} ⚠️")
            return jsonify({"message": "Message sent successfully! 🚀"}), 200
        except Exception as e:
            return jsonify({"error": f"Contact submission failed: {str(e)}"}), 500
    return render_template('contact.html')

@app.route('/track_order', methods=['GET', 'POST'])
def track_order():
    if request.method == 'POST':
        try:
            order_number = request.form['order_number'].strip()
            phone = request.form['phone'].strip()
            if not order_number or not phone:
                return jsonify({"error": "Order number and phone are required"}), 400
            db.collection('tracking_requests').document().set({"order_number": order_number, "phone": phone, "timestamp": time.time()})
            bot_token = "7984570465:AAEOci3s55Pg07REgZR74W-8SrtqsG4GLPE"
            chat_id = "-1002522817592"
            notification_message = f"New Order Tracking Request 📬\nOrder Number: {order_number} 🌟\nPhone: {phone} 📱\nTime: {time.strftime('%I:%M %p SAST, %B %d, %Y')} ⏰\nPlease follow up! 🚨"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            params = {"chat_id": chat_id, "text": notification_message}
            response = requests.post(url, data=params, timeout=10)
            if response.status_code != 200 or not response.json().get("ok"):
                print(f"Failed to send tracking request notification: {response.text} ⚠️")
            return jsonify({"message": "Request submitted! We’ll get back to you soon. 🚀"}), 200
        except Exception as e:
            return jsonify({"error": f"Tracking request failed: {str(e)}"}), 500
    return render_template('track_order.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)