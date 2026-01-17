"""
Punto de entrada para Vercel (función serverless)
Exporta la aplicación Flask como WSGI application
"""
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app
from flask_cors import CORS

# Crear la aplicación
app = create_app('production')

# Configurar SECRET_KEY para sesiones
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-for-sessions')

# Configurar CORS
CORS(
    app,
    resources={r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }},
    supports_credentials=True
)

# Vercel requiere que la app esté disponible como 'app'
# No ejecutar con app.run() en serverless
