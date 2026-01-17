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
        
        # Procesar carga (valida, guarda archivo)
        upload_result = file_service.process_upload(file)
        filepath = upload_result['filepath']
        in_memory = upload_result.get('in_memory', False)
        
        logger.info(f"Archivo cargado exitosamente: {upload_result['filename']}")
        
        # Guardar el archivo en sesión para procesamiento en memoria
        file.seek(0)  # Volver al inicio del stream
        
        # Crear un BytesIO desde el archivo para pasar al servicio de gráficos
        file_bytes = io.BytesIO(file.read())
        file_bytes.name = upload_result['filename']
        
        # Obtener recomendaciones de gráficos (incluye procesamiento de DataFrame y análisis de IA)
        # Pasar el archivo en lugar del filepath para soportar filesystems de solo lectura
        recommendations_result = chart_service.recommend_chart_file(file_bytes, upload_result['filename'])
        
        # Combinar resultados
        response = {
            'status': 'success',
            'message': 'Archivo cargado y analizado exitosamente',
            'file_info': {
                'filename': upload_result['filename'],
                'size': upload_result['size'],
                'filepath': upload_result['filepath']
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
