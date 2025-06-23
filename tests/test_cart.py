import pytest
import json

class TestCart:
    """Test cart endpoints"""
    
    def test_get_empty_cart(self, client, auth_headers):
        """Test getting empty cart"""
        response = client.get('/api/cart', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'cart' in response_data
        assert response_data['cart']['total_items'] == 0
        assert len(response_data['cart']['items']) == 0
    
    def test_add_to_cart(self, client, auth_headers, product):
        """Test adding item to cart"""
        data = {
            'product_id': product.id,
            'quantity': 2
        }
        
        response = client.post('/api/cart/add',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'cart' in response_data
        assert response_data['cart']['total_items'] == 2
        assert len(response_data['cart']['items']) == 1
    
    def test_add_to_cart_invalid_product(self, client, auth_headers):
        """Test adding non-existent product to cart"""
        data = {
            'product_id': 'non-existent-id',
            'quantity': 1
        }
        
        response = client.post('/api/cart/add',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_add_to_cart_insufficient_inventory(self, client, auth_headers, product):
        """Test adding more items than available inventory"""
        data = {
            'product_id': product.id,
            'quantity': 999  # More than available
        }
        
        response = client.post('/api/cart/add',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Insufficient inventory' in response_data['error']
    
    def test_update_cart_item(self, client, auth_headers, cart_with_items):
        """Test updating cart item quantity"""
        cart_item = cart_with_items.items[0]
        data = {
            'quantity': 5
        }
        
        response = client.put(f'/api/cart/update/{cart_item.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['cart']['total_items'] == 5
    
    def test_update_cart_item_zero_quantity(self, client, auth_headers, cart_with_items):
        """Test updating cart item quantity to zero (should remove item)"""
        cart_item = cart_with_items.items[0]
        data = {
            'quantity': 0
        }
        
        response = client.put(f'/api/cart/update/{cart_item.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['cart']['total_items'] == 0
        assert len(response_data['cart']['items']) == 0
    
    def test_remove_cart_item(self, client, auth_headers, cart_with_items):
        """Test removing item from cart"""
        cart_item = cart_with_items.items[0]
        
        response = client.delete(f'/api/cart/remove/{cart_item.id}',
                               headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['cart']['total_items'] == 0
        assert len(response_data['cart']['items']) == 0
    
    def test_remove_cart_item_not_found(self, client, auth_headers):
        """Test removing non-existent cart item"""
        response = client.delete('/api/cart/remove/non-existent-id',
                               headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_clear_cart(self, client, auth_headers, cart_with_items):
        """Test clearing entire cart"""
        response = client.delete('/api/cart/clear', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['cart']['total_items'] == 0
        assert len(response_data['cart']['items']) == 0
    
    def test_get_cart_count(self, client, auth_headers, cart_with_items):
        """Test getting cart item count"""
        response = client.get('/api/cart/count', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'count' in response_data
        assert response_data['count'] == 2
    
    def test_validate_cart(self, client, auth_headers, cart_with_items):
        """Test validating cart"""
        response = client.post('/api/cart/validate',
                             headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'valid' in response_data
        assert 'issues' in response_data
        assert 'cart' in response_data
    
    def test_cart_unauthorized(self, client):
        """Test cart operations without authentication"""
        response = client.get('/api/cart')
        assert response.status_code == 401
        
        response = client.post('/api/cart/add')
        assert response.status_code == 401
        
        response = client.delete('/api/cart/clear')
        assert response.status_code == 401
