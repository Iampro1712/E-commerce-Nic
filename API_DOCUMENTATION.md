# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Response Format
All responses follow this format:
```json
{
  "message": "Success message",
  "data": { ... },
  "error": "Error message (if any)"
}
```

## Error Codes
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## Authentication Endpoints

### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "Password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+505 8888-8888"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": { ... },
  "access_token": "jwt-token",
  "refresh_token": "refresh-token"
}
```

### Login User
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "Password123"
}
```

### Get Profile
```http
GET /auth/profile
```
*Requires authentication*

### Update Profile
```http
PUT /auth/profile
```
*Requires authentication*

**Request Body:**
```json
{
  "first_name": "Updated Name",
  "last_name": "Updated Last",
  "phone": "+505 9999-9999"
}
```

### Change Password
```http
POST /auth/change-password
```
*Requires authentication*

**Request Body:**
```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword123"
}
```

---

## Product Endpoints

### Get Products
```http
GET /products
```

**Query Parameters:**
- `q` - Search query
- `category_id` - Filter by category
- `min_price` - Minimum price
- `max_price` - Maximum price
- `is_featured` - Filter featured products
- `in_stock` - Filter in-stock products
- `sort_by` - Sort field (name, price, created_at)
- `sort_order` - Sort order (asc, desc)
- `page` - Page number
- `per_page` - Items per page

**Example:**
```http
GET /products?q=smartphone&category_id=123&min_price=100&max_price=1000&page=1&per_page=20
```

### Get Product
```http
GET /products/{id}
```

### Create Product (Admin)
```http
POST /products
```
*Requires admin authentication*

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "sku": "PROD-001",
  "slug": "new-product",
  "price": 99.99,
  "compare_price": 129.99,
  "category_id": "category-uuid",
  "inventory_quantity": 50,
  "is_active": true,
  "is_featured": false,
  "images": [
    {
      "image_url": "https://example.com/image.jpg",
      "alt_text": "Product image",
      "is_primary": true
    }
  ]
}
```

### Update Product (Admin)
```http
PUT /products/{id}
```
*Requires admin authentication*

### Delete Product (Admin)
```http
DELETE /products/{id}
```
*Requires admin authentication*

---

## Category Endpoints

### Get Categories
```http
GET /products/categories
```

### Create Category (Admin)
```http
POST /products/categories
```
*Requires admin authentication*

**Request Body:**
```json
{
  "name": "New Category",
  "slug": "new-category",
  "description": "Category description",
  "is_active": true,
  "sort_order": 1
}
```

---

## Cart Endpoints

### Get Cart
```http
GET /cart
```
*Requires authentication*

### Add to Cart
```http
POST /cart/add
```
*Requires authentication*

**Request Body:**
```json
{
  "product_id": "product-uuid",
  "quantity": 2
}
```

### Update Cart Item
```http
PUT /cart/update/{item_id}
```
*Requires authentication*

**Request Body:**
```json
{
  "quantity": 3
}
```

### Remove Cart Item
```http
DELETE /cart/remove/{item_id}
```
*Requires authentication*

### Clear Cart
```http
DELETE /cart/clear
```
*Requires authentication*

### Get Cart Count
```http
GET /cart/count
```
*Requires authentication*

### Validate Cart
```http
POST /cart/validate
```
*Requires authentication*

---

## Order Endpoints

### Create Order
```http
POST /orders
```
*Requires authentication*

**Request Body:**
```json
{
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "Managua",
    "state": "Managua",
    "postal_code": "12345",
    "country": "NI",
    "phone": "+505 8888-8888"
  },
  "billing_address": { ... },
  "payment_method": "card",
  "customer_notes": "Please deliver after 5 PM"
}
```

### Get Orders
```http
GET /orders
```
*Requires authentication*

**Query Parameters:**
- `status` - Filter by status
- `payment_status` - Filter by payment status
- `order_number` - Search by order number
- `start_date` - Filter from date
- `end_date` - Filter to date
- `page` - Page number
- `per_page` - Items per page

### Get Order
```http
GET /orders/{id}
```
*Requires authentication*

### Cancel Order
```http
POST /orders/{id}/cancel
```
*Requires authentication*

---

## Payment Endpoints

### Create PayPal Payment
```http
POST /payments/create
```
*Requires authentication*

**Request Body:**
```json
{
  "amount": 99.99,
  "currency": "USD",
  "return_url": "https://yoursite.com/success",
  "cancel_url": "https://yoursite.com/cancel",
  "description": "Payment for order",
  "items": []
}
```

### Execute PayPal Payment
```http
POST /payments/execute
```
*Requires authentication*

**Request Body:**
```json
{
  "payment_id": "PAYID-XXXXXXX",
  "payer_id": "XXXXXXX"
}
```

### Create Direct Credit Card Payment
```http
POST /payments/direct
```
*Requires authentication*

**Request Body:**
```json
{
  "amount": 99.99,
  "currency": "USD",
  "credit_card": {
    "type": "visa",
    "number": "4032035728516179",
    "expire_month": 12,
    "expire_year": 2025,
    "cvv2": "123",
    "first_name": "John",
    "last_name": "Doe"
  },
  "description": "Direct payment"
}
```

### Get Payment Details
```http
GET /payments/details/{payment_id}
```
*Requires authentication*

---

## Admin Endpoints

### Get All Orders (Admin)
```http
GET /orders/admin/all
```
*Requires admin authentication*

### Update Order Status (Admin)
```http
PUT /orders/admin/{id}/status
```
*Requires admin authentication*

**Request Body:**
```json
{
  "status": "shipped",
  "admin_notes": "Order shipped via DHL"
}
```

### Get Order Statistics (Admin)
```http
GET /orders/stats
```
*Requires admin authentication*

### Refund Payment (Admin)
```http
POST /payments/refund
```
*Requires admin authentication*

**Request Body:**
```json
{
  "sale_id": "SALE-XXXXXXX",
  "amount": 50.00,
  "currency": "USD"
}
```

---

## Webhook Endpoints

### PayPal Webhook
```http
POST /payments/webhook
```
*Public endpoint for PayPal notifications*

---

## Status Codes

### Order Status
- `pending` - Order created, awaiting payment
- `confirmed` - Payment confirmed
- `processing` - Order being prepared
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled
- `refunded` - Order refunded

### Payment Status
- `pending` - Payment pending
- `paid` - Payment successful
- `failed` - Payment failed
- `refunded` - Payment refunded
- `partially_refunded` - Payment partially refunded
