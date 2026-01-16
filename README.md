# Recommended Chart API

Una API robusta basada en Flask para recomendaciones inteligentes de gráficos usando análisis de datos potenciado por IA.

## 🎯 Características

- **Carga de Archivos Robusta**: Validación segura de archivos (CSV, Excel, JSON)
- **Procesamiento con Pandas**: Análisis completo de datos (describe, info, estadísticas)
- **Recomendaciones con IA**: Analista de datos experto que identifica patrones y sugiere 3-5 visualizaciones
- **Endpoint de Datos Agregados**: Agregación eficiente y formateo de datos para visualización
- **Arquitectura Limpia**: Siguiendo principios SOLID, clean code y patrones de diseño

---

## 📋 Tabla de Contenidos

- [Configuración y Ejecución Local](#-configuración-y-ejecución-local)
- [Decisiones Técnicas](#-decisiones-técnicas)
- [Ingeniería de Prompts](#-ingeniería-de-prompts-para-la-ia)
- [API Endpoints](#-api-endpoints)
- [Ejemplos de Consumo con cURL](#-ejemplos-de-consumo-con-curl)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Patrones de Diseño](#-patrones-de-diseño)
- [Modo de Funcionamiento](#-modo-de-funcionamiento)

---

## 🚀 Configuración y Ejecución Local

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Paso 1: Clonar o Descargar el Proyecto

```bash
git clone <repository-url>
cd RecomendedChartWS
```

O descarga y descomprime el proyecto.

### Paso 2: Crear Entorno Virtual

Es **muy recomendable** usar un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear entorno virtual
python -m venv venv
```

### Paso 3: Activar el Entorno Virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

Si encuentras un error de política de ejecución, ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

Verás `(venv)` al inicio de tu prompt cuando esté activado.

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias:
- Flask 3.1.2+
- pandas 2.3.3+
- openpyxl 3.1.5+
- requests 2.32.5+
- werkzeug 3.1.5+
- python-dotenv 1.2.1+

### Paso 5: Configurar Variables de Entorno (Opcional)

#### Modo Desarrollo (Sin API Key - Recomendado para Pruebas)

El sistema funciona **sin configuración adicional** usando recomendaciones inteligentes basadas en análisis del DataFrame. No necesitas configurar nada más.

#### Modo LLM (Con OpenAI API Key - Opcional)

Si deseas usar OpenAI GPT-4 para recomendaciones más avanzadas, configura la API key:

**Windows PowerShell:**
```powershell
$env:LLM_API_KEY="tu-api-key-de-openai"
```

**Windows CMD:**
```cmd
set LLM_API_KEY=tu-api-key-de-openai
```

**Linux/Mac:**
```bash
export LLM_API_KEY="tu-api-key-de-openai"
```

**O crea un archivo `.env` en la raíz del proyecto:**
```env
LLM_API_KEY=tu-api-key-de-openai
LLM_MODEL=gpt-4
LLM_API_URL=https://api.openai.com/v1
LLM_TIMEOUT=30
```

### Paso 6: Ejecutar la Aplicación

```bash
python run.py
```

Deberías ver algo como:
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

La aplicación estará disponible en `http://localhost:5000`

### Paso 7: Verificar que Funciona

Prueba el endpoint de salud:
```bash
curl http://localhost:5000/health
```

O abre en tu navegador: `http://localhost:5000/health`

---

## 🔧 Decisiones Técnicas

### Framework: Flask

**¿Por qué Flask?**

- **Simplicidad**: Framework minimalista y flexible, ideal para APIs REST
- **Ligereza**: Menor overhead comparado con frameworks más pesados como Django
- **Extensibilidad**: Fácil de extender con blueprints y plugins
- **Comunidad**: Amplia documentación y comunidad activa
- **Python nativo**: Integración perfecta con pandas y otras librerías de ciencia de datos

**Alternativas consideradas:**
- **FastAPI**: Más moderno pero requiere Python 3.7+ y tiene curva de aprendizaje
- **Django**: Demasiado pesado para una API simple, mejor para aplicaciones web completas

### Procesamiento de Datos: Pandas

**¿Por qué Pandas?**

- **Estándar de la industria**: Librería más usada para análisis de datos en Python
- **Funciones potentes**: `describe()`, `info()`, operaciones de agregación nativas
- **Manejo de archivos**: Soporte nativo para CSV, Excel, JSON con `read_csv()`, `read_excel()`, etc.
- **Rendimiento**: Optimizado para trabajar con grandes volúmenes de datos
- **Compatibilidad**: Funciona perfectamente con NumPy y otras librerías científicas

### Cliente HTTP: requests

**¿Por qué requests en lugar de urllib3?**

- **API más limpia**: Sintaxis más intuitiva y legible
- **Mejor manejo de errores**: Excepciones más claras
- **Sesiones**: Soporte para mantener conexiones HTTP persistentes
- **Estándar de facto**: Librería más popular para HTTP en Python

### Persistencia: Sin Base de Datos

**¿Por qué no usar base de datos?**

- **Simplicidad**: Para MVP y prototipos, los archivos son suficientes
- **Stateless**: Cada petición procesa el archivo directamente
- **Escalabilidad futura**: Fácil migrar a base de datos si se necesita
- **Archivos temporales**: Los archivos subidos se almacenan localmente (se pueden limpiar periódicamente)

### Manejo de Archivos: werkzeug.utils.secure_filename

**¿Por qué secure_filename?**

- **Seguridad**: Previene path traversal attacks y caracteres maliciosos en nombres de archivo
- **Compatibilidad**: Asegura nombres de archivo válidos en diferentes sistemas operativos
- **Integración**: Incluido en Flask, no requiere dependencias adicionales

### Validación: Custom Validators

**¿Por qué validadores personalizados?**

- **Control**: Validación específica para nuestro caso de uso
- **Mensajes de error claros**: Mensajes específicos para el usuario
- **Separación de responsabilidades**: Lógica de validación separada de los controladores
- **Reutilización**: Validadores que se pueden usar en múltiples endpoints

### Arquitectura: Capas de Servicio

**¿Por qué Service Layer Pattern?**

- **Separación de responsabilidades**: Lógica de negocio separada de controladores
- **Testabilidad**: Fácil de testear servicios de forma aislada
- **Reutilización**: Servicios pueden ser usados por múltiples controladores
- **Mantenibilidad**: Cambios en lógica de negocio no afectan la API directamente

---

## 🧠 Ingeniería de Prompts para la IA

### Estrategia General

El enfoque para la ingeniería de prompts sigue los principios de **clarity, context, and constraint** (claridad, contexto y restricciones):

1. **Definir el Rol**: La IA actúa como "experto analista de datos"
2. **Proveer Contexto Estructurado**: Datos organizados y etiquetados claramente
3. **Especificar el Formato**: JSON estructurado con campos requeridos
4. **Establecer Restricciones**: Número de recomendaciones, tipos de gráficos válidos

### Estructura del Prompt de Recomendaciones

```python
"""
Estructura del prompt:
1. Role Definition (Definición de Rol)
2. Context Data (Datos de Contexto)
   - Dataset Structure
   - Column Analysis
   - Statistical Summary
   - Sample Data
3. Task Definition (Definición de Tarea)
4. Output Format (Formato de Salida)
5. Constraints (Restricciones)
"""
```

### Componentes del Prompt

#### 1. Role Definition (Líneas 135-136)

```python
"You are an expert data analyst specializing in data visualization."
```

**¿Por qué?** 
- Establece el contexto y conocimiento esperado
- La IA adopta un "persona" especializado
- Resulta en respuestas más precisas y profesionales

#### 2. Context Data - Dataset Information

```python
f"""
DATASET INFORMATION:
- Shape: {shape.get('rows', 0)} rows × {shape.get('columns', 0)} columns
- Columns: {', '.join(columns)}
"""
```

**¿Por qué incluir estructura del dataset?**
- Proporciona una vista general rápida del tamaño y alcance
- Ayuda a la IA a dimensionar la complejidad del análisis

#### 3. Context Data - Column Analysis

```python
f"""
COLUMN ANALYSIS:
{self._format_column_info(columns, dtypes, column_types)}
"""
```

**¿Por qué análisis detallado de columnas?**
- La IA necesita entender los tipos de datos para sugerir gráficos apropiados
- Diferencia entre numéricas, categóricas y fechas es crucial
- Ejemplo: Si hay una columna de fecha, sugiere gráficos de línea temporales

#### 4. Context Data - Statistical Summary

```python
f"""
STATISTICAL SUMMARY:
{json.dumps(describe, indent=2)}
"""
```

**¿Por qué estadísticas descriptivas?**
- Permite a la IA identificar distribuciones, rangos y valores atípicos
- Puede detectar patrones: ¿los datos tienen mucha variación? ¿Hay outliers?
- Informa decisiones sobre qué visualizaciones serán más útiles

#### 5. Context Data - Sample Data

```python
f"""
SAMPLE DATA (first 3 rows):
{json.dumps(sample_data, indent=2, default=str)}
"""
```

**¿Por qué datos de muestra?**
- Da contexto real de cómo se ven los datos
- Permite a la IA entender los valores específicos (nombres de categorías, rangos numéricos)
- Ayuda a generar títulos y insights más específicos

#### 6. Task Definition

```python
"""
Act as an expert data analyst and identify the most interesting patterns, 
trends, correlations, or relationships in this dataset. Then recommend 
3-5 specific chart visualizations that would best highlight these insights.
"""
```

**¿Por qué ser específico en la tarea?**
- Define claramente qué se espera: identificar patrones Y sugerir visualizaciones
- Especifica el número de recomendaciones (3-5)
- Enfatiza "interesting" - no solo cualquier visualización

#### 7. Output Format Specification

```python
"""
For each recommendation, you must provide:
1. **title**: A descriptive, meaningful title for the chart
2. **chart_type**: One of: "bar", "line", "pie", or "scatter"
3. **parameters**: An object specifying which columns to use
4. **insight**: A brief 1-2 sentence explanation
"""
```

**¿Por qué especificar el formato exacto?**
- Garantiza respuestas estructuradas y parseables
- Evita variaciones en el formato que romperían el parsing
- Facilita la validación posterior

#### 8. Constraints and Guidelines

```python
"""
FOCUS ON:
- Identifying meaningful relationships between variables
- Highlighting trends, distributions, or outliers
- Comparing categories or groups
- Showing correlations or patterns

IMPORTANT: 
- Return ONLY a valid JSON array
- Each recommendation must have exactly these fields
- The parameters must reference actual column names
- Provide 3-5 recommendations, no more, no less
"""
```

**¿Por qué restricciones explícitas?**
- Limita el espacio de respuesta para evitar divergencias
- Asegura que se usen nombres de columnas reales
- Garantiza consistencia en el número de recomendaciones

### Ejemplo de Prompt Completo

```python
"""
You are an expert data analyst specializing in data visualization. 
Your task is to analyze a dataset and recommend 3-5 specific visualizations.

DATASET INFORMATION:
- Shape: 100 rows × 5 columns
- Columns: Region, Sales, Date, Category, Revenue

COLUMN ANALYSIS:
  - Region: object (categorical)
  - Sales: float64 (numeric)
  - Date: datetime64[ns] (datetime)
  - Category: object (categorical)
  - Revenue: float64 (numeric)

STATISTICAL SUMMARY:
{
  "Sales": {
    "mean": 1500.5,
    "std": 500.2,
    "min": 200.0,
    "max": 3000.0
  }
}

SAMPLE DATA:
[
  {"Region": "North", "Sales": 1500, "Date": "2024-01-01"},
  {"Region": "South", "Sales": 2000, "Date": "2024-01-02"}
]

[Task Definition + Format + Constraints]
"""
```

### Técnicas de Ingeniería de Prompts Utilizadas

1. **Few-Shot Learning**: Incluimos ejemplos del formato esperado
2. **Chain-of-Thought**: Pedimos a la IA que identifique patrones primero, luego sugiera visualizaciones
3. **Output Constraints**: Especificamos formato JSON estricto
4. **Role Playing**: La IA actúa como "experto analista"
5. **Structured Context**: Organizamos la información en secciones claras

### Validación y Parsing de Respuestas

```python
def _parse_recommendations(self, content: str) -> List[Dict[str, Any]]:
    # Elimina markdown code blocks si existen
    # Intenta parsear JSON
    # Valida estructura
    # Retorna lista validada
```

**¿Por qué validación post-procesamiento?**
- Las LLMs pueden incluir texto adicional además del JSON
- Validación asegura que la respuesta es usable
- Fallback a modo mock si falla

---

## 📡 API Endpoints

### POST /api/upload

Sube un archivo y obtiene recomendaciones automáticas de gráficos.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV, XLSX, XLS, o JSON)

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded and analyzed successfully",
  "file_info": {
    "filename": "data.csv",
    "size": 12345,
    "filepath": "uploads/data.csv"
  },
  "recommendations": [
    {
      "title": "Sales by Region",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "Region",
        "y_axis": "Sales"
      },
      "insight": "This visualization reveals significant regional variations..."
    }
  ],
  "data_summary": {
    "shape": {"rows": 100, "columns": 5},
    "columns": ["Region", "Sales", "Date"],
    "column_types": {"Region": "categorical", "Sales": "numeric"}
  }
}
```

### POST /api/chart/data

Obtiene datos agregados y formateados para un gráfico específico.

**Request Body:**
```json
{
  "filepath": "uploads/data.csv",
  "chart_type": "bar",
  "parameters": {
    "x_axis": "Region",
    "y_axis": "Sales"
  },
  "aggregation": "sum"
}
```

**Response:**
```json
{
  "chart_type": "bar",
  "data": {
    "labels": ["North", "South", "East", "West"],
    "values": [1000, 1500, 1200, 1800],
    "data": [
      {"Region": "North", "Sales": 1000}
    ]
  },
  "parameters": {
    "x_axis": "Region",
    "y_axis": "Sales"
  },
  "aggregation": "sum"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 💻 Ejemplos de Consumo con cURL

### 1. Subir Archivo y Obtener Recomendaciones

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@ruta/a/tu/archivo.csv"
```

**Ejemplo con archivo Excel:**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@datos_ventas.xlsx"
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "File uploaded and analyzed successfully",
  "file_info": {
    "filename": "datos_ventas.xlsx",
    "size": 45678,
    "filepath": "uploads/datos_ventas.xlsx"
  },
  "recommendations": [
    {
      "title": "Ventas por Región",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "Region",
        "y_axis": "Sales"
      },
      "insight": "Muestra las variaciones regionales en ventas..."
    },
    {
      "title": "Tendencia de Ventas Mensual",
      "chart_type": "line",
      "parameters": {
        "x_axis": "Month",
        "y_axis": "Revenue"
      },
      "insight": "Revela la tendencia de ingresos a lo largo del tiempo..."
    }
  ],
  "data_summary": {
    "shape": {"rows": 100, "columns": 5},
    "columns": ["Region", "Sales", "Month", "Revenue", "Category"],
    "column_types": {
      "Region": "categorical",
      "Sales": "numeric",
      "Month": "datetime",
      "Revenue": "numeric",
      "Category": "categorical"
    }
  }
}
```

### 2. Obtener Datos para Gráfico de Barras

```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos_ventas.xlsx",
    "chart_type": "bar",
    "parameters": {
      "x_axis": "Region",
      "y_axis": "Sales"
    },
    "aggregation": "sum"
  }'
```

**Respuesta:**
```json
{
  "chart_type": "bar",
  "data": {
    "labels": ["North", "South", "East", "West"],
    "values": [15000, 20000, 18000, 22000],
    "data": [
      {"Region": "North", "Sales": 15000},
      {"Region": "South", "Sales": 20000},
      {"Region": "East", "Sales": 18000},
      {"Region": "West", "Sales": 22000}
    ]
  },
  "parameters": {
    "x_axis": "Region",
    "y_axis": "Sales"
  },
  "aggregation": "sum"
}
```

### 3. Obtener Datos para Gráfico de Línea

```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos_ventas.xlsx",
    "chart_type": "line",
    "parameters": {
      "x_axis": "Month",
      "y_axis": "Revenue"
    },
    "aggregation": "mean"
  }'
```

### 4. Obtener Datos para Gráfico Circular (Pie)

```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos_ventas.xlsx",
    "chart_type": "pie",
    "parameters": {
      "x_axis": "Category",
      "y_axis": "Count"
    },
    "aggregation": "sum"
  }'
```

**Nota:** Para pie charts, `y_axis` es opcional. Si no se proporciona, cuenta ocurrencias:

```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos_ventas.xlsx",
    "chart_type": "pie",
    "parameters": {
      "x_axis": "Category"
    }
  }'
```

### 5. Obtener Datos para Gráfico de Dispersión (Scatter)

```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos_ventas.xlsx",
    "chart_type": "scatter",
    "parameters": {
      "x_axis": "Age",
      "y_axis": "Salary"
    }
  }'
```

**Nota:** Para scatter plots, `aggregation` se ignora ya que muestra puntos individuales.

### 6. Flujo Completo: Subir y Visualizar

```bash
# Paso 1: Subir archivo
UPLOAD_RESPONSE=$(curl -X POST http://localhost:5000/api/upload \
  -F "file=@mi_datos.csv")

# Extraer filepath de la respuesta (requiere jq o procesamiento manual)
FILEPATH=$(echo $UPLOAD_RESPONSE | jq -r '.file_info.filepath')
CHART_TYPE=$(echo $UPLOAD_RESPONSE | jq -r '.recommendations[0].chart_type')
X_AXIS=$(echo $UPLOAD_RESPONSE | jq -r '.recommendations[0].parameters.x_axis')
Y_AXIS=$(echo $UPLOAD_RESPONSE | jq -r '.recommendations[0].parameters.y_axis')

# Paso 2: Obtener datos del primer gráfico recomendado
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d "{
    \"filepath\": \"$FILEPATH\",
    \"chart_type\": \"$CHART_TYPE\",
    \"parameters\": {
      \"x_axis\": \"$X_AXIS\",
      \"y_axis\": \"$Y_AXIS\"
    },
    \"aggregation\": \"sum\"
  }"
```

### 7. Verificar Salud del Servidor

```bash
curl http://localhost:5000/health
```

**Respuesta:**
```json
{
  "status": "healthy"
}
```

---

## 🏗️ Arquitectura del Proyecto

```
project/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # Flask app factory con configuración
│   ├── exceptions.py          # Excepciones personalizadas
│   │
│   ├── api/                   # Capa de Controladores (REST)
│   │   ├── __init__.py
│   │   ├── upload_controller.py   # Endpoint de carga de archivos
│   │   └── chart_controller.py    # Endpoint de datos de gráficos
│   │
│   ├── services/              # Capa de Lógica de Negocio
│   │   ├── __init__.py
│   │   ├── file_service.py        # Procesamiento de archivos
│   │   ├── dataframe_service.py   # Análisis de DataFrames (pandas)
│   │   ├── ai_analysis_service.py # Lógica de IA y prompts
│   │   ├── chart_service.py       # Orquestación de servicios
│   │   └── mock_recommendation_service.py  # Recomendaciones sin LLM
│   │
│   ├── clients/               # Clientes de APIs Externas
│   │   ├── __init__.py
│   │   └── llm_client.py          # Cliente de OpenAI
│   │
│   ├── models/                # Modelos de Datos
│   │   └── chart_suggestion.py
│   │
│   └── utils/                 # Utilidades
│       └── validators.py          # Validadores reutilizables
│
├── uploads/                   # Archivos subidos (gitignored)
├── logs/                      # Logs de la aplicación
├── venv/                      # Entorno virtual (gitignored)
├── requirements.txt           # Dependencias del proyecto
├── run.py                     # Punto de entrada
└── README.md                  # Este archivo
```

---

## 🎨 Patrones de Diseño

### Application Factory Pattern
- **Ubicación**: `app/main.py`
- **Propósito**: Crear instancia de Flask de forma modular y testeable
- **Ventajas**: Permite diferentes configuraciones por entorno

### Service Layer Pattern
- **Ubicación**: `app/services/`
- **Propósito**: Separar lógica de negocio de controladores
- **Ventajas**: Testeable, reutilizable, mantenible

### Strategy Pattern
- **Ubicación**: `app/clients/llm_client.py`
- **Propósito**: Abstraer diferentes proveedores de LLM
- **Ventajas**: Fácil cambiar de OpenAI a otro proveedor

### Dependency Injection
- **Ubicación**: Constructores de servicios
- **Propósito**: Inyectar dependencias para mejor testeo
- **Ventajas**: Bajo acoplamiento, fácil mockear en tests

### Repository Pattern (Implícito)
- **Ubicación**: `app/services/dataframe_service.py`
- **Propósito**: Abstraer acceso a datos
- **Ventajas**: Fácil cambiar de archivos a base de datos

---

## 🔄 Modo de Funcionamiento

### Modo Desarrollo (Default)

Cuando **no hay API key configurada**, el sistema funciona con **recomendaciones inteligentes** basadas en análisis automático del DataFrame:

- ✅ Detecta tipos de columnas (numéricas, categóricas, fechas)
- ✅ Analiza relaciones entre columnas
- ✅ Genera 3-5 recomendaciones apropiadas
- ✅ **No requiere API key de OpenAI**

### Modo LLM (Opcional)

Si configuras `LLM_API_KEY`, el sistema usa **OpenAI GPT-4** para:

- ✅ Análisis más profundo de patrones
- ✅ Recomendaciones más contextuales
- ✅ Insights más detallados y específicos
- ✅ Mejor comprensión de relaciones complejas

**Fallback Automático:** Si falla la llamada a LLM, el sistema automáticamente usa el modo desarrollo.

---

## 📦 Dependencias Principales

| Librería | Versión | Propósito |
|----------|---------|-----------|
| Flask | 3.1.2+ | Framework web para API REST |
| pandas | 2.3.3+ | Análisis y procesamiento de datos |
| openpyxl | 3.1.5+ | Lectura de archivos Excel |
| requests | 2.32.5+ | Cliente HTTP para llamadas a OpenAI API |
| werkzeug | 3.1.5+ | Utilidades de Flask (seguridad, validación) |
| python-dotenv | 1.2.1+ | Carga de variables de entorno desde .env |

---

## 🧪 Testing

Para probar los endpoints:

1. **Health Check:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Subir archivo:**
   ```bash
   curl -X POST http://localhost:5000/api/upload -F "file=@test.csv"
   ```

3. **Obtener datos de gráfico:**
   ```bash
   curl -X POST http://localhost:5000/api/chart/data \
     -H "Content-Type: application/json" \
     -d '{"filepath": "uploads/test.csv", "chart_type": "bar", ...}'
   ```

---

## 📝 Notas Adicionales

- Los archivos subidos se guardan en `uploads/` (asegúrate de limpiar periódicamente)
- Los logs se guardan en `logs/app.log` en producción
- El tamaño máximo de archivo es 10MB por defecto
- Formatos soportados: CSV, XLSX, XLS, JSON

---

## 📄 Licencia

MIT

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

## 📞 Soporte

Si encuentras algún problema o tienes preguntas, abre un issue en el repositorio.
