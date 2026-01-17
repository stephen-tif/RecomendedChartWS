"""
Módulo controlador de gráficos
Maneja endpoints de recuperación de datos de gráficos
Siguiendo los principios de diseño RESTful API
"""
import logging
import io
from flask import Blueprint, request, jsonify, session
from app.services.chart_service import ChartService

logger = logging.getLogger(__name__)

chart_bp = Blueprint('chart', __name__, url_prefix='/api/chart')
chart_service = ChartService()


@chart_bp.route('/data', methods=['POST'],strict_slashes=False)
def get_chart_data():
    """
    Obtener datos agregados y formateados para un gráfico específico
    
    Este endpoint recibe parámetros del gráfico y devuelve solo los datos
    procesados y agregados necesarios para la visualización. Esto evita enviar
    todo el conjunto de datos sin procesar al frontend.
    
    Cuerpo de la solicitud (JSON):
        {
            "filepath": "ruta/al/archivo.csv",
            "chart_type": "bar|line|pie|scatter",
            "parameters": {
                "x_axis": "NombreColumna",
                "y_axis": "NombreColumna"  // opcional para gráficos circulares
            },
            "aggregation": "sum|mean|count|max|min"  // opcional, default: "sum"
        }
    
    Retorna:
        Respuesta JSON con:
            - chart_type: Tipo de gráfico
            - data: Datos formateados (estructura varía según tipo de gráfico)
                - Para bar/line: {labels: [], values: [], data: []}
                - Para pie: {labels: [], values: [], data: []}
                - Para scatter: {data: [{x, y}], x_values: [], y_values: []}
            - parameters: Parámetros originales utilizados
            - aggregation: Función de agregación utilizada
            
    Códigos de estado:
        - 200: Éxito
        - 400: Solicitud inválida (parámetros faltantes/inválidos)
        - 404: Archivo no encontrado
        - 500: Error del servidor
    
    Ejemplo de solicitud:
        POST /api/chart/data
        {
            "filepath": "uploads/sales_data.csv",
            "chart_type": "bar",
            "parameters": {
                "x_axis": "Region",
                "y_axis": "Sales"
            },
            "aggregation": "sum"
        }
    """
    try:
        data = request.get_json()
        
        # Validar datos de la solicitud
        if not data:
            logger.warning("Solicitud de datos de gráfico recibida sin cuerpo JSON")
            return jsonify({
                'error': 'No se proporcionaron datos',
                'message': 'Por favor proporciona un cuerpo de solicitud con filepath, chart_type y parameters'
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
        
        # Verificar si hay un archivo en la sesión (del último upload)
        uploaded_file = session.get('uploaded_file')
        uploaded_filename = session.get('uploaded_filename')
        
        # Si hay un archivo en sesión, usarlo directamente (Vercel/memoria)
        if uploaded_file and uploaded_filename:
            try:
                chart_data = chart_service.get_chart_data_bytes(
                    file_bytes=uploaded_file,
                    filename=uploaded_filename,
                    chart_type=chart_type,
                    parameters=parameters,
                    aggregation=aggregation
                )
            except Exception as e:
                logger.error(f"Error usando archivo en memoria de sesión: {str(e)}")
                return jsonify({
                    'error': 'Error interno del servidor',
                    'message': 'Ocurrió un error al generar los datos del gráfico. Por favor intenta nuevamente.'
                }), 500
        else:
            # Intentar usar filepath si está disponible (para compatibilidad con ambientes locales)
            if not filepath:
                return jsonify({
                    'error': 'Error de configuración',
                    'message': 'No hay archivo disponible. Por favor carga un archivo primero.'
                }), 400
            
            try:
                # Intentar cargar desde filepath (puede fallar en Vercel)
                chart_data = chart_service.get_chart_data(
                    filepath=filepath,
                    chart_type=chart_type,
                    parameters=parameters,
                    aggregation=aggregation
                )
            except FileNotFoundError:
                # Si el archivo no existe en disco, informar al usuario
                logger.error(f"Archivo no encontrado: {filepath}")
                return jsonify({
                    'error': 'Archivo no disponible',
                    'message': 'El archivo ha expirado o no está disponible. Por favor carga el archivo nuevamente.'
                }), 404
            except Exception as e:
                logger.error(f"Error generando datos del gráfico: {str(e)}")
                return jsonify({
                    'error': 'Error interno del servidor',
                    'message': 'Ocurrió un error al generar los datos del gráfico. Por favor intenta nuevamente.'
                }), 500
        
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
