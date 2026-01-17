"""
Módulo de servicio de Dataframe
Maneja operaciones de DataFrame y procesamiento de datos
"""
import pandas as pd
import json
import io
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DataFrameService:
    """Servicio para operaciones de DataFrame siguiendo el Principio de Responsabilidad Única"""
    
    def __init__(self):
        """Inicializar DataFrameService"""
        pass
    
    def load_from_file(self, filepath: str) -> pd.DataFrame:
        """
        Cargar datos desde archivo al DataFrame
        
        Args:
            filepath (str): Ruta al archivo de datos
            
        Returns:
            pd.DataFrame: DataFrame cargado
            
        Raises:
            ValueError: Si el tipo de archivo no es soportado
            FileNotFoundError: Si el archivo no existe
        """
        try:
            file_ext = filepath.rsplit('.', 1)[1].lower()
            
            if file_ext == 'csv':
                df = pd.read_csv(filepath)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(filepath)
            elif file_ext == 'json':
                df = pd.read_json(filepath)
            else:
                raise ValueError(f'Tipo de archivo no soportado: {file_ext}')
            
            logger.info(f"DataFrame cargado exitosamente desde {filepath}. Forma: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error al cargar archivo {filepath}: {str(e)}")
            raise
    
    def load_from_bytes(self, file_bytes: Any, filename: str) -> pd.DataFrame:
        """
        Cargar datos desde bytes/BytesIO al DataFrame
        Útil para sistemas con filesystems de solo lectura
        
        Args:
            file_bytes: Objeto BytesIO o similar con datos del archivo
            filename (str): Nombre del archivo (para determinar tipo)
            
        Returns:
            pd.DataFrame: DataFrame cargado
            
        Raises:
            ValueError: Si el tipo de archivo no es soportado
        """
        try:
            # Extraer extensión del nombre de archivo
            if '.' not in filename:
                raise ValueError(f'Archivo sin extensión: {filename}')
            
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            # Asegurarse de que estamos al principio del stream
            if hasattr(file_bytes, 'seek'):
                file_bytes.seek(0)
            
            if file_ext == 'csv':
                df = pd.read_csv(file_bytes)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(file_bytes)
            elif file_ext == 'json':
                df = pd.read_json(file_bytes)
            else:
                raise ValueError(f'Tipo de archivo no soportado: {file_ext}')
            
            logger.info(f"DataFrame cargado exitosamente desde bytes ({filename}). Forma: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error al cargar archivo desde bytes ({filename}): {str(e)}")
            raise
    
    def get_dataframe_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Obtener resumen completo del DataFrame incluyendo describe() e info()
        
        Args:
            df (pd.DataFrame): DataFrame a analizar
            
        Returns:
            dict: Información completa del DataFrame incluyendo:
                - columns: Lista de nombres de columnas
                - dtypes: Tipos de datos para cada columna
                - shape: Dimensiones del DataFrame
                - null_counts: Conteo de valores nulos por columna
                - describe: Resumen estadístico (describe())
                - info: Información del DataFrame (uso de memoria, conteos no nulos, etc.)
                - sample_data: Primeras filas
        """
        try:
            # Obtener información básica
            buffer = io.StringIO()
            df.info(buf=buffer)
            info_str = buffer.getvalue()
            
            # Obtener resumen estadístico
            numeric_cols = df.select_dtypes(include=['number']).columns
            describe_dict = {}
            if len(numeric_cols) > 0:
                describe_dict = df[numeric_cols].describe().to_dict()
            
            summary = {
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'shape': {
                    'rows': int(df.shape[0]),
                    'columns': int(df.shape[1])
                },
                'null_counts': df.isnull().sum().to_dict(),
                'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict(),
                'describe': describe_dict,
                'info': info_str,
                'memory_usage': int(df.memory_usage(deep=True).sum()),
                'sample_data': df.head(5).to_dict('records'),
                'column_types': self._classify_columns(df)
            }
            
            logger.debug(f"Resumen de DataFrame generado para {len(df.columns)} columnas")
            return summary
            
        except Exception as e:
            logger.error(f"Error al generar resumen del DataFrame: {str(e)}")
            raise
    
    def _classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Clasificar columnas como numéricas, categóricas, datetime, etc.
        
        Args:
            df (pd.DataFrame): DataFrame a clasificar
            
        Returns:
            dict: Clasificación de columnas
        """
        column_types = {}
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                column_types[col] = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                column_types[col] = 'datetime'
            elif df[col].dtype == 'object':
                # Verificar si es realmente categórica (baja cardinalidad)
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:
                    column_types[col] = 'categorical'
                else:
                    column_types[col] = 'text'
            else:
                column_types[col] = 'other'
        
        return column_types
    
    def get_aggregated_data(
        self, 
        df: pd.DataFrame, 
        x_axis: str, 
        y_axis: str = None,
        chart_type: str = 'bar',
        aggregation: str = 'sum'
    ) -> Dict[str, Any]:
        """
        Obtener datos agregados y formateados para visualización de gráficos
        
        Args:
            df (pd.DataFrame): DataFrame fuente
            x_axis (str): Nombre de columna para eje x
            y_axis (str): Nombre de columna para eje y (opcional para gráficos circulares)
            chart_type (str): Tipo de gráfico (bar, line, pie, scatter)
            aggregation (str): Función de agregación (sum, mean, count, max, min)
            
        Returns:
            dict: Datos formateados listos para visualización de gráficos
            
        Raises:
            ValueError: Si las columnas requeridas están faltando o son inválidas
        """
        try:
            # Validar que las columnas existan
            if x_axis not in df.columns:
                raise ValueError(f"Columna '{x_axis}' no encontrada en el DataFrame")
            
            if y_axis and y_axis not in df.columns:
                raise ValueError(f"Columna '{y_axis}' no encontrada en el DataFrame")
            
            # Manejar diferentes tipos de gráficos
            if chart_type == 'pie':
                return self._prepare_pie_data(df, x_axis, y_axis, aggregation)
            elif chart_type in ['bar', 'line']:
                return self._prepare_bar_line_data(df, x_axis, y_axis, aggregation)
            elif chart_type == 'scatter':
                return self._prepare_scatter_data(df, x_axis, y_axis)
            else:
                raise ValueError(f"Tipo de gráfico no soportado: {chart_type}")
                
        except Exception as e:
            logger.error(f"Error al agregar datos: {str(e)}")
            raise
    
    def _prepare_pie_data(
        self, 
        df: pd.DataFrame, 
        category_col: str, 
        value_col: str = None,
        aggregation: str = 'count'
    ) -> Dict[str, Any]:
        """Preparar datos para gráfico circular"""
        if value_col:
            # Agregar por categoría
            agg_func = {'sum': 'sum', 'mean': 'mean', 'count': 'count'}.get(aggregation, 'sum')
            if aggregation == 'count':
                grouped = df.groupby(category_col).size().reset_index(name='value')
            else:
                grouped = df.groupby(category_col)[value_col].agg(agg_func).reset_index(name='value')
        else:
            # Contar ocurrencias
            grouped = df[category_col].value_counts().reset_index()
            grouped.columns = [category_col, 'value']
        
        return {
            'labels': grouped[category_col].tolist(),
            'values': grouped['value'].tolist(),
            'data': grouped.to_dict('records')
        }
    
    def _prepare_bar_line_data(
        self, 
        df: pd.DataFrame, 
        x_axis: str, 
        y_axis: str,
        aggregation: str = 'sum'
    ) -> Dict[str, Any]:
        """Preparar datos para gráfico de barras o líneas"""
        agg_func = {'sum': 'sum', 'mean': 'mean', 'count': 'count', 
                   'max': 'max', 'min': 'min'}.get(aggregation, 'sum')
        
        if aggregation == 'count':
            grouped = df.groupby(x_axis).size().reset_index(name=y_axis)
        else:
            grouped = df.groupby(x_axis)[y_axis].agg(agg_func).reset_index()
        
        # Ordenar por x_axis para mejor visualización
        grouped = grouped.sort_values(x_axis)
        
        return {
            'labels': grouped[x_axis].astype(str).tolist(),
            'values': grouped[y_axis].tolist(),
            'data': grouped.to_dict('records')
        }
    
    def _prepare_scatter_data(
        self, 
        df: pd.DataFrame, 
        x_axis: str, 
        y_axis: str
    ) -> Dict[str, Any]:
        """Preparar datos para gráfico de dispersión"""
        # Eliminar valores nulos para scatter
        clean_df = df[[x_axis, y_axis]].dropna()
        
        return {
            'data': [
                {'x': float(row[x_axis]), 'y': float(row[y_axis])}
                for _, row in clean_df.iterrows()
            ],
            'x_values': clean_df[x_axis].tolist(),
            'y_values': clean_df[y_axis].tolist()
        }
