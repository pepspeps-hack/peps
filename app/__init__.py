from flask import Flask

import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key') # It's better to set this via an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optional: to suppress a warning

db = SQLAlchemy(app)

# Import routes and models after the app and db objects are created to avoid circular imports
from app import routes
# We will create models.py content later, but it's good to have the import structure ready
from app import models # Ensure models are imported so SQLAlchemy knows about them
