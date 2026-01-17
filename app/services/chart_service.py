"""
Módulo de servicio de gráficos
Maneja la generación de gráficos, recomendaciones y agregación de datos
Siguiendo el Patrón de Capa de Servicio
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from app.services.dataframe_service import DataFrameService
from app.services.ai_analysis_service import AIAnalysisService

logger = logging.getLogger(__name__)


class ChartService:
    """Servicio para operaciones de gráficos con procesamiento de datos completo"""
    
    def __init__(self, df_service: Optional[DataFrameService] = None, 
                 ai_service: Optional[AIAnalysisService] = None):
        """
        Inicializar el servicio de gráficos con inyección de dependencias
        
        Args:
            df_service (DataFrameService): Instancia opcional de DataFrameService
            ai_service (AIAnalysisService): Instancia opcional de AIAnalysisService
        """
        self.df_service = df_service or DataFrameService()
        self.ai_service = ai_service or AIAnalysisService()
    
    def recommend_chart(self, filepath: str) -> Dict[str, Any]:
        """
        Recomendar tipos de gráficos basados en datos de archivo cargado
        
        Flujo de trabajo completo:
        1. Cargar DataFrame desde archivo
        2. Extraer resumen completo (describe, info, etc.)
        3. Enviar a IA para análisis experto
        4. Devolver recomendaciones estructuradas
        
        Args:
            filepath (str): Ruta al archivo de datos cargado
            
        Returns:
            dict: Recomendaciones de gráficos con estructura:
                - recommendations: Lista de sugerencias de gráficos
                - data_summary: Información de resumen del DataFrame
                
        Raises:
            ValueError: Si la ruta del archivo es inválida
            FileNotFoundError: Si el archivo no existe
        """
        try:
            # Cargar y analizar DataFrame
            df = self.df_service.load_from_file(filepath)
            df_summary = self.df_service.get_dataframe_summary(df)
            
            # Obtener recomendaciones impulsadas por IA
            recommendations = self.ai_service.recommend_chart_types(df_summary)
            
            logger.info(f"Se generaron {len(recommendations)} recomendaciones de gráficos para {filepath}")
            
            return {
                'recommendations': recommendations,
                'data_summary': {
                    'shape': df_summary['shape'],
                    'columns': df_summary['columns'],
                    'column_types': df_summary['column_types']
                }
            }
    
    def recommend_chart_file(self, file_bytes: Any, filename: str) -> Dict[str, Any]:
        """
        Recomendar tipos de gráficos basados en datos desde bytes/BytesIO
        Para sistemas con filesystems de solo lectura (como Vercel)
        
        Flujo de trabajo:
        1. Cargar DataFrame desde bytes
        2. Extraer resumen completo
        3. Enviar a IA para análisis experto
        4. Devolver recomendaciones estructuradas
        
        Args:
            file_bytes: Objeto BytesIO o similar con datos del archivo
            filename (str): Nombre del archivo
            
        Returns:
            dict: Recomendaciones de gráficos con estructura:
                - recommendations: Lista de sugerencias de gráficos
                - data_summary: Información de resumen del DataFrame
        """
        try:
            # Cargar y analizar DataFrame desde bytes
            df = self.df_service.load_from_bytes(file_bytes, filename)
            df_summary = self.df_service.get_dataframe_summary(df)
            
            # Obtener recomendaciones impulsadas por IA
            recommendations = self.ai_service.recommend_chart_types(df_summary)
            
            logger.info(f"Se generaron {len(recommendations)} recomendaciones de gráficos para {filename}")
            
            return {
                'recommendations': recommendations,
                'data_summary': {
                    'shape': df_summary['shape'],
                    'columns': df_summary['columns'],
                    'column_types': df_summary['column_types']
                }
            }
        except Exception as e:
            logger.error(f"Error en recomendación de gráficos: {str(e)}")
            raise
    
    def get_chart_data(
        self, 
        filepath: str, 
        chart_type: str, 
        parameters: Dict[str, str],
        aggregation: str = 'sum'
    ) -> Dict[str, Any]:
        """
        Obtener datos agregados y formateados para un gráfico específico
        
        Este endpoint procesa el DataFrame de acuerdo a los parámetros del gráfico
        y devuelve solo los datos formateados necesarios para la visualización,
        evitando enviar datos sin procesar al frontend.
        
        Args:
            filepath (str): Ruta al archivo de datos
            chart_type (str): Tipo de gráfico (bar, line, pie, scatter)
            parameters (dict): Parámetros del gráfico con x_axis y/o y_axis
            aggregation (str): Función de agregación (sum, mean, count, max, min)
            
        Returns:
            dict: Datos del gráfico formateados listos para visualización:
                - chart_type: Tipo de gráfico
                - data: Datos formateados (labels, values, etc.)
                - metadata: Metadatos adicionales del gráfico
                
        Raises:
            ValueError: Si los parámetros son inválidos
            KeyError: Si las columnas requeridas no existen
        """
        try:
            # Validar entradas
            if not filepath:
                raise ValueError("filepath es requerido")
            if not chart_type:
                raise ValueError("chart_type es requerido")
            if not parameters:
                raise ValueError("parameters son requeridos")
            
            # Validar chart_type
            valid_types = ['bar', 'line', 'pie', 'scatter']
            if chart_type not in valid_types:
                raise ValueError(f"chart_type inválido. Debe ser uno de: {valid_types}")
            
            # Extraer parámetros
            x_axis = parameters.get('x_axis')
            y_axis = parameters.get('y_axis')
            
            if not x_axis:
                raise ValueError("x_axis es requerido en parameters")
            
            # Cargar DataFrame
            df = self.df_service.load_from_file(filepath)
            
            # Obtener datos agregados
            aggregated_data = self.df_service.get_aggregated_data(
                df=df,
                x_axis=x_axis,
                y_axis=y_axis,
                chart_type=chart_type,
                aggregation=aggregation
            )
            
            logger.info(f"Datos de gráfico {chart_type} generados con parámetros {parameters}")
            
            return {
                'chart_type': chart_type,
                'data': aggregated_data,
                'parameters': parameters,
                'aggregation': aggregation
            }
            
        except Exception as e:
            logger.error(f"Error al generar datos del gráfico: {str(e)}")
            raise
    
    def get_chart_data_bytes(
        self,
        file_bytes: Any,
        filename: str,
        chart_type: str,
        parameters: Dict[str, str],
        aggregation: str = 'sum'
    ) -> Dict[str, Any]:
        """
        Obtener datos agregados y formateados desde bytes/BytesIO
        Para sistemas con filesystems de solo lectura
        
        Args:
            file_bytes: Objeto BytesIO o similar con datos del archivo
            filename (str): Nombre del archivo
            chart_type (str): Tipo de gráfico (bar, line, pie, scatter)
            parameters (dict): Parámetros del gráfico con x_axis y/o y_axis
            aggregation (str): Función de agregación
            
        Returns:
            dict: Datos del gráfico formateados
        """
        try:
            # Validar entradas
            if not file_bytes:
                raise ValueError("file_bytes es requerido")
            if not filename:
                raise ValueError("filename es requerido")
            if not chart_type:
                raise ValueError("chart_type es requerido")
            if not parameters:
                raise ValueError("parameters son requeridos")
            
            # Validar chart_type
            valid_types = ['bar', 'line', 'pie', 'scatter']
            if chart_type not in valid_types:
                raise ValueError(f"chart_type inválido. Debe ser uno de: {valid_types}")
            
            # Extraer parámetros
            x_axis = parameters.get('x_axis')
            y_axis = parameters.get('y_axis')
            
            if not x_axis:
                raise ValueError("x_axis es requerido en parameters")
            
            # Cargar DataFrame desde bytes
            df = self.df_service.load_from_bytes(file_bytes, filename)
            
            # Obtener datos agregados
            aggregated_data = self.df_service.get_aggregated_data(
                df=df,
                x_axis=x_axis,
                y_axis=y_axis,
                chart_type=chart_type,
                aggregation=aggregation
            )
            
            logger.info(f"Datos de gráfico {chart_type} generados desde bytes ({filename})")
            
            return {
                'chart_type': chart_type,
                'data': aggregated_data,
                'parameters': parameters,
                'aggregation': aggregation
            }
            
        except Exception as e:
            logger.error(f"Error al generar datos del gráfico desde bytes: {str(e)}")
            raise
