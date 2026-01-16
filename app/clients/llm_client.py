"""
Módulo de cliente LLM
Gestiona la interacción con APIs de Modelos de Lenguaje Grandes (LLM)
Siguiendo el patrón Strategy para extensibilidad
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Excepción personalizada para errores del cliente LLM"""
    pass


class LLMClient(ABC):
    """Clase base abstracta para clientes LLM"""

    @abstractmethod
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """Analiza datos usando un LLM"""
        pass

    @abstractmethod
    def recommend(self, prompt: str) -> List[Dict[str, Any]]:
        """Obtiene recomendaciones usando un LLM"""
        pass


class OpenAILLMClient(LLMClient):
    """Implementación del cliente OpenAI"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa el cliente LLM de OpenAI

        Args:
            api_key (str): API Key de OpenAI. Si no se proporciona, se lee desde LLM_API_KEY
            base_url (str): URL base de la API. Si no se proporciona, se usa el endpoint oficial
        """
        
        self.api_key = api_key or os.getenv('LLM_API_KEY', '')
        self.base_url = base_url or os.getenv('LLM_API_URL', 'https://api.openai.com/v1')
        self.model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        self.timeout = int(os.getenv('LLM_TIMEOUT', '30'))

        if not self.api_key or self.api_key == '':
            logger.warning("⚠️ LLM_API_KEY no configurada. Se utilizarán mocks.")
        else:
            logger.info(f"✅ Cliente OpenAI inicializado correctamente - Modelo: {self.model}")

    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Analiza datos usando el LLM

        Args:
            prompt (str): Prompt de análisis

        Returns:
            dict: Resultado del análisis
        """
        try:
            response = self._make_api_call(prompt)
            return {
                "analysis": response.get("content", ""),
                "insights": self._extract_insights(response.get("content", ""))
            }
        except Exception as e:
            logger.error(f"Error en análisis LLM: {str(e)}")
            raise LLMClientError(str(e))

    def recommend(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones de gráficos usando el LLM

        Args:
            prompt (str): Prompt de recomendaciones

        Returns:
            list: Lista de recomendaciones estructuradas
        """
        try:
            response = self._make_api_call(prompt)
            recommendations = self._parse_recommendations(response.get("content", ""))
            self._validate_recommendations(recommendations)
            return recommendations
        except Exception as e:
            logger.error(f"Error en recomendaciones LLM: {str(e)}")
            raise LLMClientError(str(e))

    def _make_api_call(self, prompt: str) -> Dict[str, Any]:
        """Realiza la llamada a la API de OpenAI"""
        if not self.api_key or self.api_key == '':
            raise LLMClientError("🚫 API Key no configurada. No se puede hacer llamadas a OpenAI.")

        logger.info(f"🌐 Realizando llamada a OpenAI API ({self.model})...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un analista de datos experto. "
                        "Cuando se solicite, responde únicamente con JSON válido."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            usage = result.get('usage', {})

            logger.info(f"✅ Llamada a OpenAI exitosa. Tokens usados: {usage.get('total_tokens', 'N/A')}")

            return {"content": content}

        except requests.RequestException as e:
            logger.error(f"🌐 Error en llamada HTTP a OpenAI: {str(e)}")
            raise LLMClientError(f"Error en llamada HTTP: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"❌ Formato de respuesta inválido de OpenAI: {str(e)}")
            raise LLMClientError(f"Formato de respuesta inválido: {str(e)}")

    def _parse_recommendations(self, content: str) -> List[Dict[str, Any]]:
        """Extrae recomendaciones desde la respuesta del LLM"""
        content = content.strip()

        # Si tiene markdown code blocks, extraer el contenido
        if content.startswith("```"):
            logger.debug("Detectado bloque de código markdown, extrayendo contenido JSON...")
            content = content.split("```")[1]

        try:
            parsed = json.loads(content)
            logger.debug(f"JSON parseado exitosamente. Tipo: {type(parsed)}")
            
            if isinstance(parsed, list):
                logger.debug(f"Lista de {len(parsed)} recomendaciones detectada")
                return parsed
            if isinstance(parsed, dict) and "recommendations" in parsed:
                logger.debug(f"Objeto con campo 'recommendations' detectado")
                return parsed["recommendations"]
            
            logger.debug("Devolviendo como recomendación única")
            return [parsed]
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error al parsear JSON de OpenAI: {str(e)}")
            logger.error(f"Contenido recibido: {content[:200]}...")
            raise LLMClientError("El LLM no devolvió JSON válido")

    def _validate_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """Valida la estructura de las recomendaciones"""
        required = {"title", "chart_type", "parameters", "insight"}
        for rec in recommendations:
            if not required.issubset(rec):
                raise LLMClientError("Estructura de recomendación inválida")

    def _extract_insights(self, content: str) -> List[str]:
        """Extrae insights desde el texto del análisis"""
        lines = content.splitlines()
        insights = [
            line.lstrip("-• ").strip()
            for line in lines
            if line.strip().startswith(("-", "•"))
        ]
        return insights or [content[:200]]
