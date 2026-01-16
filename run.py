"""
Punto de entrada de la aplicación
Ejecuta el servidor de desarrollo de Flask
"""
from app.main import create_app
from flask_cors import CORS

app = create_app()

CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:8080"}}
)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)