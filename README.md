# E-commerce API

Una API REST completa para tienda online construida con Flask, MySQL, JWT y PayPal API.

## Características

- 🔐 **Autenticación JWT** - Sistema completo de registro, login y gestión de usuarios
- 📦 **Gestión de Productos** - CRUD completo con categorías, imágenes y búsqueda avanzada
- 🛒 **Carrito de Compras** - Funcionalidades completas de carrito con validación de inventario
- 💳 **Procesamiento de Pagos** - Integración completa con PayPal API
- 📋 **Gestión de Pedidos** - Sistema completo de pedidos con seguimiento y estados
- 👤 **Gestión de Usuarios** - Perfiles, direcciones y roles de administrador
- 📊 **Panel de Administración** - Endpoints para administradores con estadísticas

## Tecnologías

- **Backend**: Flask 2.3.3
- **Base de Datos**: MySQL con SQLAlchemy
- **Autenticación**: JWT (Flask-JWT-Extended)
- **Pagos**: PayPal API
- **Validación**: Marshmallow
- **CORS**: Flask-CORS

## Instalación

### Prerrequisitos

- Python 3.8+
- MySQL 5.7+
- Cuenta de PayPal Developer (para pagos)

### Configuración

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd E-commerce-Nic
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:
```env
# Flask Configuration
SECRET_KEY=tu-clave-secreta-aqui
JWT_SECRET_KEY=tu-jwt-clave-secreta-aqui

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_db
DB_USER=tu-usuario-db
DB_PASSWORD=tu-password-db

# PayPal Configuration
PAYPAL_CLIENT_ID=tu-paypal-client-id
PAYPAL_CLIENT_SECRET=tu-paypal-client-secret
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID=tu-webhook-id
```

5. **Crear base de datos**
```bash
mysql -u root -p
CREATE DATABASE ecommerce_db;
```

6. **Inicializar base de datos**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. **Ejecutar la aplicación**
```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
E-commerce-Nic/
├── app/
│   ├── __init__.py          # Factory de aplicación
│   ├── models/              # Modelos de base de datos
│   │   ├── user.py         # Usuario y direcciones
│   │   ├── product.py      # Productos y categorías
│   │   ├── cart.py         # Carrito de compras
│   │   └── order.py        # Pedidos
│   ├── routes/              # Endpoints de la API
│   │   ├── auth.py         # Autenticación
│   │   ├── products.py     # Productos
│   │   ├── cart.py         # Carrito
│   │   ├── orders.py       # Pedidos
│   │   └── payments.py     # Pagos
│   ├── schemas/             # Validación con Marshmallow
│   └── utils/               # Utilidades
├── config.py                # Configuración
├── app.py                   # Punto de entrada
└── requirements.txt         # Dependencias
```

## Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Login de usuario
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/profile` - Obtener perfil
- `PUT /api/auth/profile` - Actualizar perfil
- `POST /api/auth/change-password` - Cambiar contraseña
- `GET /api/auth/addresses` - Obtener direcciones
- `POST /api/auth/addresses` - Agregar dirección
- `PUT /api/auth/addresses/<id>` - Actualizar dirección
- `DELETE /api/auth/addresses/<id>` - Eliminar dirección

### Productos
- `GET /api/products` - Listar productos (con filtros y búsqueda)
- `POST /api/products` - Crear producto (admin)
- `GET /api/products/<id>` - Obtener producto
- `PUT /api/products/<id>` - Actualizar producto (admin)
- `DELETE /api/products/<id>` - Eliminar producto (admin)
- `GET /api/products/categories` - Listar categorías
- `POST /api/products/categories` - Crear categoría (admin)

### Carrito
- `GET /api/cart` - Obtener carrito
- `POST /api/cart/add` - Agregar al carrito
- `PUT /api/cart/update/<item_id>` - Actualizar cantidad
- `DELETE /api/cart/remove/<item_id>` - Eliminar del carrito
- `DELETE /api/cart/clear` - Vaciar carrito
- `GET /api/cart/count` - Obtener cantidad de items
- `POST /api/cart/validate` - Validar carrito

### Pedidos
- `POST /api/orders` - Crear pedido
- `GET /api/orders` - Listar pedidos del usuario
- `GET /api/orders/<id>` - Obtener pedido
- `POST /api/orders/<id>/cancel` - Cancelar pedido
- `GET /api/orders/admin/all` - Listar todos los pedidos (admin)
- `PUT /api/orders/admin/<id>/status` - Actualizar estado (admin)
- `GET /api/orders/stats` - Estadísticas (admin)

### Pagos
- `POST /api/payments/methods` - Obtener métodos de pago
- `POST /api/payments/session` - Crear sesión de pago
- `POST /api/payments/create` - Crear pago
- `POST /api/payments/details` - Manejar detalles de pago
- `POST /api/payments/webhook` - Webhook de Adyen
- `POST /api/payments/capture` - Capturar pago (admin)
- `POST /api/payments/refund` - Reembolsar pago (admin)
- `POST /api/payments/cancel` - Cancelar pago (admin)

## Autenticación

La API utiliza JWT para autenticación. Incluye el token en el header:

```
Authorization: Bearer <tu-jwt-token>
```

## Ejemplos de Uso

### Registro de Usuario
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "MiPassword123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+505 8888-8888"
  }'
```

### Agregar Producto al Carrito
```bash
curl -X POST http://localhost:5000/api/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "product_id": "product-uuid",
    "quantity": 2
  }'
```

### Crear Pedido
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "shipping_address": {
      "first_name": "Juan",
      "last_name": "Pérez",
      "address_line_1": "Calle Principal 123",
      "city": "Managua",
      "state": "Managua",
      "postal_code": "12345",
      "country": "NI"
    },
    "billing_address": { ... },
    "payment_method": "card"
  }'
```

## Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app
```

## Despliegue

### Producción con Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (opcional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Soporte

Para soporte, crear un issue en GitHub o contactar al equipo de desarrollo.
