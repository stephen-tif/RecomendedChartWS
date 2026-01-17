"""
Módulo controlador de gráficos
Maneja endpoints de recuperación de datos de gráficos
Siguiendo los principios de diseño RESTful API
"""
import logging
import io
from flask import Blueprint, request, jsonify
from app.services.chart_service import ChartService

logger = logging.getLogger(__name__)

chart_bp = Blueprint('chart', __name__, url_prefix='/api/chart')
chart_service = ChartService()


@chart_bp.route('/data', methods=['POST'],strict_slashes=False)
def get_chart_data():
    """
    Obtener datos agregados y formateados para un gráfico específico
    
    Soporta dos modos de solicitud:
    
    1. CON ARCHIVO (multipart):
        - Enviar el archivo en el campo 'file'
        - Parámetros en campos de formulario: chart_type, parameters (JSON), aggregation (opcional)
        
    2. CON FILEPATH (JSON):
        - Parámetros en JSON: filepath, chart_type, parameters, aggregation (opcional)
    
    Retorna:
        Respuesta JSON con datos del gráfico formateados
        
    Códigos de estado:
        - 200: Éxito
        - 400: Solicitud inválida
        - 404: Archivo no encontrado
        - 500: Error del servidor
    """
    try:
        # Verificar si es una solicitud multipart (con archivo)
        if 'file' in request.files:
            logger.info("Modo: solicitud con archivo multipart")
            file = request.files['file']
            
            if not file or file.filename == '':
                return jsonify({
                    'error': 'Archivo requerido',
                    'message': 'Por favor proporciona un archivo en el campo "file"'
                }), 400
            
            # Obtener parámetros desde formulario
            chart_type = request.form.get('chart_type')
            parameters_json = request.form.get('parameters')
            aggregation = request.form.get('aggregation', 'sum')
            
            if not chart_type:
                return jsonify({
                    'error': 'Campo requerido faltante',
                    'message': 'chart_type es requerido'
                }), 400
            
            if not parameters_json:
                return jsonify({
                    'error': 'Campo requerido faltante',
                    'message': 'parameters es requerido (como JSON string)'
                }), 400
            
            # Parsear parámetros JSON
            import json
            try:
                parameters = json.loads(parameters_json)
            except json.JSONDecodeError as e:
                return jsonify({
                    'error': 'JSON inválido',
                    'message': f'parameters debe ser un JSON válido: {str(e)}'
                }), 400
            
            # Procesar archivo como BytesIO
            file.seek(0)
            file_bytes = io.BytesIO(file.read())
            filename = file.filename
            
            logger.info(f"Procesando archivo: {filename}")
            
            # Validar parámetros
            if not isinstance(parameters, dict):
                return jsonify({
                    'error': 'Parámetros inválidos',
                    'message': 'parameters debe ser un objeto JSON'
                }), 400
            
            if 'x_axis' not in parameters:
                return jsonify({
                    'error': 'Parámetro faltante',
                    'message': 'parameters debe incluir x_axis'
                }), 400
            
            # Validar chart_type
            valid_types = ['bar', 'line', 'pie', 'scatter']
            if chart_type not in valid_types:
                return jsonify({
                    'error': 'chart_type inválido',
                    'message': f'chart_type debe ser uno de: {", ".join(valid_types)}'
                }), 400
            
            # Obtener datos del gráfico desde archivo
            try:
                chart_data = chart_service.get_chart_data_bytes(
                    file_bytes=file_bytes,
                    filename=filename,
                    chart_type=chart_type,
                    parameters=parameters,
                    aggregation=aggregation
                )
            except Exception as e:
                logger.error(f"Error generando datos del gráfico: {str(e)}", exc_info=True)
                return jsonify({
                    'error': 'Error interno del servidor',
                    'message': 'Ocurrió un error al generar los datos del gráfico.'
                }), 500
        
        else:
            # Modo JSON con filepath
            logger.info("Modo: solicitud JSON con filepath")
            data = request.get_json()
            
            # Validar datos de la solicitud
            if not data:
                logger.warning("Solicitud de datos de gráfico recibida sin datos")
                return jsonify({
                    'error': 'No se proporcionaron datos',
                    'message': 'Por favor proporciona un cuerpo de solicitud o archivo multipart'
                }), 400
            
            # Extraer campos requeridos
            filepath = data.get('filepath')
            chart_type = data.get('chart_type')
            parameters = data.get('parameters')
            aggregation = data.get('aggregation', 'sum')
            
            # Validar campos requeridos
            if not filepath:
                return jsonify({
                    'error': 'Campo requerido faltante',
                    'message': 'filepath es requerido'
                }), 400
            
            if not chart_type:
                return jsonify({
                    'error': 'Campo requerido faltante',
                    'message': 'chart_type es requerido'
                }), 400
            
            if not parameters:
                return jsonify({
                    'error': 'Campo requerido faltante',
                    'message': 'objeto parameters es requerido'
                }), 400
            
            # Validar chart_type
            valid_types = ['bar', 'line', 'pie', 'scatter']
            if chart_type not in valid_types:
                return jsonify({
                    'error': 'chart_type inválido',
                    'message': f'chart_type debe ser uno de: {", ".join(valid_types)}'
                }), 400
            
            # Validar parámetros
            if not isinstance(parameters, dict):
                return jsonify({
                    'error': 'Parámetros inválidos',
                    'message': 'parameters debe ser un objeto'
                }), 400
            
            if 'x_axis' not in parameters:
                return jsonify({
                    'error': 'Parámetro faltante',
                    'message': 'parameters debe incluir x_axis'
                }), 400
            
            # Obtener datos del gráfico desde filepath
            try:
                chart_data = chart_service.get_chart_data(
                    filepath=filepath,
                    chart_type=chart_type,
                    parameters=parameters,
                    aggregation=aggregation
                )
            except FileNotFoundError:
                logger.error(f"Archivo no encontrado: {filepath}")
                return jsonify({
                    'error': 'Archivo no disponible',
                    'message': 'El archivo especificado no fue encontrado.'
                }), 404
            except Exception as e:
                logger.error(f"Error generando datos del gráfico: {str(e)}", exc_info=True)
                return jsonify({
                    'error': 'Error interno del servidor',
                    'message': 'Ocurrió un error al generar los datos del gráfico.'
                }), 500
        
        # Si llegamos aquí, tenemos chart_data válido
        logger.info(f"Datos de gráfico {chart_type} generados exitosamente")
        
        logger.info(f"Datos de gráfico {chart_type} generados exitosamente")
        
        return jsonify(chart_data), 200
        
    except ValueError as e:
        logger.warning(f"Error de validación en endpoint de datos de gráfico: {str(e)}")
        return jsonify({
            'error': 'Error de validación',
            'message': str(e)
        }), 400
        
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {str(e)}")
        return jsonify({
            'error': 'Archivo no encontrado',
            'message': str(e)
        }), 404
        
    except KeyError as e:
        logger.warning(f"Error columna faltante: {str(e)}")
        return jsonify({
            'error': 'Columna inválida',
            'message': f'Columna no encontrada en el conjunto de datos: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"Error inesperado en endpoint de datos de gráfico: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error al generar los datos del gráfico. Por favor intenta nuevamente.'
        }), 500
