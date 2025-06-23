# 🚀 Guía de Despliegue en Fly.io

Esta guía te ayudará a desplegar tu aplicación E-commerce NIC en Fly.io paso a paso.

## 📋 Prerrequisitos

1. **Cuenta en Fly.io**: Regístrate en [fly.io](https://fly.io)
2. **Fly CLI instalado**: [Instalar flyctl](https://fly.io/docs/getting-started/installing-flyctl/)
3. **Docker instalado** (opcional, para pruebas locales)
4. **Cuenta PayPal Developer** para pagos

## 🔧 Preparación Inicial

### 1. Instalar y configurar Fly CLI

```bash
# Instalar flyctl (macOS)
brew install flyctl

# Instalar flyctl (Linux)
curl -L https://fly.io/install.sh | sh

# Instalar flyctl (Windows)
# Descargar desde https://github.com/superfly/flyctl/releases

# Autenticarse
flyctl auth login
```

### 2. Clonar y preparar el proyecto

```bash
git clone <tu-repositorio>
cd E-commerce-Nic
```

## 🗄️ Configuración de Base de Datos

### Crear base de datos PostgreSQL en Fly.io

```bash
# Crear aplicación PostgreSQL
flyctl postgres create --name ecommerce-nic-db --region mia

# Obtener la cadena de conexión
flyctl postgres connect -a ecommerce-nic-db
```

Guarda la información de conexión que aparece:
- Host
- Puerto
- Base de datos
- Usuario
- Contraseña

## 🚀 Despliegue de la Aplicación

### 1. Inicializar aplicación Fly.io

```bash
# Inicializar aplicación (esto creará/actualizará fly.toml)
flyctl launch --no-deploy

# Cuando te pregunte:
# - App name: e-commerce-nic (o el nombre que prefieras)
# - Region: mia (Miami, más cerca de Nicaragua)
# - PostgreSQL: No (ya la creamos)
# - Redis: No
```

### 2. Configurar variables de entorno (secretos)

```bash
# Variables de aplicación
flyctl secrets set SECRET_KEY="tu-clave-secreta-super-segura"
flyctl secrets set JWT_SECRET_KEY="tu-jwt-clave-secreta-super-segura"
flyctl secrets set FLASK_ENV="production"

# Variables de base de datos
flyctl secrets set DB_TYPE="postgresql"
flyctl secrets set DB_HOST="tu-postgres-host.fly.dev"
flyctl secrets set DB_PORT="5432"
flyctl secrets set DB_NAME="tu_base_datos"
flyctl secrets set DB_USER="tu_usuario"
flyctl secrets set DB_PASSWORD="tu_contraseña"

# Variables de PayPal
flyctl secrets set PAYPAL_CLIENT_ID="tu_paypal_client_id"
flyctl secrets set PAYPAL_CLIENT_SECRET="tu_paypal_client_secret"
flyctl secrets set PAYPAL_MODE="sandbox"  # Cambiar a "live" para producción

# Variables de CORS
flyctl secrets set APP_URL="https://tu-app.fly.dev"
flyctl secrets set CORS_ORIGINS="https://tu-frontend.com,https://tu-app.fly.dev"

# Variables de administrador (opcional)
flyctl secrets set ADMIN_EMAIL="admin@tudominio.com"
flyctl secrets set ADMIN_PASSWORD="AdminPassword123"
```

### 3. Crear volumen para uploads

```bash
# Crear volumen persistente para archivos subidos
flyctl volumes create uploads_volume --region mia --size 1
```

### 4. Desplegar aplicación

```bash
# Desplegar
flyctl deploy

# Verificar estado
flyctl status

# Ver logs
flyctl logs
```

## 🔍 Verificación del Despliegue

### Endpoints de verificación

```bash
# Health check
curl https://tu-app.fly.dev/api/health

# Readiness check
curl https://tu-app.fly.dev/api/ready

# Liveness check
curl https://tu-app.fly.dev/api/live
```

### Verificar base de datos

```bash
# Conectar a la aplicación
flyctl ssh console

# Dentro del contenedor, verificar base de datos
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('Tables:', db.engine.table_names())"
```

## 🔧 Configuración Adicional

### Configurar dominio personalizado

```bash
# Agregar dominio personalizado
flyctl certs create tudominio.com
flyctl certs create www.tudominio.com

# Verificar certificados
flyctl certs list
```

### Configurar escalado

```bash
# Configurar número de instancias
flyctl scale count 2

# Configurar recursos
flyctl scale vm shared-cpu-1x --memory 512
```

## 🐛 Solución de Problemas

### Ver logs detallados

```bash
# Logs en tiempo real
flyctl logs -f

# Logs de una instancia específica
flyctl logs -i <instance-id>
```

### Conectar por SSH

```bash
# Conectar por SSH
flyctl ssh console

# Ejecutar comandos dentro del contenedor
flyctl ssh console -C "python init_db.py"
```

### Reiniciar aplicación

```bash
# Reiniciar todas las instancias
flyctl apps restart

# Reiniciar instancia específica
flyctl machine restart <machine-id>
```

### Problemas comunes

1. **Error de conexión a base de datos**:
   - Verificar variables de entorno: `flyctl secrets list`
   - Verificar conectividad: `flyctl ssh console -C "ping tu-postgres-host.fly.dev"`

2. **Error 503 en health check**:
   - Verificar logs: `flyctl logs`
   - Verificar que las tablas existan: `flyctl ssh console -C "python init_db.py"`

3. **Problemas de CORS**:
   - Verificar CORS_ORIGINS incluye tu dominio
   - Actualizar: `flyctl secrets set CORS_ORIGINS="https://tu-dominio.com"`

## 📊 Monitoreo

### Métricas básicas

```bash
# Ver métricas
flyctl metrics

# Ver estado de máquinas
flyctl machine list
```

### Configurar alertas

Fly.io proporciona métricas básicas. Para monitoreo avanzado, considera integrar:
- Sentry para errores
- New Relic para performance
- Datadog para métricas personalizadas

## 🔄 Actualizaciones

### Desplegar cambios

```bash
# Hacer cambios en el código
git add .
git commit -m "Actualización"

# Desplegar cambios
flyctl deploy

# Verificar despliegue
flyctl status
```

### Rollback

```bash
# Ver releases
flyctl releases

# Hacer rollback
flyctl releases rollback <version>
```

## 💰 Costos Estimados

- **Aplicación básica**: ~$5-10/mes
- **Base de datos PostgreSQL**: ~$15-25/mes
- **Volumen de almacenamiento**: ~$0.15/GB/mes
- **Tráfico**: Incluido hasta cierto límite

## 📞 Soporte

- **Documentación Fly.io**: https://fly.io/docs/
- **Comunidad**: https://community.fly.io/
- **Status**: https://status.fly.io/

---

¡Tu aplicación E-commerce NIC está lista para producción en Fly.io! 🎉
