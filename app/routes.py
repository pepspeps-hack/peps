from flask import render_template, url_for
from app import app

# Dummy data - will be replaced by database queries later
dummy_products = [
    {'id': 1, 'name': 'Awesome T-Shirt', 'description': 'A really awesome t-shirt.', 'price': 25.99, 'image_file': 'tshirt.jpg', 'stock': 10},
    {'id': 2, 'name': 'Cool Mug', 'description': 'A mug that keeps your coffee cool.', 'price': 15.00, 'image_file': 'mug.jpg', 'stock': 5},
    {'id': 3, 'name': 'Fancy Hat', 'description': 'A very fancy hat for special occasions.', 'price': 45.50, 'image_file': 'hat.jpg', 'stock': 0},
]

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Welcome')

@app.route('/products')
def products():
    return render_template('products.html', title='Products', products=dummy_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in dummy_products if p['id'] == product_id), None)
    if product:
        return render_template('product_detail.html', title=product['name'], product=product)
    return "Product not found", 404

# We will add more routes for cart, user auth, etc. later.
