"""
Módulo del modelo de sugerencia de gráficos
Modelos de datos para sugerencias de gráficos
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChartSuggestion:
    """Modelo para sugerencia de gráfico"""
    chart_type: str
    reason: str
    confidence: float
    config: Optional[dict] = None
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'chart_type': self.chart_type,
            'reason': self.reason,
            'confidence': self.confidence,
            'config': self.config
        }


@dataclass
class DataAnalysisResult:
    """Modelo para resultado de análisis de datos"""
    columns: List[str]
    data_types: dict
    shape: tuple
    insights: List[str]
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'columns': self.columns,
            'data_types': self.data_types,
            'shape': self.shape,
            'insights': self.insights
        }
