# Ejemplos de Uso de la API

## Endpoint: POST /api/chart/data

Este endpoint recibe los parámetros de un gráfico y devuelve los datos agregados y formateados listos para visualizar.

---

## Estructura de la Petición

### Headers
```
Content-Type: application/json
```

### Body (JSON)
```json
{
  "filepath": "uploads/nombre_archivo.csv",
  "chart_type": "bar|line|pie|scatter",
  "parameters": {
    "x_axis": "NombreColumna",
    "y_axis": "NombreColumna"  // opcional para pie charts
  },
  "aggregation": "sum|mean|count|max|min"  // opcional, default: "sum"
}
```

### Campos Requeridos
- `filepath`: Ruta del archivo (obtenida del endpoint `/api/upload`)
- `chart_type`: Tipo de gráfico (`bar`, `line`, `pie`, `scatter`)
- `parameters.x_axis`: Nombre de la columna para el eje X
- `parameters.y_axis`: Nombre de la columna para el eje Y (requerido para bar/line/scatter, opcional para pie)

### Campos Opcionales
- `aggregation`: Función de agregación (`sum`, `mean`, `count`, `max`, `min`) - default: `sum`

---

## Ejemplos por Herramienta

### 1. cURL (Terminal/Command Line)

#### Gráfico de Barras (Bar Chart)
```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos.csv",
    "chart_type": "bar",
    "parameters": {
      "x_axis": "Region",
      "y_axis": "Sales"
    },
    "aggregation": "sum"
  }'
```

#### Gráfico de Línea (Line Chart)
```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/ventas.xlsx",
    "chart_type": "line",
    "parameters": {
      "x_axis": "Date",
      "y_axis": "Revenue"
    },
    "aggregation": "mean"
  }'
```

#### Gráfico Circular (Pie Chart)
```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/categorias.csv",
    "chart_type": "pie",
    "parameters": {
      "x_axis": "Category",
      "y_axis": "Count"
    },
    "aggregation": "sum"
  }'
```

#### Gráfico de Dispersión (Scatter Plot)
```bash
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/datos.csv",
    "chart_type": "scatter",
    "parameters": {
      "x_axis": "Age",
      "y_axis": "Salary"
    }
  }'
```

---

### 2. JavaScript (Fetch API)

```javascript
// Función para obtener datos del gráfico
async function getChartData(filepath, chartType, xAxis, yAxis, aggregation = 'sum') {
  try {
    const response = await fetch('http://localhost:5000/api/chart/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filepath: filepath,
        chart_type: chartType,
        parameters: {
          x_axis: xAxis,
          y_axis: yAxis
        },
        aggregation: aggregation
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error al obtener datos del gráfico');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Ejemplo de uso - Gráfico de Barras
getChartData('uploads/datos.csv', 'bar', 'Region', 'Sales', 'sum')
  .then(chartData => {
    console.log('Datos del gráfico:', chartData);
    // Usar chartData.data.labels y chartData.data.values para crear el gráfico
  })
  .catch(error => {
    console.error('Error al obtener datos:', error);
  });

// Ejemplo de uso - Gráfico Circular
getChartData('uploads/categorias.csv', 'pie', 'Category', 'Count', 'sum')
  .then(chartData => {
    console.log('Datos del gráfico:', chartData);
    // Usar chartData.data.labels y chartData.data.values para crear el gráfico
  });
```

---

### 3. Python (requests)

```python
import requests
import json

# URL del endpoint
url = "http://localhost:5000/api/chart/data"

# Ejemplo 1: Gráfico de Barras
def get_bar_chart_data(filepath, x_axis, y_axis, aggregation='sum'):
    payload = {
        "filepath": filepath,
        "chart_type": "bar",
        "parameters": {
            "x_axis": x_axis,
            "y_axis": y_axis
        },
        "aggregation": aggregation
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Ejemplo de uso
chart_data = get_bar_chart_data('uploads/datos.csv', 'Region', 'Sales', 'sum')
if chart_data:
    print("Labels:", chart_data['data']['labels'])
    print("Values:", chart_data['data']['values'])
```

```python
# Ejemplo 2: Gráfico Circular
def get_pie_chart_data(filepath, category_col, value_col=None, aggregation='sum'):
    payload = {
        "filepath": filepath,
        "chart_type": "pie",
        "parameters": {
            "x_axis": category_col
        },
        "aggregation": aggregation
    }
    
    # Agregar y_axis si se especifica
    if value_col:
        payload["parameters"]["y_axis"] = value_col
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Ejemplo de uso
pie_data = get_pie_chart_data('uploads/categorias.csv', 'Category', 'Count', 'sum')
if pie_data:
    print("Labels:", pie_data['data']['labels'])
    print("Values:", pie_data['data']['values'])
```

