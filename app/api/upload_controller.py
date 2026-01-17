"""
Módulo controlador de carga
Maneja la carga de archivos y recomendaciones automáticas de gráficos
Siguiendo los principios de diseño RESTful API
"""
import logging
import io
from flask import Blueprint, request, jsonify, session
from app.services.file_service import FileService
from app.services.chart_service import ChartService

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')
file_service = FileService()
chart_service = ChartService()


@upload_bp.route('/', methods=['POST'],strict_slashes=False)
def upload_file():
    """
    Endpoint de carga de archivo - Carga robusta de archivo con procesamiento automático
    
    Proceso:
    1. Validar y guardar archivo cargado
    2. Cargar en DataFrame
    3. Extraer resumen de datos completo (describe, info, etc.)
    4. Enviar a IA para análisis
    5. Devolver información de archivo + recomendaciones de gráficos
    
    Solicitud:
        - Datos de formulario con campo 'file'
        
    Retorna:
        Respuesta JSON con:
            - status: 'success'
            - file_info: Metadatos del archivo
            - recommendations: Recomendaciones de gráficos generadas por IA (3-5)
            - data_summary: Resumen breve de la estructura de datos
            
    Códigos de estado:
        - 200: Éxito
        - 400: Solicitud inválida (sin archivo, archivo inválido)
        - 500: Error del servidor
    """
    try:
        # Validar presencia del archivo
        if 'file' not in request.files:
            logger.warning("Solicitud de carga recibida sin archivo")
            return jsonify({
                'error': 'No se proporcionó archivo',
                'message': 'Por favor incluye un archivo en el campo "file"'
            }), 400
        
        file = request.files['file']
        
        # Validar que el archivo no esté vacío
        if file.filename == '':
            logger.warning("Solicitud de carga recibida con nombre de archivo vacío")
            return jsonify({
                'error': 'No se seleccionó archivo',
                'message': 'Por favor selecciona un archivo para cargar'
            }), 400
        
        # Validar extensión del archivo antes de procesar
        from app.utils.validators import validate_file
        try:
            validate_file(file)
        except ValueError as e:
            return jsonify({
                'error': 'Error de validación',
                'message': str(e)
            }), 400
        
        filename = file.filename
        
        # Obtener el tamaño del archivo
        file.seek(0, 2)  # Ir al final
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        logger.info(f"Archivo recibido: {filename} ({file_size} bytes)")
        
        # Crear BytesIO para procesamiento en memoria
        file_bytes = io.BytesIO(file.read())
        file_bytes.name = filename
        
        # Obtener recomendaciones de gráficos directamente desde bytes
        # Sin intentar guardar a disco (Vercel tiene filesystem de solo lectura)
        recommendations_result = chart_service.recommend_chart_file(file_bytes, filename)
        
        # Guardar el archivo en sesión para uso posterior
        file_bytes.seek(0)
        session['uploaded_file'] = file_bytes
        session['uploaded_filename'] = filename
        
        # Combinar resultados
        response = {
            'status': 'success',
            'message': 'Archivo cargado y analizado exitosamente',
            'file_info': {
                'filename': filename,
                'size': file_size,
                'filepath': None  # No hay ruta física en Vercel
            },
            'recommendations': recommendations_result['recommendations'],
            'data_summary': recommendations_result['data_summary']
        }
        
        logger.info(f"Carga procesada exitosamente y generadas {len(response['recommendations'])} recomendaciones")
        
        return jsonify(response), 200
        
    except ValueError as e:
        logger.warning(f"Error de validación en carga: {str(e)}")
        return jsonify({
            'error': 'Error de validación',
            'message': str(e)
        }), 400
        
    except FileNotFoundError as e:
        logger.error(f"Error archivo no encontrado: {str(e)}")
        return jsonify({
            'error': 'Error al procesar archivo',
            'message': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error inesperado en endpoint de carga: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error al procesar el archivo. Por favor intenta nuevamente.'
        }), 500
