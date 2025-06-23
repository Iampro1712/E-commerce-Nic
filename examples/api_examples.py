#!/usr/bin/env python3
"""
API Usage Examples
Run this script to test the API endpoints
"""
import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:5000/api"

class APIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
    
    def set_auth_token(self, token):
        """Set authentication token"""
        self.access_token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def post(self, endpoint, data=None):
        """POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return response
    
    def get(self, endpoint, params=None):
        """GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return response
    
    def put(self, endpoint, data=None):
        """PUT request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data)
        return response
    
    def delete(self, endpoint):
        """DELETE request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return response

def print_response(response, title="Response"):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*50}")

def test_api():
    """Test API endpoints"""
    client = APIClient()
    
    print("🚀 Testing E-commerce API")
    
    # 1. Health Check
    print("\n1. Health Check")
    response = client.get("/health")
    print_response(response, "Health Check")
    
    # 2. Register User
    print("\n2. Register User")
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+505 8888-8888"
    }
    response = client.post("/auth/register", user_data)
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        data = response.json()
        client.set_auth_token(data['access_token'])
        print("✅ Authentication token set")
    
    # 3. Login (alternative)
    print("\n3. Login User")
    login_data = {
        "email": "user@dev.com",
        "password": "user123"
    }
    response = client.post("/auth/login", login_data)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        data = response.json()
        client.set_auth_token(data['access_token'])
        print("✅ Authentication token set from login")
    
    # 4. Get Profile
    print("\n4. Get User Profile")
    response = client.get("/auth/profile")
    print_response(response, "User Profile")
    
    # 5. Get Categories
    print("\n5. Get Categories")
    response = client.get("/products/categories")
    print_response(response, "Categories")
    
    # 6. Get Products
    print("\n6. Get Products")
    response = client.get("/products")
    print_response(response, "Products")
    
    # Store product ID for cart operations
    product_id = None
    if response.status_code == 200:
        data = response.json()
        if data['products']:
            product_id = data['products'][0]['id']
    
    # 7. Get Specific Product
    if product_id:
        print(f"\n7. Get Product {product_id}")
        response = client.get(f"/products/{product_id}")
        print_response(response, "Single Product")
    
    # 8. Search Products
    print("\n8. Search Products")
    response = client.get("/products", params={"q": "smartphone", "min_price": 100})
    print_response(response, "Product Search")
    
    # 9. Get Cart
    print("\n9. Get Cart")
    response = client.get("/cart")
    print_response(response, "Cart")
    
    # 10. Add to Cart
    if product_id:
        print(f"\n10. Add Product to Cart")
        cart_data = {
            "product_id": product_id,
            "quantity": 2
        }
        response = client.post("/cart/add", cart_data)
        print_response(response, "Add to Cart")
    
    # 11. Get Cart Count
    print("\n11. Get Cart Count")
    response = client.get("/cart/count")
    print_response(response, "Cart Count")
    
    # 12. Validate Cart
    print("\n12. Validate Cart")
    response = client.post("/cart/validate")
    print_response(response, "Cart Validation")
    
    # 13. Get Orders
    print("\n13. Get Orders")
    response = client.get("/orders")
    print_response(response, "Orders")
    
    # 14. Add Address
    print("\n14. Add Address")
    address_data = {
        "type": "shipping",
        "first_name": "Test",
        "last_name": "User",
        "address_line_1": "Calle Principal 123",
        "city": "Managua",
        "state": "Managua",
        "postal_code": "12345",
        "country": "NI",
        "phone": "+505 8888-8888",
        "is_default": True
    }
    response = client.post("/auth/addresses", address_data)
    print_response(response, "Add Address")
    
    # 15. Get Addresses
    print("\n15. Get Addresses")
    response = client.get("/auth/addresses")
    print_response(response, "Addresses")
    
    print("\n🎉 API Testing Complete!")
    print("\nNext steps:")
    print("- Set up MySQL database for production")
    print("- Configure PayPal API keys for payments")
    print("- Test payment flows")
    print("- Deploy to production server")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("Make sure the server is running: python run_dev.py")
    except Exception as e:
        print(f"❌ Error: {e}")
