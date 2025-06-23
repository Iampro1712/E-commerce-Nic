import pytest
import json

class TestProducts:
    """Test product endpoints"""
    
    def test_get_products(self, client, product):
        """Test getting products list"""
        response = client.get('/api/products')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'products' in response_data
        assert 'pagination' in response_data
        assert len(response_data['products']) >= 1
    
    def test_get_products_with_search(self, client, product):
        """Test getting products with search"""
        response = client.get('/api/products?q=Test')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['products']) >= 1
        assert 'Test' in response_data['products'][0]['name']
    
    def test_get_products_with_filters(self, client, product):
        """Test getting products with filters"""
        response = client.get(f'/api/products?category_id={product.category_id}&min_price=20&max_price=50')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['products']) >= 1
    
    def test_get_product_by_id(self, client, product):
        """Test getting specific product"""
        response = client.get(f'/api/products/{product.id}')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'product' in response_data
        assert response_data['product']['id'] == product.id
    
    def test_get_product_not_found(self, client):
        """Test getting non-existent product"""
        response = client.get('/api/products/non-existent-id')
        
        assert response.status_code == 404
    
    def test_create_product_admin(self, client, admin_headers, category):
        """Test creating product as admin"""
        data = {
            'name': 'New Test Product',
            'description': 'New test product description',
            'sku': 'NEW-TEST-001',
            'slug': 'new-test-product',
            'price': 39.99,
            'category_id': category.id,
            'inventory_quantity': 20,
            'is_active': True
        }
        
        response = client.post('/api/products',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert 'product' in response_data
        assert response_data['product']['name'] == data['name']
    
    def test_create_product_unauthorized(self, client, auth_headers, category):
        """Test creating product as regular user (should fail)"""
        data = {
            'name': 'New Test Product',
            'description': 'New test product description',
            'sku': 'NEW-TEST-001',
            'slug': 'new-test-product',
            'price': 39.99,
            'category_id': category.id
        }
        
        response = client.post('/api/products',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_update_product_admin(self, client, admin_headers, product):
        """Test updating product as admin"""
        data = {
            'name': 'Updated Product Name',
            'price': 49.99
        }
        
        response = client.put(f'/api/products/{product.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=admin_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['product']['name'] == data['name']
        assert float(response_data['product']['price']) == data['price']
    
    def test_delete_product_admin(self, client, admin_headers, product):
        """Test deleting product as admin"""
        response = client.delete(f'/api/products/{product.id}',
                               headers=admin_headers)
        
        assert response.status_code == 200
    
    def test_get_categories(self, client, category):
        """Test getting categories"""
        response = client.get('/api/products/categories')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'categories' in response_data
        assert len(response_data['categories']) >= 1
    
    def test_create_category_admin(self, client, admin_headers):
        """Test creating category as admin"""
        data = {
            'name': 'New Category',
            'slug': 'new-category',
            'description': 'New category description',
            'is_active': True
        }
        
        response = client.post('/api/products/categories',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert 'category' in response_data
        assert response_data['category']['name'] == data['name']
    
    def test_create_category_duplicate_slug(self, client, admin_headers, category):
        """Test creating category with duplicate slug"""
        data = {
            'name': 'Another Category',
            'slug': category.slug,  # Duplicate slug
            'description': 'Another category description'
        }
        
        response = client.post('/api/products/categories',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'slug already exists' in response_data['error']
