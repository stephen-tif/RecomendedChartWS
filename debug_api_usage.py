#!/usr/bin/env python
"""
Script de debugging para verificar si se está usando OpenAI o mocks
Ejecuta este script para ver qué está configurado en tu aplicación
"""

import os
import sys
from pathlib import Path

# Agregar la ruta del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from app.clients.llm_client import OpenAILLMClient
from app.services.ai_analysis_service import AIAnalysisService

print("=" * 80)
print("🔍 DEBUGGING: Verificación de configuración de API")
print("=" * 80)
print()

# 1. Verificar variables de entorno
print("1️⃣  VARIABLES DE ENTORNO:")
print("-" * 80)

llm_api_key = os.getenv('LLM_API_KEY')
use_mock = os.getenv('USE_MOCK_RECOMMENDATIONS', 'false')
llm_model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
llm_api_url = os.getenv('LLM_API_URL', 'https://api.openai.com/v1')

print(f"  LLM_API_KEY configurada: {'✅ SÍ' if llm_api_key else '❌ NO'}")
if llm_api_key:
    # Mostrar solo los primeros y últimos caracteres por seguridad
    key_preview = f"{llm_api_key[:10]}...{llm_api_key[-10:]}"
    print(f"    Preview: {key_preview}")
else:
    print(f"    ⚠️  No hay API key configurada. Se usarán MOCKS")

print(f"  USE_MOCK_RECOMMENDATIONS: {use_mock}")
print(f"  LLM_MODEL: {llm_model}")
print(f"  LLM_API_URL: {llm_api_url}")
print()

# 2. Verificar inicialización del cliente OpenAI
print("2️⃣  INICIALIZACIÓN DEL CLIENTE OPENAI:")
print("-" * 80)

try:
    client = OpenAILLMClient()
    print(f"  ✅ Cliente inicializado correctamente")
    print(f"     - Modelo: {client.model}")
    print(f"     - URL: {client.base_url}")
    print(f"     - API Key presente: {'✅ SÍ' if client.api_key else '❌ NO'}")
    print(f"     - Timeout: {client.timeout}s")
except Exception as e:
    print(f"  ❌ Error al inicializar cliente: {str(e)}")

print()

# 3. Verificar servicio de IA
print("3️⃣  INICIALIZACIÓN DEL SERVICIO DE IA:")
print("-" * 80)

try:
    ai_service = AIAnalysisService()
    
    if ai_service.use_mock:
        print(f"  ⚠️  USANDO SERVICIO SIMULADO (MOCK)")
        print(f"     Razón: ", end="")
        if use_mock == 'true':
            print("USE_MOCK_RECOMMENDATIONS=true")
        else:
            print("LLM_API_KEY no configurada")
    else:
        print(f"  ✅ USANDO API DE OPENAI")
        print(f"     Modelo: {ai_service.llm_client.model}")
        
except Exception as e:
    print(f"  ❌ Error al inicializar servicio: {str(e)}")

print()
print("=" * 80)
print("📋 RECOMENDACIONES:")
print("=" * 80)

if not llm_api_key:
    print("""
  ❌ NO SE DETECTÓ API KEY DE OPENAI

  Para usar OpenAI en lugar de mocks, realiza uno de estos pasos:

  OPCIÓN 1: Variable de entorno (recomendado)
  -------------------------------------------
  En PowerShell:
    $env:LLM_API_KEY = "tu-api-key-aqui"
    python run.py

  En Linux/Mac:
    export LLM_API_KEY="tu-api-key-aqui"
    python run.py

  OPCIÓN 2: Archivo .env
  -----------------------
  Crea un archivo .env en el directorio raíz con:
    LLM_API_KEY=tu-api-key-aqui
    LLM_MODEL=gpt-4o-mini
    LLM_API_URL=https://api.openai.com/v1

  OPCIÓN 3: Dentro del código
  ----------------------------
  Modifica app/clients/llm_client.py línea 51:
    self.api_key = "tu-api-key-aqui"
    
  ⚠️  NO RECOMENDADO - ¡Nunca hagas esto en producción!
    """)
elif use_mock == 'true':
    print("""
  ⚠️  SE ESTÁ USANDO MOCK EXPLÍCITAMENTE

  Para cambiar a OpenAI:
    - Elimina o cambia USE_MOCK_RECOMMENDATIONS=true
    - Asegúrate de que LLM_API_KEY esté configurada
    """)
else:
    print("""
  ✅ CONFIGURACIÓN CORRECTA - Usando OpenAI API
  
  El sistema está correctamente configurado para usar OpenAI.
  """)

print()
print("=" * 80)
