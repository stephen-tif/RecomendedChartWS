"""
Módulo de servicio de análisis con IA
Gestiona el análisis de datos impulsado por IA y recomendaciones de gráficos
Siguiendo el Principio de Responsabilidad Única y el patrón de Inyección de Dependencias
"""
import json
import logging
import os
from typing import Dict, List, Any
from app.clients.llm_client import LLMClient, OpenAILLMClient, LLMClientError
from app.services.mock_recommendation_service import MockRecommendationService

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    Servicio para análisis de datos impulsado por IA con ingeniería de prompts avanzada
    """
    
    def __init__(self, llm_client: LLMClient = None):
        """
        Inicializa el servicio de análisis con IA
        
        Args:
            llm_client (LLMClient): Instancia del cliente LLM.
                                     Si es None, se crea automáticamente OpenAILLMClient
        """
        self.llm_client = llm_client or OpenAILLMClient()
        self.mock_service = MockRecommendationService()
        
        # Determinar si usar mock basado en variables de entorno
        use_mock_env = os.getenv('USE_MOCK_RECOMMENDATIONS', 'false').lower() == 'true'
        has_api_key = bool(os.getenv('LLM_API_KEY'))
        
        self.use_mock = use_mock_env or not has_api_key
        
        # Logging claro sobre qué se está usando
        if self.use_mock:
            if use_mock_env:
                logger.info("🔄 USANDO RECOMENDACIONES SIMULADAS: USE_MOCK_RECOMMENDATIONS=true")
            else:
                logger.warning("⚠️ USANDO RECOMENDACIONES SIMULADAS: LLM_API_KEY no está configurada")
        else:
            logger.info(f"🚀 USANDO API DE OPENAI - Modelo: {self.llm_client.model}")
    
    def analyze_data_structure(self, df_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza la estructura del conjunto de datos utilizando IA
        
        Args:
            df_summary (dict): Resumen completo del DataFrame generado por DataFrameService
            
        Returns:
            dict: Resultados del análisis con observaciones e insights
        """
        try:
            prompt = self._create_analysis_prompt(df_summary)
            response = self.llm_client.analyze(prompt)
            logger.info("Análisis de estructura de datos con IA completado exitosamente")
            return response
        except LLMClientError as e:
            logger.error(f"Error del cliente LLM durante el análisis: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado durante el análisis: {str(e)}")
            raise
    
    def recommend_chart_types(self, df_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recomienda tipos de gráficos en función de la estructura del conjunto de datos
        
        Actúa como un analista de datos experto para identificar patrones
        y sugerir visualizaciones adecuadas.
        
        Utiliza recomendaciones simuladas si la API del LLM no está configurada
        o si ocurre algún error.
        
        Args:
            df_summary (dict): Resumen completo del DataFrame, incluyendo describe() e info()
            
        Returns:
            list: Lista de visualizaciones recomendadas con la siguiente estructura:
                - title: Título descriptivo del gráfico
                - chart_type: Tipo de gráfico (bar, line, pie, scatter)
                - parameters: Diccionario con ejes y configuraciones
                - insight: Breve explicación del valor del gráfico
        """
        if self.use_mock:
            logger.info("📊 Generando recomendaciones simuladas (sin IA)")
            return self.mock_service.generate_recommendations(df_summary)
        
        try:
            logger.info(f"🤖 Enviando datos a OpenAI para análisis ({self.llm_client.model})...")
            prompt = self._create_recommendation_prompt(df_summary)
            response = self.llm_client.recommend(prompt)
            logger.info(f"✅ Se generaron exitosamente {len(response)} recomendaciones mediante IA OpenAI")
            return response
        except LLMClientError as e:
            logger.warning(
                f"❌ Error en la API del LLM, usando recomendaciones simuladas: {str(e)}"
            )
            return self.mock_service.generate_recommendations(df_summary)
        except Exception as e:
            logger.error(
                f"❌ Error inesperado en recomendaciones, usando simulación: {str(e)}"
            )
            return self.mock_service.generate_recommendations(df_summary)
    
    def _create_analysis_prompt(self, df_summary: Dict[str, Any]) -> str:
        """
        Crea el prompt completo para el análisis de la estructura de datos
        """
        columns = df_summary.get('columns', [])
        dtypes = df_summary.get('dtypes', {})
        shape = df_summary.get('shape', {})
        null_counts = df_summary.get('null_counts', {})
        describe = df_summary.get('describe', {})
        column_types = df_summary.get('column_types', {})
        
        prompt = f"""Eres un analista de datos experto con amplia experiencia en exploración y visualización de datos.

Por favor, analiza el siguiente conjunto de datos y proporciona información sobre sus características:

ESTRUCTURA DEL CONJUNTO DE DATOS:
- Número de filas: {shape.get('rows', 0)}
- Número de columnas: {shape.get('columns', 0)}
- Nombres de las columnas: {', '.join(columns)}

TIPOS DE COLUMNAS Y TIPOS DE DATOS:
{self._format_column_info(columns, dtypes, column_types)}

CALIDAD DE LOS DATOS:
- Valores faltantes por columna: {json.dumps(null_counts, indent=2)}

RESUMEN ESTADÍSTICO:
{json.dumps(describe, indent=2)}

Por favor, proporciona:
1. Una evaluación general del conjunto de datos
2. Patrones o relaciones clave que identifiques
3. Posibles problemas de calidad de datos (si existen)
4. Características relevantes o destacables de los datos

Responde en un formato claro y estructurado."""
        
        return prompt
    
    def _create_recommendation_prompt(self, df_summary: Dict[str, Any]) -> str:
        """
        Crea el prompt experto para la recomendación de visualizaciones
        """
        columns = df_summary.get('columns', [])
        dtypes = df_summary.get('dtypes', {})
        shape = df_summary.get('shape', {})
        describe = df_summary.get('describe', {})
        column_types = df_summary.get('column_types', {})
        sample_data = df_summary.get('sample_data', [])[:3]
        
        prompt = f"""Eres un analista de datos experto especializado en visualización de datos. Tu tarea es analizar un conjunto de datos y recomendar entre 3 y 5 visualizaciones específicas que resalten los patrones, relaciones o insights más relevantes.

INFORMACIÓN DEL CONJUNTO DE DATOS:
- Dimensiones: {shape.get('rows', 0)} filas × {shape.get('columns', 0)} columnas
- Columnas: {', '.join(columns)}

ANÁLISIS DE COLUMNAS:
{self._format_column_info(columns, dtypes, column_types)}

RESUMEN ESTADÍSTICO:
{json.dumps(describe, indent=2)}

DATOS DE EJEMPLO (primeras 3 filas):
{json.dumps(sample_data, indent=2, default=str)}

TU TAREA:
Actúa como un analista de datos experto e identifica los patrones, tendencias, correlaciones o relaciones más interesantes del conjunto de datos. Luego, recomienda entre 3 y 5 visualizaciones que destaquen claramente estos insights.

Para cada recomendación, proporciona:
1. **title**: Un título descriptivo y claro del gráfico
2. **chart_type**: Uno de los siguientes valores: "bar", "line", "pie", "scatter"
3. **parameters**: Un objeto que especifique las columnas a utilizar, por ejemplo:
   - Para gráficos de barras o líneas: {{"x_axis": "Categoría", "y_axis": "Valor"}}
   - Para gráficos circulares: {{"x_axis": "Categoría", "y_axis": "Valor"}} o {{"x_axis": "Categoría"}} si es conteo
   - Para gráficos de dispersión: {{"x_axis": "Variable1", "y_axis": "Variable2"}}
4. **insight**: Una breve explicación (1–2 oraciones) del patrón o relación que el gráfico revela y por qué es útil

ENFÓCATE EN:
- Identificar relaciones significativas entre variables
- Destacar tendencias, distribuciones o valores atípicos
- Comparar categorías o grupos
- Mostrar correlaciones que no son evidentes a simple vista

IMPORTANTE:
- Devuelve ÚNICAMENTE un arreglo JSON válido
- Cada recomendación debe contener exactamente los campos: title, chart_type, parameters, insight
- Los parámetros deben referenciar nombres reales de columnas del conjunto de datos
- Proporciona entre 3 y 5 recomendaciones, ni más ni menos
- Todo el contenido debe estar escrito en español

Formato de ejemplo:
[
  {{
    "title": "Desempeño de ventas por región",
    "chart_type": "bar",
    "parameters": {{"x_axis": "Región", "y_axis": "Ventas"}},
    "insight": "Este gráfico permite identificar diferencias claras en el rendimiento de ventas entre regiones."
  }}
]

Ahora analiza el conjunto de datos proporcionado y devuelve tus recomendaciones en formato JSON:"""
        
        return prompt
    
    def _format_column_info(self, columns: List[str], dtypes: Dict, column_types: Dict) -> str:
        """
        Formatea la información de las columnas para el prompt
        """
        info_lines = []
        for col in columns:
            dtype = dtypes.get(col, 'desconocido')
            col_type = column_types.get(col, 'desconocido')
            info_lines.append(f"  - {col}: {dtype} ({col_type})")
        return '\n'.join(info_lines)
