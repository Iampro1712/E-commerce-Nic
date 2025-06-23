#!/usr/bin/env python3
"""
Simple HTTP server for the frontend
"""
import http.server
import socketserver
import os
import webbrowser
import threading
import time

def serve_frontend():
    """Serve the frontend on port 8080"""
    PORT = 8080
    DIRECTORY = "frontend"
    
    # Change to frontend directory
    os.chdir(DIRECTORY)
    
    # Create server
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("🌐 Sirviendo frontend en:")
        print(f"   📍 http://localhost:{PORT}")
        print(f"   📍 http://127.0.0.1:{PORT}")
        print("\n🚀 Funcionalidades disponibles:")
        print("   ✅ Documentación interactiva de la API")
        print("   ✅ Testing de todos los endpoints")
        print("   ✅ Gestión automática de tokens JWT")
        print("   ✅ Respuestas formateadas con colores")
        print("\n👤 Usuarios de prueba:")
        print("   🔑 Admin: admin@test.com / admin123")
        print("   👤 User: user@test.com / user123")
        print("\n⚠️  Asegúrate de que la API esté corriendo en http://localhost:5000")
        print("\n🛑 Presiona Ctrl+C para detener el servidor")
        
        # Auto-open browser after a short delay
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{PORT}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor detenido")
            print("✅ ¡Gracias por usar la documentación interactiva!")

if __name__ == "__main__":
    serve_frontend()
