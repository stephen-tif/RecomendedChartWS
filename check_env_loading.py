#!/usr/bin/env python
"""
Script de diagnóstico avanzado para verificar la carga de variables de entorno
Ejecuta este script para ver exactamente cómo se están cargando las variables
"""

import os
import sys
from pathlib import Path

print("=" * 90)
print("🔍 DIAGNÓSTICO AVANZADO: Carga de variables de entorno")
print("=" * 90)
print()

# 1. Mostrar información del sistema
print("1️⃣  INFORMACIÓN DEL SISTEMA:")
print("-" * 90)
print(f"  Python: {sys.version}")
print(f"  Directorio actual: {os.getcwd()}")
print(f"  Carpeta del script: {Path(__file__).parent.absolute()}")
print()

# 2. Verificar si existe .env
env_file = Path(__file__).parent / '.env'
print("2️⃣  ARCHIVO .env:")
print("-" * 90)
if env_file.exists():
    print(f"  ✅ Archivo encontrado: {env_file}")
    print(f"  Tamaño: {env_file.stat().st_size} bytes")
    print(f"\n  Contenido (primeras líneas):")
    try:
        with open(env_file, encoding='utf-8') as f:
            lines = f.readlines()[:10]
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    # Ocultar valores sensibles
                    if 'API_KEY' in line or 'SECRET' in line:
                        key, val = line.split('=', 1)
                        val_preview = val.strip()
                        if len(val_preview) > 20:
                            val_preview = f"{val_preview[:10]}...{val_preview[-10:]}"
                        print(f"    {key}={val_preview}")
                    else:
                        print(f"    {line.rstrip()}")
    except UnicodeDecodeError:
        print(f"  ⚠️  No se puede leer el archivo (problema de encoding)")
else:
    print(f"  ❌ Archivo NO encontrado: {env_file}")
    print(f"     Crea uno basado en .env.example")
print()

# 3. Intentar cargar dotenv
print("3️⃣  CARGA DE DOTENV:")
print("-" * 90)
try:
    from dotenv import load_dotenv
    print("  ✅ python-dotenv está instalado")
    
    # Cargar desde el archivo .env
    result = load_dotenv(env_file)
    if result:
        print(f"  ✅ Variables cargadas desde {env_file}")
    else:
        print(f"  ⚠️  No se pudieron cargar variables (¿archivo vacío o no existe?)")
except ImportError:
    print("  ❌ python-dotenv NO está instalado")
    print("     Instálalo con: pip install python-dotenv")

print()

# 4. Verificar variables de entorno después de cargar .env
print("4️⃣  VARIABLES DE ENTORNO (después de cargar .env):")
print("-" * 90)

variables_to_check = [
    'LLM_API_KEY',
    'LLM_MODEL',
    'LLM_API_URL',
    'LLM_TIMEOUT',
    'USE_MOCK_RECOMMENDATIONS',
    'UPLOAD_FOLDER'
]

for var in variables_to_check:
    value = os.getenv(var)
    status = "✅" if value else "❌"
    
    if var == 'LLM_API_KEY' and value:
        # Mostrar solo preview de la clave
        display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else value
    else:
        display_value = value if value else "(no configurada)"
    
    print(f"  {status} {var:30} = {display_value}")

print()

# 5. Resumen y recomendaciones
print("5️⃣  RESUMEN Y RECOMENDACIONES:")
print("-" * 90)

api_key = os.getenv('LLM_API_KEY')

if not api_key:
    print("""
  ⚠️  LA API KEY NO ESTÁ CONFIGURADA
  
  PASOS A SEGUIR:
  
  1️⃣  Abre el archivo .env en este directorio
  2️⃣  Reemplaza la línea:
      LLM_API_KEY=
      
      Con tu clave real:
      LLM_API_KEY=sk-proj-tu-clave-aqui
      
  3️⃣  Guarda el archivo
  4️⃣  Reinicia la aplicación
  
  📌 NOTA: El archivo .env ya está en .gitignore, no será enviado a Git
  
  ¿Dónde obtener la clave?
  - Ve a: https://platform.openai.com/api/keys
  - Inicia sesión con tu cuenta de OpenAI
  - Copia tu clave y pégala en el archivo .env
    """)
else:
    print("""
  ✅ LA API KEY ESTÁ CONFIGURADA CORRECTAMENTE
  
  La aplicación usará OpenAI en lugar de recomendaciones simuladas.
  
  Si aún ves mensajes de MOCK:
  1. Reinicia la aplicación
  2. Verifica que los logs muestren: "✅ Cliente OpenAI inicializado"
  3. Ejecuta nuevamente: python debug_api_usage.py
    """)

print()
print("=" * 90)
