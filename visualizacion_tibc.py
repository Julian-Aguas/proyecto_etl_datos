import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys # Importar sys para salir del script en caso de error crítico

# --- Configuración ---
DATABASE_NAME = 'tibc_data.db'
TABLE_NAME = 'tasas_interes_bancario'

# --- Gestión de Rutas Robusta ---
# Obtiene el directorio absoluto donde se encuentra este script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construye la ruta completa a la base de datos
db_path = os.path.join(script_dir, DATABASE_NAME)
# Construye las rutas para guardar las imágenes
output_image_path_1 = os.path.join(script_dir, 'tasa_interes_historial.png')
output_image_path_2 = os.path.join(script_dir, 'tasa_interes_distribucion_tipo_credito.png')
output_image_path_3 = os.path.join(script_dir, 'top_5_tasas_altas.png')

print(f"********** INICIO DE GENERACIÓN DE VISUALIZACIONES **********")
print(f"Directorio de trabajo actual (desde el script): {os.getcwd()}")
print(f"Ruta del script: {script_dir}")
print(f"Ruta esperada de la base de datos: {db_path}")

# --- VERIFICACIÓN CRÍTICA: Asegurarse de que el archivo de la base de datos existe ---
if not os.path.exists(db_path):
    print(f"ERROR FATAL: La base de datos '{DATABASE_NAME}' NO se encontró en la ruta esperada: {db_path}")
    print("Asegúrate de que:")
    print("1. El script 'etl_tibc.py' se ha ejecutado y creó 'tibc_data.db'.")
    print("2. 'tibc_data.db' está en la MISMA CARPETA que 'visualizacion_tibc.py'.")
    print("********** FIN (FALLO) **********")
    sys.exit(1) # Salir del script con un código de error

try:
    # --- Paso 1: Cargar datos desde SQLite a un DataFrame de Pandas ---
    print(f"\n--- Paso 1: Conectando a la base de datos y cargando datos de la tabla '{TABLE_NAME}' ---")
    conn = sqlite3.connect(db_path)
    # pd.read_sql_query puede fallar si la tabla no existe o la consulta es errónea
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    print(f"Datos cargados exitosamente. {len(df)} filas encontradas.")

    if df.empty:
        print("ADVERTENCIA: El DataFrame está vacío. No hay datos para visualizar.")
        print("Asegúrate de que la tabla 'tasas_interes_bancario' contiene datos.")
        print("********** FIN (ADVERTENCIA) **********")
        sys.exit(0) # Salir con éxito, pero con advertencia de datos vacíos

    # Convertir columnas de fecha a datetime y la tasa a numérico
    print("Realizando conversiones de tipo de datos...")
    df['fecha_resolucion'] = pd.to_datetime(df['fecha_resolucion'], errors='coerce')
    df['vigencia_desde'] = pd.to_datetime(df['vigencia_desde'], errors='coerce')
    df['vigencia_hasta'] = pd.to_datetime(df['vigencia_hasta'], errors='coerce')
    df['tasa_interes_ea'] = pd.to_numeric(df['tasa_interes_ea'], errors='coerce')
    print("Conversiones de tipo de datos completadas.")
    print("Información del DataFrame después de la conversión de tipos:")
    df.info()

    # Eliminar filas con NaT o NaN en columnas críticas para la visualización
    df.dropna(subset=['fecha_resolucion', 'tasa_interes_ea'], inplace=True)
    if df.empty:
        print("ADVERTENCIA: El DataFrame está vacío después de eliminar filas con datos nulos críticos. No hay datos para visualizar.")
        print("********** FIN (ADVERTENCIA) **********")
        sys.exit(0)

    # --- Paso 2: Crear Visualizaciones ---

    # Asegúrate de que los estilos de seaborn estén configurados para un mejor aspecto
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = 100 # Mejorar la resolución de las imágenes guardadas
    plt.rcParams['figure.figsize'] = (10, 6) # Tamaño por defecto para los gráficos

    print(f"\n--- Generando Visualización 1: Historial de Tasa de Interés Bancario Corriente (General) ---")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='fecha_resolucion', y='tasa_interes_ea')
    plt.title('Historial de Tasa de Interés Bancario Corriente (EA)')
    plt.xlabel('Fecha de Resolución')
    plt.ylabel('Tasa de Interés EA (%)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_image_path_1)
    print(f"Gráfico '{output_image_path_1}' guardado.")
    plt.close() # Cierra la figura para liberar memoria y evitar que se muestre automáticamente si no se desea

    print(f"\n--- Generando Visualización 2: Distribución de Tasas de Interés por Tipo de Crédito ---")
    plt.figure(figsize=(14, 7))
    sns.boxplot(data=df, x='tipo_credito_nombre', y='tasa_interes_ea')
    plt.title('Distribución de Tasas de Interés por Tipo de Crédito')
    plt.xlabel('Tipo de Crédito')
    plt.ylabel('Tasa de Interés EA (%)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(output_image_path_2)
    print(f"Gráfico '{output_image_path_2}' guardado.")
    plt.close()

    print(f"\n--- Generando Visualización 3: Top 5 Tasas Más Altas ---")
    top_5_general = df.nlargest(5, 'tasa_interes_ea')
    # Manejar caso de menos de 5 filas si se filtra mucho
    if len(top_5_general) == 0:
        print("ADVERTENCIA: No hay datos suficientes para generar el gráfico de Top 5 tasas.")
    else:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top_5_general, x='tasa_interes_ea', y='tipo_credito_nombre',
                    order=top_5_general.sort_values('tasa_interes_ea', ascending=False)['tipo_credito_nombre'])
        plt.title('Top 5 Tasas de Interés Bancario Corriente Más Altas Registradas')
        plt.xlabel('Tasa de Interés EA (%)')
        plt.ylabel('Tipo de Crédito')
        plt.tight_layout()
        plt.savefig(output_image_path_3)
        print(f"Gráfico '{output_image_path_3}' guardado.")
        plt.close()

except sqlite3.Error as e:
    print(f"ERROR de SQLite: No se pudo conectar a la base de datos o ejecutar la consulta. Detalles: {e}")
    print(f"Asegúrate de que la tabla '{TABLE_NAME}' existe en '{DATABASE_NAME}'.")
    print("********** FIN (FALLO SQLITE) **********")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print("ERROR: No se pudieron leer los datos del DataFrame. El archivo CSV podría estar vacío o corrupto.")
    print("********** FIN (FALLO DATAFRAME) **********")
    sys.exit(1)
except Exception as e:
    print(f"ERROR INESPERADO durante la visualización. Detalles: {e}")
    import traceback
    traceback.print_exc() # Imprime el rastreo completo del error
    print("********** FIN (FALLO GENÉRICO) **********")
    sys.exit(1)

print(f"\n********** FIN DE GENERACIÓN DE VISUALIZACIONES (EXITOSO) **********")

# Si deseas que los gráficos se muestren en ventanas emergentes DEPSUÉS de que se hayan guardado,
# descomenta la siguiente línea. Ten en cuenta que esto bloqueará la terminal hasta que cierres las ventanas.
# plt.show()