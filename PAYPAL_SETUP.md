# Configuración de PayPal API

Esta guía te ayudará a configurar PayPal para procesar pagos en tu tienda online.

## 1. Crear Cuenta de PayPal Developer

1. Ve a [PayPal Developer](https://developer.paypal.com)
2. Inicia sesión con tu cuenta de PayPal o crea una nueva
3. Ve a **My Apps & Credentials**

## 2. Crear Aplicación

### Sandbox (Desarrollo)
1. En **Sandbox**, haz clic en **Create App**
2. Nombre de la app: `Mi Tienda E-commerce`
3. Merchant: Selecciona tu cuenta sandbox
4. Features: Selecciona **Accept payments**
5. Haz clic en **Create App**

### Live (Producción)
1. En **Live**, haz clic en **Create App**
2. Sigue los mismos pasos que para Sandbox
3. Necesitarás una cuenta business verificada

## 3. Obtener Credenciales

### Client ID y Client Secret
1. En tu aplicación, encontrarás:
   - **Client ID**: Identificador público de tu aplicación
   - **Client Secret**: Clave secreta (mantener privada)

### Cuentas de Prueba Sandbox
PayPal automáticamente crea cuentas de prueba:
- **Personal Account**: Para simular compradores
- **Business Account**: Para recibir pagos

## 4. Configurar Variables de Entorno

Edita tu archivo `.env`:

```env
# PayPal Configuration
PAYPAL_CLIENT_ID=tu_client_id_aqui
PAYPAL_CLIENT_SECRET=tu_client_secret_aqui
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID=tu_webhook_id_aqui
```

**Importante**: 
- Para desarrollo usa `PAYPAL_MODE=sandbox`
- Para producción usa `PAYPAL_MODE=live`

## 5. Configurar Webhooks

Los webhooks son necesarios para recibir notificaciones de estado de pago.

### Crear Webhook
1. En tu aplicación, ve a **Features** > **Webhooks**
2. Haz clic en **Add Webhook**
3. URL: `https://tu-dominio.com/api/payments/webhook`
4. Selecciona eventos:
   - `PAYMENT.SALE.COMPLETED`
   - `PAYMENT.SALE.DENIED`
   - `PAYMENT.SALE.REFUNDED`
5. Guarda el **Webhook ID**

## 6. Métodos de Pago Disponibles

### PayPal Checkout
- Pago con cuenta PayPal
- Pago como invitado con tarjeta
- PayPal Credit (donde esté disponible)

### Tarjetas de Crédito/Débito Directas
- Visa
- Mastercard
- American Express
- Discover

### Métodos Locales
- Transferencias bancarias
- Pagos en efectivo (según país)

## 7. Tarjetas de Prueba (Sandbox)

### Cuentas de Prueba Automáticas
PayPal crea automáticamente cuentas de prueba en Sandbox:

**Comprador Personal:**
- Email: `sb-buyer@personal.example.com`
- Password: `password123`

**Vendedor Business:**
- Email: `sb-seller@business.example.com`
- Password: `password123`

### Tarjetas de Prueba
```
Visa: 4032035728516179
Mastercard: 5555555555554444
Amex: 378282246310005
```

## 8. Flujo de Pago

### 1. Crear Pago PayPal
```bash
curl -X POST http://localhost:5000/api/payments/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 99.99,
    "currency": "USD",
    "return_url": "https://tu-sitio.com/success",
    "cancel_url": "https://tu-sitio.com/cancel",
    "description": "Compra en Mi Tienda"
  }'
```

### 2. Ejecutar Pago (después de aprobación)
```bash
curl -X POST http://localhost:5000/api/payments/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "PAYID-XXXXXXX",
    "payer_id": "XXXXXXX"
  }'
```

### 3. Pago Directo con Tarjeta
```bash
curl -X POST http://localhost:5000/api/payments/direct \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
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
    }
  }'
```

## 9. Monitoreo y Logs

### PayPal Dashboard
- Ve a [PayPal.com](https://paypal.com) > **Activity**
- Para Sandbox: [Sandbox PayPal](https://sandbox.paypal.com)
- **Reports** para análisis detallados

### Logs de la API
Los logs se guardan automáticamente en la aplicación Flask.

## 10. Seguridad

### Mejores Prácticas
1. **Nunca** expongas el Client Secret en el frontend
2. Usa HTTPS en producción
3. Valida siempre los webhooks
4. Implementa rate limiting
5. Monitorea transacciones sospechosas

### Validación de Webhooks
La API incluye validación automática de webhooks de PayPal.

## 11. Ir a Producción

### Checklist
- [ ] Cuenta PayPal Business verificada
- [ ] Aplicación Live creada
- [ ] Credenciales de producción configuradas
- [ ] Webhooks configurados en Live
- [ ] SSL/TLS configurado
- [ ] Pruebas completas realizadas
- [ ] Monitoreo configurado

### Cambios Necesarios
1. Cambiar `PAYPAL_MODE=live`
2. Usar credenciales de aplicación Live
3. Configurar webhooks de producción
4. Actualizar URLs de return y cancel

## 12. Soporte

### Documentación Oficial
- [PayPal Developer Docs](https://developer.paypal.com/docs/)
- [Python SDK](https://github.com/paypal/PayPal-Python-SDK)

### Contacto
- Soporte: [PayPal Developer Support](https://developer.paypal.com/support/)
- Comunidad: [PayPal Developer Community](https://community.paypal.com/t5/Developer-Community/ct-p/developer-community)

## 13. Troubleshooting

### Errores Comunes

#### "Authentication failed"
- Verifica Client ID y Client Secret
- Asegúrate de usar el mode correcto (sandbox/live)

#### "Invalid payment state"
- Verifica que el pago esté en estado correcto
- Revisa los logs de PayPal

#### "Webhook verification failed"
- Verifica el Webhook ID
- Asegúrate de que el webhook esté configurado correctamente

#### "Payment denied"
- Verifica los datos de la tarjeta
- Revisa las políticas de riesgo en PayPal

### Logs Útiles
```bash
# Ver logs de la aplicación
tail -f app.log

# Ver logs específicos de PayPal
grep "PayPal" app.log
```

## 14. Diferencias con Adyen

### Ventajas de PayPal
- ✅ Configuración más simple
- ✅ Amplia adopción de usuarios
- ✅ Sandbox robusto para testing
- ✅ Documentación clara
- ✅ Soporte en español

### Consideraciones
- 🔄 Flujo de redirección para PayPal Checkout
- 🔄 Tarifas competitivas pero variables
- 🔄 Menos métodos de pago locales que Adyen

## 15. Migración desde Adyen

Si estás migrando desde Adyen:

1. **Reemplazar credenciales** en `.env`
2. **Actualizar webhooks** en PayPal
3. **Probar flujos de pago** en Sandbox
4. **Actualizar frontend** para manejar redirecciones PayPal
5. **Migrar datos de transacciones** si es necesario

---

**¡PayPal está listo para procesar pagos! 💳**
