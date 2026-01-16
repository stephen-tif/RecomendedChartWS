"""
Módulo del Servicio de Recomendaciones Simuladas
Genera recomendaciones inteligentes de gráficos basadas en análisis de DataFrame
Se utiliza cuando la API de LLM no está disponible (modo desarrollo/prueba)
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MockRecommendationService:
    """Servicio para generar recomendaciones de gráficos sin LLM"""
    
    def generate_recommendations(self, df_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generar recomendaciones inteligentes de gráficos basadas en la estructura del DataFrame
        
        Args:
            df_summary (dict): Resumen del DataFrame de DataFrameService
            
        Returns:
            list: Visualizaciones de gráficos recomendadas
        """
        columns = df_summary.get('columns', [])
        column_types = df_summary.get('column_types', {})
        describe = df_summary.get('describe', {})
        shape = df_summary.get('shape', {})
        
        recommendations = []
        
        # Analizar columnas
        numeric_cols = [col for col, col_type in column_types.items() if col_type == 'numeric']
        categorical_cols = [col for col, col_type in column_types.items() if col_type == 'categorical']
        datetime_cols = [col for col, col_type in column_types.items() if col_type == 'datetime']
        
        # Recomendación 1: Gráfico de barras para categorías vs numérico
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            recommendations.append({
                'title': f'{num_col} por {cat_col}',
                'chart_type': 'bar',
                'parameters': {
                    'x_axis': cat_col,
                    'y_axis': num_col
                },
                'insight': f'Este gráfico de barras compara {num_col} en diferentes categorías de {cat_col}, mostrando cuáles son el mejor desempeño.'
            })
        
        # Recomendación 2: Gráfico de líneas si hay una columna datetime
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            dt_col = datetime_cols[0]
            num_col = numeric_cols[0]
            recommendations.append({
                'title': f'Tendencia de {num_col} en el tiempo',
                'chart_type': 'line',
                'parameters': {
                    'x_axis': dt_col,
                    'y_axis': num_col
                },
                'insight': f'Este gráfico de líneas muestra cómo cambia {num_col} a lo largo del tiempo, destacando tendencias y patrones en los datos temporales.'
            })
        
        # Recomendación 3: Gráfico circular para distribución categórica
        if len(categorical_cols) > 0:
            cat_col = categorical_cols[0]
            if len(numeric_cols) > 0:
                num_col = numeric_cols[0]
                recommendations.append({
                    'title': f'Distribución de {cat_col}',
                    'chart_type': 'pie',
                    'parameters': {
                        'x_axis': cat_col,
                        'y_axis': num_col
                    },
                    'insight': f'Este gráfico circular muestra la distribución proporcional de {cat_col} basada en {num_col}, facilitando la visualización de proporciones relativas.'
                })
            else:
                recommendations.append({
                    'title': f'Distribución de {cat_col}',
                    'chart_type': 'pie',
                    'parameters': {
                        'x_axis': cat_col
                    },
                    'insight': f'Este gráfico circular muestra la distribución de categorías de {cat_col}, revelando la frecuencia relativa de cada categoría.'
                })
        
        # Recomendación 4: Gráfico de dispersión para dos columnas numéricas
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            recommendations.append({
                'title': f'{y_col} vs {x_col}',
                'chart_type': 'scatter',
                'parameters': {
                    'x_axis': x_col,
                    'y_axis': y_col
                },
                'insight': f'Este gráfico de dispersión revela la relación entre {x_col} e {y_col}, ayudando a identificar correlaciones o patrones entre estas variables numéricas.'
            })
        
        # Recomendación 5: Gráfico de barras adicional si hay múltiples columnas numéricas
        if len(numeric_cols) > 1 and len(categorical_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[-1] if len(numeric_cols) > 1 else numeric_cols[0]
            # Solo agregar si no tenemos exactamente esta combinación
            if not any(
                rec['parameters'].get('x_axis') == cat_col and 
                rec['parameters'].get('y_axis') == num_col
                for rec in recommendations
            ):
                recommendations.append({
                    'title': f'Comparación de {num_col} por {cat_col}',
                    'chart_type': 'bar',
                    'parameters': {
                        'x_axis': cat_col,
                        'y_axis': num_col
                    },
                    'insight': f'Esta visualización compara valores de {num_col} en diferentes grupos de {cat_col}, mostrando variaciones e identificando los principales.'
                })
        
        # Asegurar al menos 3 recomendaciones (límite de 5)
        if len(recommendations) == 0:
            # Fallback: recomendaciones básicas
            if len(columns) >= 2:
                recommendations.extend([
                    {
                        'title': f'{columns[0]} vs {columns[1]}',
                        'chart_type': 'bar',
                        'parameters': {
                            'x_axis': columns[0],
                            'y_axis': columns[1]
                        },
                        'insight': 'Gráfico de barras mostrando la relación entre las primeras dos columnas de tu conjunto de datos.'
                    }
                ])
        
        # Limitar a 5 recomendaciones
        recommendations = recommendations[:5]
        
        logger.info(f"Se generaron {len(recommendations)} recomendaciones simuladas basadas en la estructura de datos")
        
        return recommendations
