# Proyecto ETL y Visualización de Tasas de Interés Bancario Corriente (TIBC)

Este proyecto implementa un pipeline de Extracción, Transformación y Carga (ETL) para obtener datos de Tasas de Interés Bancario Corriente (TIBC) de fuentes públicas, procesarlos y almacenarlos en una base de datos SQLite. Adicionalmente, incluye scripts para la visualización de los datos resultantes.

##  Características

* **Extracción (Extract):** Obtiene datos de tasas de interés bancario corriente desde la API de datos.gov.co.
* **Transformación (Transform):** Limpia, normaliza y estructura los datos, incluyendo la conversión de tipos de datos y el manejo de valores nulos.
* **Carga (Load):** Almacena los datos transformados en una base de datos SQLite (`tibc_data.db`) para facilitar su consulta y análisis.
* **Automatización:** Configurado para ejecutarse diariamente en Windows mediante el Programador de Tareas, asegurando que los datos estén siempre actualizados.
* **Visualización:** Genera gráficos clave para entender las tendencias y distribuciones de las tasas de interés.

##  Visualizaciones Generadas

El script de visualización (`visualizacion_tibc.py`) genera los siguientes gráficos:

1.  **Historial de Tasa de Interés Bancario Corriente (EA):** Muestra la evolución de las tasas a lo largo del tiempo.
    * `tasa_interes_historial.png`
2.  **Distribución de Tasas de Interés por Tipo de Crédito:** Un boxplot que ilustra la dispersión de las tasas para cada modalidad de crédito.
    * `tasa_interes_distribucion_tipo_credito.png`
3.  **Top 5 Tasas de Interés Bancario Corriente Más Altas Registradas:** Un gráfico de barras que destaca las tasas más elevadas encontradas en el dataset.
    * `top_5_tasas_altas.png`

Estas imágenes se guardan automáticamente en la carpeta raíz del proyecto.

##  Tecnologías Utilizadas

* **Python 3.x:** Lenguaje de programación principal.
* **Pandas:** Para manipulación y análisis de datos.
* **SQLite3:** Base de datos ligera para almacenamiento local.
* **Matplotlib:** Para la creación de gráficos estáticos.
* **Seaborn:** Para visualizaciones estadísticas más atractivas.
* **Git:** Sistema de control de versiones.
* **Programador de Tareas de Windows:** Para la automatización del pipeline ETL.

##  Estructura del Proyecto
proyecto_etl_datos/
├── .venv/                         # Entorno virtual de Python
├── etl_tibc.py                    # Script principal del pipeline ETL
├── visualizacion_tibc.py          # Script para generar visualizaciones
├── tibc_data.db                   # Base de datos SQLite (generada por el ETL)
├── tasa_interes_historial.png     # Gráfico de historial de tasas (generado por visualización)
├── tasa_interes_distribucion_tipo_credito.png # Gráfico de distribución (generado por visualización)
├── top_5_tasas_altas.png          # Gráfico de top 5 tasas (generado por visualización)
├── README.md                      # Documentación del proyecto (este archivo)
└── .gitignore                     # Archivo para ignorar archivos y carpetas en Git


## 🚀 Cómo Ejecutar el Proyecto

### Requisitos Previos

* Python 3.x instalado.
* Git instalado.
* Acceso a internet para la extracción de datos.

### Pasos de Configuración

1.  **Clonar el Repositorio (si lo estás descargando de GitHub):**
    ```bash
    git clone [https://github.com/TuUsuario/NombreDeTuRepositorio.git](https://github.com/TuUsuario/NombreDeTuRepositorio.git)
    cd NombreDeTuRepositorio
    ```
    *(Si ya tienes la carpeta localmente, omite este paso y ve directamente a tu carpeta)*

2.  **Crear y Activar el Entorno Virtual:**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1   # En Windows PowerShell
    # source .venv/bin/activate    # En Linux/macOS o Git Bash
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install pandas matplotlib seaborn
    ```

4.  **Ejecutar el Pipeline ETL (manual):**
    Para generar o actualizar la base de datos `tibc_data.db`:
    ```bash
    .\.venv\Scripts\python.exe etl_tibc.py
    ```

5.  **Generar Visualizaciones (manual):**
    Para crear los archivos `.png` de los gráficos:
    ```bash
    .\.venv\Scripts\python.exe visualizacion_tibc.py
    ```

### Automatización (Windows)

El script `etl_tibc.py` puede ser programado para ejecutarse diariamente usando el **Programador de Tareas de Windows**.

1.  **Abrir el Programador de Tareas:** Buscar "Programador de Tareas" en el menú de inicio.
2.  **Crear Tarea Básica:**
    * **Nombre:** `ETL_TIBC_Diario`
    * **Desencadenador:** Diariamente, a la hora deseada (ej. 03:00 AM).
    * **Acción:** "Iniciar un programa".
    * **Programa o script:** `E:\Bibliotecas\Documents\proyecto_etl_datos\.venv\Scripts\python.exe` (Ruta completa a tu intérprete Python del entorno virtual)
    * **Agregar argumentos (opcional):** `E:\Bibliotecas\Documents\proyecto_etl_datos\etl_tibc.py` (Ruta completa a tu script ETL)
    * **Iniciar en (opcional):** `E:\Bibliotecas\Documents\proyecto_etl_datos` (Ruta a la carpeta raíz de tu proyecto)

##  Contribuciones

Las contribuciones son bienvenidas. Si tienes sugerencias o mejoras, no dudes en abrir un *issue* o enviar un *pull request*.

##  Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

##  Contacto

**Julián Aguas**
Estudiante de Ingeniería de Sistemas