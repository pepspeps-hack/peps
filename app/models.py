from datetime import datetime
from app import db # db object is created in app/__init__.py

# Association table for the many-to-many relationship between Order and Product
# This allows an order to have multiple products and a product to be in multiple orders (with different quantities)
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False, default=1)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False) # In a real app, this would be longer
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False) # Consider using db.Numeric for precision with currency
    image_file = db.Column(db.String(20), nullable=False, default='default_product.jpg')
    stock = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False, default=0.0) # This would be calculated
    paid = db.Column(db.Boolean, default=False)

    # Relationship to products through the association table 'order_items'
    # 'secondary' points to the association table
    # 'back_populates' is used if Product needs a direct link back to orders it's part of
    # For simplicity here, we might not need a direct products.orders relationship on Product model
    # but the association table itself allows querying.
    # A more explicit OrderItem model might be used for more complex item properties (e.g. price at time of order)
    products = db.relationship('Product', secondary=order_items, lazy='subquery',
                               backref=db.backref('orders_associated', lazy=True))

    def __repr__(self):
        return f"Order('Order ID: {self.id}', 'User ID: {self.user_id}', 'Date: {self.date_ordered}')"

# To make this work, we also need to import models in app/__init__.py
# The line `from app import models` should be uncommented or added if not present.
# And we'd need to create the database from a Python shell:
# from app import db, app
# app.app_context().push()
# db.create_all()
