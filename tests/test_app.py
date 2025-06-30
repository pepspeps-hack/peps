import unittest
import sys
import os

# Add the parent directory (project root) to the Python path
# to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, routes

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        # Propagate the exceptions to the test client
        self.app.testing = True
        # Push an application context
        self.app_context = app.app_context()
        self.app_context.push()


    def tearDown(self):
        self.app_context.pop()

    def test_index_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome - E-commerce Site", response.data) # Check for the title
        self.assertIn(b"Welcome to our E-commerce Site!", response.data) # Check for content

    def test_products_page(self):
        response = self.app.get('/products', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Our Products", response.data)
        # Check if dummy product names are present
        self.assertIn(b"Awesome T-Shirt", response.data)
        self.assertIn(b"Cool Mug", response.data)

    def test_product_detail_page_valid(self):
        # Test with the first product from dummy_products
        product_id = routes.dummy_products[0]['id']
        product_name = routes.dummy_products[0]['name'].encode('utf-8') # Encode to bytes for assertion

        response = self.app.get(f'/product/{product_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(product_name, response.data)
        self.assertIn(b"Description:", response.data)
        self.assertIn(b"Price:", response.data)

    def test_product_detail_page_invalid(self):
        invalid_product_id = 999 # An ID that doesn't exist in dummy_products
        response = self.app.get(f'/product/{invalid_product_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Product not found", response.data)

if __name__ == '__main__':
    unittest.main()
