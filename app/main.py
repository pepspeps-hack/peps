from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'your_very_secret_key'  # Important for session management

# Dummy Product Data (in-memory)
# In a real application, this would come from a database
PRODUCTS = {
    1: {"id": 1, "name": "ChronosMaster Prestige", "brand": "Horologique", "price": 12500.00, "description": "A masterpiece of Swiss engineering, featuring a self-winding mechanical movement and a sapphire crystal case. Water-resistant up to 100 meters.", "image_url": "/static/images/watch1_placeholder.png", "specifications": {"Case Material": "Stainless Steel", "Movement": "Automatic", "Dial Color": "Black", "Strap": "Leather"}},
    2: {"id": 2, "name": "Aetheria Diamond", "brand": "Celestia", "price": 28750.00, "description": "Exquisite ladies' watch adorned with ethically sourced diamonds. Features a mother-of-pearl dial and a delicate rose gold bracelet.", "image_url": "/static/images/watch2_placeholder.png", "specifications": {"Case Material": "18k Rose Gold", "Movement": "Quartz", "Dial Color": "Mother of Pearl", "Strap": "Rose Gold Bracelet", "Gemstones": "Diamonds"}},
    3: {"id": 3, "name": "Titanium Sport X1", "brand": "Valiant", "price": 7800.00, "description": "Robust and lightweight sports watch, crafted from aerospace-grade titanium. Includes chronograph functions and a durable rubber strap.", "image_url": "/static/images/watch3_placeholder.png", "specifications": {"Case Material": "Titanium", "Movement": "Chronograph Quartz", "Dial Color": "Blue", "Strap": "Rubber", "Water Resistance": "200m"}},
    4: {"id": 4, "name": "Regal Classic", "brand": "Monarch", "price": 9950.00, "description": "Timeless design with a vintage appeal. Features a guilloché dial, Roman numerals, and a polished stainless steel case.", "image_url": "/static/images/watch4_placeholder.png", "specifications": {"Case Material": "Stainless Steel", "Movement": "Manual Wind", "Dial Color": "Silver", "Strap": "Alligator Leather"}},
}

# Helper function to get cart from session
def get_cart():
    if 'cart' not in session:
        session['cart'] = {} # {product_id: quantity}
    return session['cart']

# Helper function to calculate cart total
def calculate_cart_total(cart):
    total = 0
    for product_id, quantity in cart.items():
        product = PRODUCTS.get(int(product_id))
        if product:
            total += product['price'] * quantity
    return total

@app.route('/')
def index():
    # For now, all products are "featured"
    featured_products = list(PRODUCTS.values())
    return render_template('index.html', products=featured_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return "Product not found", 404 # Or render a 404 template

    # Get some related products (excluding the current one)
    related_products = [p for p_id, p in PRODUCTS.items() if p_id != product_id][:3] # Show up to 3

    return render_template('product_detail.html', product=product, related_products=related_products)

@app.route('/cart')
def cart():
    cart_data = get_cart()
    cart_items_detailed = []
    for product_id, quantity in cart_data.items():
        product = PRODUCTS.get(int(product_id))
        if product:
            cart_items_detailed.append({"product": product, "quantity": quantity})

    cart_total = calculate_cart_total(cart_data)
    return render_template('cart.html', cart_items=cart_items_detailed, cart_total=cart_total)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart_data = get_cart()
    quantity = int(request.form.get('quantity', 1))

    if product_id not in PRODUCTS:
        # Handle error: product not found
        return redirect(url_for('index')) # Or some error page

    str_product_id = str(product_id) # Session keys are strings
    if str_product_id in cart_data:
        cart_data[str_product_id] += quantity
    else:
        cart_data[str_product_id] = quantity

    session['cart'] = cart_data # Save cart back to session
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    cart_data = get_cart()
    str_product_id = str(product_id)
    quantity = int(request.form.get('quantity', 1))

    if str_product_id in cart_data:
        if quantity > 0:
            cart_data[str_product_id] = quantity
        else: # If quantity is 0 or less, remove item
            del cart_data[str_product_id]
        session['cart'] = cart_data
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_data = get_cart()
    str_product_id = str(product_id)
    if str_product_id in cart_data:
        del cart_data[str_product_id]
        session['cart'] = cart_data
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    cart_data = get_cart()
    if not cart_data:
        return redirect(url_for('cart')) # Can't checkout with an empty cart

    cart_items_detailed = []
    for product_id, quantity in cart_data.items():
        product = PRODUCTS.get(int(product_id))
        if product:
            cart_items_detailed.append({"product": product, "quantity": quantity})

    cart_total = calculate_cart_total(cart_data)
    return render_template('checkout.html', cart_items=cart_items_detailed, cart_total=cart_total)

@app.route('/checkout/process', methods=['POST'])
def process_checkout():
    # This is where payment processing and order creation would happen.
    # For now, it's just a placeholder.

    # Clear the cart after "successful" checkout
    session.pop('cart', None)

    # In a real app, you would save order details, send confirmation emails, etc.
    # For now, redirect to a thank you page or homepage.
    # return render_template('thank_you.html')
    return redirect(url_for('index')) # Redirect to homepage for now

if __name__ == '__main__':
    app.run(debug=True)
