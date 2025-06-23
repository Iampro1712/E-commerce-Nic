# 🚀 Quick Start Guide

## Inicio Rápido (5 minutos)

### Opción 1: Desarrollo Rápido (Sin MySQL)

```bash
# 1. Instalar dependencias básicas
sudo apt update
sudo apt install -y python3-pip python3-venv

# 2. Crear entorno virtual
python3 -m venv env
source env/bin/activate

# 3. Instalar dependencias mínimas
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors python-dotenv marshmallow

# 4. Ejecutar servidor de desarrollo
python3 run_dev.py
```

**¡Listo!** La API estará disponible en `http://localhost:5000`

### Opción 2: Instalación Completa

```bash
# 1. Ejecutar script de instalación
./setup.sh

# 2. Configurar base de datos MySQL
mysql -u root -p
CREATE DATABASE ecommerce_db;

# 3. Editar configuración
cp .env.example .env
# Editar .env con tus credenciales

# 4. Inicializar base de datos
python init_db.py

# 5. Ejecutar servidor
python app.py
```

## 🧪 Probar la API

### Método 1: Script Automático
```bash
# En otra terminal
python3 examples/api_examples.py
```

### Método 2: Curl Manual
```bash
# Health check
curl http://localhost:5000/api/health

# Registrar usuario
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "first_name": "Test",
    "last_name": "User"
  }'
```

## 📋 Usuarios de Prueba (Desarrollo)

### Administrador
- **Email**: `admin@dev.com`
- **Password**: `admin123`
- **Permisos**: Todos los endpoints de admin

### Usuario Regular
- **Email**: `user@dev.com`
- **Password**: `user123`
- **Permisos**: Endpoints de usuario

## 🔑 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Estado de la API |
| `/api/auth/register` | POST | Registro de usuario |
| `/api/auth/login` | POST | Login de usuario |
| `/api/products` | GET | Listar productos |
| `/api/cart` | GET | Ver carrito |
| `/api/cart/add` | POST | Agregar al carrito |
| `/api/orders` | POST | Crear pedido |

## 🛠️ Configuración de PayPal

Para pagos reales, necesitas configurar PayPal:

1. **Crear cuenta**: [developer.paypal.com](https://developer.paypal.com)
2. **Crear aplicación**: Obtener Client ID y Client Secret
3. **Configurar .env**:
   ```env
   PAYPAL_CLIENT_ID=tu_client_id
   PAYPAL_CLIENT_SECRET=tu_client_secret
   PAYPAL_MODE=sandbox
   PAYPAL_WEBHOOK_ID=tu_webhook_id
   ```

Ver [PAYPAL_SETUP.md](PAYPAL_SETUP.md) para detalles completos.

## 📚 Documentación

- **API Completa**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Configuración PayPal**: [PAYPAL_SETUP.md](PAYPAL_SETUP.md)
- **README Principal**: [README.md](README.md)

## 🧪 Testing

```bash
# Ejecutar tests
python run_tests.py

# Tests específicos
pytest tests/test_auth.py -v
```

## 🐳 Docker (Opcional)

```bash
# Construir y ejecutar
docker-compose up --build

# Solo la aplicación
docker build -t ecommerce-api .
docker run -p 5000:5000 ecommerce-api
```

## ⚡ Comandos Útiles

```bash
# Activar entorno virtual
source env/bin/activate

# Desarrollo rápido (SQLite)
python3 run_dev.py

# Producción (MySQL)
python app.py

# Tests
python run_tests.py

# Inicializar DB con datos de ejemplo
python init_db.py

# Probar API
python3 examples/api_examples.py
```

## 🔧 Troubleshooting

### Error: "No module named pip"
```bash
sudo apt install python3-pip
```

### Error: "MySQL connection failed"
```bash
# Usar modo desarrollo (SQLite)
python3 run_dev.py
```

### Error: "Permission denied"
```bash
chmod +x setup.sh run_dev.py
```

### Puerto 5000 ocupado
```bash
# Cambiar puerto en app.py o run_dev.py
app.run(port=8000)
```

## 📞 Soporte

- **Issues**: Crear issue en GitHub
- **Email**: Contactar al equipo de desarrollo
- **Documentación**: Ver archivos .md en el proyecto

---

**¡Felicidades! 🎉 Tu API de e-commerce está lista para usar.**
