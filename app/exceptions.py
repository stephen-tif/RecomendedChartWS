"""
Módulo de excepciones personalizadas
Define excepciones específicas de la aplicación siguiendo los principios de código limpio
"""


class AppException(Exception):
    """Excepción base para errores específicos de la aplicación"""
    pass


class FileProcessingError(AppException):
    """Excepción lanzada cuando el procesamiento de archivos falla"""
    pass


class DataAnalysisError(AppException):
    """Excepción lanzada cuando el análisis de datos falla"""
    pass


class ChartGenerationError(AppException):
    """Excepción lanzada cuando la generación de gráficos falla"""
    pass