```python
# Ejemplo 3: Gráfico de Línea
def get_line_chart_data(filepath, x_axis, y_axis, aggregation='mean'):
    payload = {
        "filepath": filepath,
        "chart_type": "line",
        "parameters": {
            "x_axis": x_axis,
            "y_axis": y_axis
        },
        "aggregation": aggregation
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Ejemplo de uso
line_data = get_line_chart_data('uploads/ventas.xlsx', 'Date', 'Revenue', 'mean')
if line_data:
    print("Labels:", line_data['data']['labels'])
    print("Values:", line_data['data']['values'])
```

---

### 4. Postman

1. **Método**: POST
2. **URL**: `http://localhost:5000/api/chart/data`
3. **Headers**:
   - Key: `Content-Type`
   - Value: `application/json`
4. **Body** (raw JSON):
   ```json
   {
     "filepath": "uploads/datos.csv",
     "chart_type": "bar",
     "parameters": {
       "x_axis": "Region",
       "y_axis": "Sales"
     },
     "aggregation": "sum"
   }
   ```

---

## Estructura de la Respuesta

### Respuesta Exitosa (200 OK)

#### Para gráficos Bar y Line:
```json
{
  "chart_type": "bar",
  "data": {
    "labels": ["North", "South", "East", "West"],
    "values": [1000, 1500, 1200, 1800],
    "data": [
      {"Region": "North", "Sales": 1000},
      {"Region": "South", "Sales": 1500},
      {"Region": "East", "Sales": 1200},
      {"Region": "West", "Sales": 1800}
    ]
  },
  "parameters": {
    "x_axis": "Region",
    "y_axis": "Sales"
  },
  "aggregation": "sum"
}
```

#### Para gráficos Pie:
```json
{
  "chart_type": "pie",
  "data": {
    "labels": ["Category A", "Category B", "Category C"],
    "values": [45, 30, 25],
    "data": [
      {"Category": "Category A", "Count": 45},
      {"Category": "Category B", "Count": 30},
      {"Category": "Category C", "Count": 25}
    ]
  },
  "parameters": {
    "x_axis": "Category",
    "y_axis": "Count"
  },
  "aggregation": "sum"
}
```

#### Para gráficos Scatter:
```json
{
  "chart_type": "scatter",
  "data": {
    "data": [
      {"x": 25, "y": 50000},
      {"x": 30, "y": 60000},
      {"x": 35, "y": 75000}
    ],
    "x_values": [25, 30, 35],
    "y_values": [50000, 60000, 75000]
  },
  "parameters": {
    "x_axis": "Age",
    "y_axis": "Salary"
  },
  "aggregation": "sum"
}
```

### Respuesta de Error (400 Bad Request)
```json
{
  "error": "Missing required field",
  "message": "filepath is required"
}
```

### Respuesta de Error (404 Not Found)
```json
{
  "error": "File not found",
  "message": "The specified file does not exist"
}
```

---

## Flujo Completo de Uso

### Paso 1: Subir archivo y obtener recomendaciones
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@mi_archivo.csv"
```

Respuesta incluye `file_info.filepath` y `recommendations`

### Paso 2: Usar el filepath y parameters de una recomendación para obtener datos
```bash
# Usar filepath de la respuesta anterior
# Usar parameters de una recomendación (ej: recommendations[0].parameters)
curl -X POST http://localhost:5000/api/chart/data \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "uploads/mi_archivo.csv",
    "chart_type": "bar",
    "parameters": {
      "x_axis": "Region",
      "y_axis": "Sales"
    },
    "aggregation": "sum"
  }'
```

### Paso 3: Usar los datos devueltos para crear el gráfico en el frontend
```javascript
// Ejemplo con Chart.js
const chartData = await getChartData(...);
const ctx = document.getElementById('myChart').getContext('2d');
new Chart(ctx, {
  type: chartData.chart_type,
  data: {
    labels: chartData.data.labels,
    datasets: [{
      label: 'My Dataset',
      data: chartData.data.values
    }]
  }
});
```

---

## Notas Importantes

1. **filepath**: Debe ser la ruta relativa obtenida del endpoint `/api/upload` (ej: `uploads/archivo.csv`)
2. **chart_type**: Solo acepta: `bar`, `line`, `pie`, `scatter`
3. **aggregation**: Solo acepta: `sum`, `mean`, `count`, `max`, `min`
4. **y_axis**: Requerido para `bar`, `line`, `scatter`. Opcional para `pie` (si no se proporciona, cuenta ocurrencias)
5. Los nombres de columnas (`x_axis`, `y_axis`) deben coincidir exactamente con los nombres de las columnas en el archivo

---

## Troubleshooting

### Error: "Column not found in dataset"
- Verifica que los nombres de las columnas en `x_axis` y `y_axis` coincidan exactamente con los del archivo
- Los nombres son case-sensitive

### Error: "File not found"
- Verifica que el `filepath` sea correcto
- Asegúrate de que el archivo se haya subido correctamente con `/api/upload`

### Error: "Invalid chart_type"
- Solo se aceptan: `bar`, `line`, `pie`, `scatter`
