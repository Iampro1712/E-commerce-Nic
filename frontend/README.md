# 🌐 Frontend - Documentación Interactiva de la API

Un frontend simple y elegante para probar todos los endpoints de la API E-commerce con PayPal.

## 🚀 **Características**

### ✅ **Interfaz Completa**
- 📋 **Documentación visual** de todos los endpoints
- 🧪 **Testing interactivo** con botones de prueba
- 🔑 **Gestión automática de tokens** JWT
- 📊 **Respuestas formateadas** con syntax highlighting
- 📱 **Diseño responsive** con Bootstrap 5

### ✅ **Endpoints Incluidos**
- 🏥 **Health Check** - Verificar estado de la API
- 🔐 **Autenticación** - Registro, login, perfil
- 📦 **Productos** - CRUD completo con filtros
- 📂 **Categorías** - Gestión de categorías
- 🛒 **Carrito** - Operaciones de carrito
- 📋 **Pedidos** - Crear y gestionar pedidos
- 💳 **Pagos PayPal** - Crear, ejecutar, reembolsar
- 👑 **Admin** - Funciones administrativas

## 🔧 **Cómo Usar**

### 1. **Abrir el Frontend**
```bash
# Opción 1: Abrir directamente en navegador
open frontend/index.html

# Opción 2: Servir con servidor HTTP simple
cd frontend
python3 -m http.server 8080
# Luego ir a: http://localhost:8080
```

### 2. **Configurar la API**
1. **Verificar URL base**: Por defecto apunta a `http://localhost:5000/api`
2. **Cambiar URL** si es necesario usando el botón "Cambiar"
3. **Verificar estado**: El indicador muestra si la API está online

### 3. **Autenticarse**
1. **Login rápido**: Usar botones "Login Admin" o "Login Usuario"
2. **Token automático**: Se guarda automáticamente después del login
3. **Token manual**: Pegar token JWT en el campo de autenticación

### 4. **Probar Endpoints**
1. **Seleccionar endpoint** desde la navegación lateral
2. **Modificar datos** en los campos de texto si es necesario
3. **Hacer clic** en el botón de prueba
4. **Ver respuesta** formateada con colores

## 🎯 **Funcionalidades Especiales**

### ✅ **Gestión de Tokens**
- **Auto-guardado**: Los tokens se guardan automáticamente en localStorage
- **Auto-inclusión**: Se incluyen automáticamente en peticiones autenticadas
- **Persistencia**: Los tokens persisten entre sesiones

### ✅ **Usuarios de Prueba**
- **Admin**: `admin@test.com` / `admin123`
- **Usuario**: `user@test.com` / `user123`

### ✅ **Atajos de Teclado**
- **Ctrl + Enter**: Enviar petición desde cualquier textarea

### ✅ **Utilidades**
- **Copiar respuestas**: Botón para copiar JSON al portapapeles
- **Notificaciones**: Feedback visual de acciones
- **Navegación suave**: Scroll automático a secciones

## 📋 **Ejemplos de Uso**

### 1. **Flujo Básico de Testing**
```
1. Abrir frontend/index.html
2. Verificar que API esté online (indicador verde)
3. Hacer clic en "Login Admin" 
4. Probar "Ver Productos"
5. Probar "Crear Producto" (como admin)
6. Probar otros endpoints
```

### 2. **Testing de Carrito y Pedidos**
```
1. Login como usuario normal
2. Ver productos disponibles
3. Copiar ID de un producto
4. Agregar al carrito con ese ID
5. Ver carrito
6. Crear pedido
```

### 3. **Testing de Pagos PayPal**
```
1. Login como usuario
2. Crear pago PayPal
3. Copiar payment_id de la respuesta
4. Usar payment_id para ejecutar pago
5. (Como admin) Probar reembolso
```

## 🎨 **Estructura del Frontend**

```
frontend/
├── index.html          # Página principal
├── script.js           # Lógica JavaScript
└── README.md          # Esta documentación
```

### **Tecnologías Usadas**
- **HTML5** - Estructura semántica
- **Bootstrap 5** - Diseño y componentes
- **JavaScript ES6+** - Funcionalidad interactiva
- **Prism.js** - Syntax highlighting
- **Fetch API** - Peticiones HTTP

## 🔧 **Personalización**

### **Cambiar URL Base**
```javascript
// En script.js, línea 2:
let baseUrl = 'https://tu-api.com/api';
```

### **Agregar Nuevos Endpoints**
1. **Agregar navegación** en el sidebar
2. **Crear sección HTML** con el endpoint
3. **Usar función** `makeRequest()` para la funcionalidad

### **Modificar Estilos**
```css
/* Agregar CSS personalizado en el <style> del HTML */
.custom-style {
    /* Tus estilos aquí */
}
```

## 🧪 **Testing Completo**

### **Checklist de Pruebas**
- [ ] ✅ Health check funciona
- [ ] 🔐 Login admin funciona
- [ ] 🔐 Login usuario funciona
- [ ] 👤 Ver perfil funciona
- [ ] 📦 Listar productos funciona
- [ ] 📦 Crear producto (admin) funciona
- [ ] 📂 Listar categorías funciona
- [ ] 🛒 Ver carrito funciona
- [ ] 🛒 Agregar al carrito funciona
- [ ] 📋 Ver pedidos funciona
- [ ] 💳 Crear pago PayPal funciona

## 🚀 **Despliegue**

### **Hosting Estático**
```bash
# Subir archivos a cualquier hosting estático:
# - GitHub Pages
# - Netlify
# - Vercel
# - Firebase Hosting
```

### **Servidor Local**
```bash
# Python
python3 -m http.server 8080

# Node.js
npx serve .

# PHP
php -S localhost:8080
```

## 🔍 **Troubleshooting**

### **API Offline**
- Verificar que el servidor de la API esté corriendo
- Verificar la URL base en la configuración
- Revisar CORS si hay problemas de origen cruzado

### **Token No Funciona**
- Verificar que el token sea válido
- Verificar que no haya expirado
- Hacer login nuevamente

### **Respuestas Vacías**
- Verificar que el endpoint exista
- Verificar el método HTTP (GET, POST, etc.)
- Revisar la consola del navegador para errores

## 📞 **Soporte**

### **Recursos**
- **API Documentation**: `../API_DOCUMENTATION.md`
- **PayPal Setup**: `../PAYPAL_SETUP.md`
- **Quick Start**: `../QUICK_START.md`

### **Desarrollo**
- **Consola del navegador**: F12 para ver errores
- **Network tab**: Para ver peticiones HTTP
- **Local Storage**: Para ver tokens guardados

---

**🎉 ¡Frontend listo para probar toda la API de forma interactiva!**
