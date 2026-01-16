"""
Módulo de validadores
Contiene funciones de validación para varios tipos de datos
"""
import os


def validate_file(file):
    """
    Validar archivo cargado
    
    Args:
        file: Objeto de archivo cargado de Flask
        
    Raises:
        ValueError: Si el archivo es inválido
    """
    if not file:
        raise ValueError('El archivo es requerido')
    
    if not file.filename:
        raise ValueError('El archivo debe tener un nombre de archivo')
    
    # Verificar tamaño del archivo (ej: máximo 10MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reiniciar puntero del archivo
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise ValueError(f'El tamaño del archivo excede el máximo permitido de {max_size} bytes')
    
    if file_size == 0:
        raise ValueError('El archivo está vacío')


def validate_chart_data(data):
    """
    Validar estructura de datos del gráfico
    
    Args:
        data (dict): Datos del gráfico a validar
        
    Raises:
        ValueError: Si los datos son inválidos
    """
    if not isinstance(data, dict):
        raise ValueError('Los datos del gráfico deben ser un diccionario')
    
    required_fields = ['chart_type']
    for field in required_fields:
        if field not in data:
            raise ValueError(f'Campo requerido faltante: {field}')
