# Dashboard de Detección de Anomalías

## Qué hace este proyecto

Este proyecto implementa un dashboard interactivo en Streamlit para analizar transacciones digitales y distinguir comportamientos normales, alertas y anomalías. La aplicación combina análisis descriptivo e inferencial sobre una base de datos cargada desde un archivo Excel y presenta los resultados en tablas y visualizaciones interactivas.

El objetivo principal es apoyar un trabajo de estadística mostrando:

- métricas generales del conjunto filtrado de transacciones,
- distribución de variables numéricas y categóricas,
- detección de valores atípicos,
- pruebas de hipótesis ya calculadas,
- intervalos de confianza para comparar grupos.

## Tecnologías usadas

- Streamlit para la interfaz web
- Pandas y NumPy para manipulación de datos
- Plotly para visualizaciones interactivas
- SciPy como dependencia estadística
- OpenPyXL para lectura del archivo Excel

Dependencias declaradas en `requirements.txt`:

- streamlit==1.57.0
- pandas==3.0.3
- numpy==2.2.6
- plotly==6.7.0
- scipy==1.15.3
- openpyxl==3.1.5

## Estructura del proyecto

- `app.py`: aplicación principal de Streamlit.
- `CALCULOS TRABAJO ESTADISTICA.xlsx`: fuente de datos y resultados precalculados.
- `.streamlit/config.toml`: configuración visual y del servidor de Streamlit.
- `requirements.txt`: dependencias del proyecto.

## Flujo general de la aplicación

La lógica completa vive en `app.py`.

1. Configura la página de Streamlit en formato ancho y aplica un tema visual oscuro con CSS personalizado.
2. Carga el archivo `CALCULOS TRABAJO ESTADISTICA.xlsx`.
3. Filtra los registros para conservar únicamente eventos de tipo `Normal`, `Alerta` y `Anomalia`.
4. Renombra columnas y convierte a numéricas las variables principales: `Monto`, `Tiempo`, `Frecuencia` y `Score`.
5. Permite filtrar la información desde la barra lateral por:
	- tipo de evento,
	- ubicación,
	- dispositivo,
	- rango del score de anomalía.
6. Calcula métricas y renderiza las secciones analíticas del dashboard.

## Datos que espera el proyecto

La aplicación depende de un archivo Excel llamado exactamente:

`CALCULOS TRABAJO ESTADISTICA.xlsx`

### Hoja principal

La carga principal del dashboard asume que el Excel contiene columnas equivalentes a estas once variables, que luego son renombradas internamente:

- ID
- Monto
- Tiempo
- Frecuencia
- Score
- Tipo_Evento
- Ubicacion
- Dispositivo
- Estado_Cuenta
- Resultado_Modelo
- Resultado_Hipotesis

### Hojas adicionales usadas

Además de la hoja principal, el dashboard lee información precalculada de estas hojas:

- `DETECCION_ATIPICOS`: resumen y registros de valores atípicos.
- `Hoja2`: intervalos de confianza por variable y grupo.

Esto significa que el proyecto no calcula todo desde cero en tiempo real: parte de los resultados estadísticos ya vienen preparados en el Excel y la app los presenta visualmente.

## Secciones del dashboard

### 1. KPIs generales

Muestra tarjetas con:

- total de transacciones visibles tras aplicar filtros,
- cantidad de anomalías,
- cantidad de alertas,
- número de casos cuyo `Resultado_Hipotesis` es `Rechaza H0`.

También calcula porcentajes sobre el total filtrado.

### 2. Identificación de variables

Presenta una tabla descriptiva con el tipo de variable, sus unidades o categorías y su rol dentro del análisis. Sirve como marco metodológico para entender qué representa cada columna.

### 3. Estadísticas descriptivas

Incluye tres pestañas:

- tabla resumen con media, mediana, desviación estándar, mínimo, máximo, cuartiles e IQR,
- histogramas superpuestos por tipo de evento,
- boxplots por variable seleccionada.

