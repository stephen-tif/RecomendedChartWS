"""
Módulo de fábrica de aplicación Flask
Crea y configura la instancia de la aplicación Flask
Siguiendo el Patrón de Fábrica de Aplicación
"""
import os
import logging
from flask import Flask, jsonify
from flask.logging import default_handler

# Cargar variables de entorno desde archivo .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.getLogger(__name__).debug("✅ Archivo .env cargado correctamente")
except ImportError:
    logging.getLogger(__name__).debug("ℹ️  python-dotenv no está instalado, usando variables de entorno del sistema")
except Exception as e:
    logging.getLogger(__name__).warning(f"⚠️ Error al cargar .env: {str(e)}")


def create_app(config_name='development'):
    """
    Función de fábrica de aplicación
    
    Crea y configura la aplicación Flask con:
    - Configuración basada en entorno
    - Configuración de logging
    - Registro de blueprints
    - Manejadores de errores
    
    Args:
        config_name (str): Nombre del ambiente de configuración
        
    Returns:
        Flask: Instancia de aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración desde entorno
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB tamaño máximo de archivo
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Configurar logging
    configure_logging(app, config_name)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Aplicación Flask inicializada con config: {config_name}")
    
    return app


def configure_logging(app: Flask, config_name: str) -> None:
    """
    Configurar el logging de la aplicación
    
    Args:
        app (Flask): Instancia de la aplicación Flask
        config_name (str): Nombre del ambiente de configuración
    """
    # En producción y serverless: usar solo consola (stdout/stderr)
    # Vercel captura automáticamente los logs de consola
    # Evitar escribir a archivos en sistemas de solo lectura
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    
    if app.debug:
        # Logging de desarrollo - nivel DEBUG
        console_handler.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    else:
        # Logging de producción - nivel INFO
        console_handler.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    app.logger.addHandler(console_handler)
    app.logger.info(f'Aplicación iniciada en ambiente: {config_name}')


def register_blueprints(app: Flask) -> None:
    """
    Registrar los blueprints de la aplicación
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    from app.api import upload_controller, chart_controller
    
    app.register_blueprint(upload_controller.upload_bp)
    app.register_blueprint(chart_controller.chart_bp)
    
    # Endpoint de verificación de salud
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint de verificación de salud"""
        return jsonify({'status': 'healthy'}), 200


def register_error_handlers(app: Flask) -> None:
    """
    Registrar los manejadores de errores para errores HTTP comunes
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Manejar error de archivo demasiado grande"""
        return jsonify({
            'error': 'Archivo demasiado grande',
            'message': 'El tamaño del archivo excede el máximo permitido (10MB)'
        }), 413
    
    @app.errorhandler(404)
    def not_found(error):
        """Manejar errores 404"""
        return jsonify({
            'error': 'No encontrado',
            'message': 'El recurso solicitado no fue encontrado'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Manejar errores 500"""
        app.logger.error(f'Error del servidor: {error}', exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado. Por favor intenta más tarde.'
        }), 500