Las variables numéricas analizadas aquí son:

- Monto
- Tiempo
- Frecuencia
- Score

### 4. Tablas de frecuencia

Construye distribuciones para variables categóricas y las muestra tanto en gráficos como en tablas:

- Tipo de Evento
- Ubicación
- Dispositivo
- Estado de Cuenta

### 5. Detección de valores atípicos

La sección de atípicos usa datos provenientes de la hoja `DETECCION_ATIPICOS` del Excel y muestra:

- tarjetas resumen de atípicos por método,
- tabla con Q1, Q3, IQR y límites del método IQR,
- gráfico comparativo entre IQR y regla `3σ`,
- dispersión de `Monto` vs `Score` para registros atípicos,
- tabla detallada de registros identificados como atípicos.

En esta parte el proyecto visualiza resultados ya consolidados en el archivo Excel, en lugar de recalcular todo directamente desde el dataframe principal.

### 6. Pruebas de hipótesis

La app muestra dos pruebas t de Student con valores cargados de forma fija dentro del código:

### Prueba 1

- Variable: `Score_Anomalia`
- Comparación: normal vs anomalía
- Tipo: unilateral
- Resultado mostrado: se rechaza H0

Interpretación incluida en la app: el score diferencia significativamente los comportamientos anómalos respecto a los normales.

### Prueba 2

- Variable: `Monto_Transaccion`
- Comparación: normal vs anomalía
- Tipo: bilateral
- Resultado mostrado: no se rechaza H0

Interpretación incluida en la app: no hay evidencia suficiente de diferencia estadísticamente significativa entre montos promedio de transacciones normales y anómalas.

### 7. Intervalos de confianza

Lee la hoja `Hoja2` y construye:

- tabla completa de medias, desviaciones, errores estándar e intervalos al 95 % y 99 %,
- gráfico comparativo por grupo,
- tarjetas individuales por grupo con amplitud del intervalo y tamaño muestral.

La visualización compara grupos `Normal`, `Alerta` y `Anomalia` para la variable seleccionada.

## Comportamiento de filtrado

Todos los filtros definidos en la barra lateral se aplican sobre el dataframe principal antes de generar:

- KPIs,
- estadísticas descriptivas,
- tablas de frecuencia,
- histogramas,
- boxplots.

Sin embargo, algunas secciones como atípicos e intervalos de confianza dependen de hojas específicas del Excel con resultados ya preparados, por lo que conceptualmente mezclan análisis dinámico con resultados precalculados.

## Puntos importantes del diseño actual

- La aplicación usa `@st.cache_data` para evitar recargar repetidamente los datos del Excel.
- El diseño visual está altamente personalizado con CSS embebido en `app.py`.
- El proyecto está pensado para ejecutarse localmente como dashboard académico o demostrativo.
- Si falta el archivo Excel o cambia su estructura, la aplicación falla al cargar y se detiene mostrando un error en pantalla.

## Cómo ejecutar el proyecto

### 1. Crear o activar un entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```powershell
streamlit run app.py
```

Después, Streamlit abrirá la aplicación en el navegador local.

## Posibles limitaciones

- El archivo Excel es parte crítica del sistema y actúa como base de datos y fuente de resultados estadísticos.
- Los nombres de algunas hojas y posiciones de lectura están fijos en el código, por lo que cambios en el Excel pueden romper la app.
- Las pruebas de hipótesis del bloque 5 están codificadas manualmente y no se recalculan a partir de los datos filtrados.

## Resumen funcional

En términos prácticos, este proyecto sirve para explorar un conjunto de transacciones digitales, segmentarlo por tipo de evento y contexto, visualizar su comportamiento estadístico y mostrar evidencia inferencial sobre diferencias entre transacciones normales y anómalas.

No es un modelo de detección entrenado en tiempo real, sino un dashboard analítico que consume datos y resultados estadísticos preparados para presentarlos de forma clara e interactiva.
