import pandas as pd
import requests
import io
import sqlite3 # Importa el módulo sqlite3 para la base de datos



def extract_data(url: str) -> pd.DataFrame:
        """
        Extrae datos de un archivo CSV desde una URL específica.

        Args:
            url (str): La URL del archivo CSV.

        Returns:
            pd.DataFrame: Un DataFrame de Pandas con los datos extraídos.
                          Retorna un DataFrame vacío si ocurre un error.
        """
        print(f"Iniciando la extracción de datos desde: {url}")
        try:
            # Realiza una petición HTTP GET para obtener el contenido del CSV
            response = requests.get(url)
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)

            # Usa io.StringIO para tratar el contenido de la respuesta como un archivo
            # y pd.read_csv para leerlo directamente en un DataFrame
            df = pd.read_csv(io.StringIO(response.text))
            print("Datos extraídos exitosamente.")
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error al extraer los datos desde la URL: {e}")
            return pd.DataFrame() # Retorna un DataFrame vacío en caso de error
        except pd.errors.EmptyDataError:
            print("El archivo CSV está vacío o no contiene datos.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la extracción: {e}")
            return pd.DataFrame()

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforma el DataFrame de datos de TIBC:
        - Renombra columnas para facilitar su uso.
        - Convierte 'FECHA_RESOLUCION' y 'VIGENCIA_DESDE'/'VIGENCIA_HASTA' a tipo datetime.
        - Convierte 'INTERES_BANCARIO_CORRIENTE' a tipo numérico.

        Args:
            df (pd.DataFrame): DataFrame original con los datos extraídos.

        Returns:
            pd.DataFrame: DataFrame con los datos transformados.
                          Retorna un DataFrame vacío si el input es vacío o inválido.
        """
        print("Iniciando la transformación de datos...")
        if df.empty:
            print("El DataFrame de entrada para la transformación está vacío. Saltando transformación.")
            return pd.DataFrame()

        # 1. Renombrar columnas
        # Ajustamos los nombres de columna a los que vimos en tu salida real
        column_mapping = {
            'RESOLUCION': 'resolucion_id',
            'FECHA_RESOLUCION': 'fecha_resolucion',
            'VIGENCIA_DESDE': 'vigencia_desde',
            'VIGENCIA_HASTA': 'vigencia_hasta',
            'INTERES_BANCARIO_CORRIENTE': 'tasa_interes_ea',
            'MODALIDAD': 'tipo_credito_nombre'
        }
        df_transformed = df.rename(columns=column_mapping)
        print("Columnas renombradas.")

        # 2. Convertir tipos de datos

        # Convertir 'fecha_resolucion' a formato datetime (ej. '22/12/2014' -> %d/%m/%Y)
        try:
            df_transformed['fecha_resolucion'] = pd.to_datetime(df_transformed['fecha_resolucion'], format='%d/%m/%Y')
            print("Columna 'fecha_resolucion' convertida a datetime.")
        except Exception as e:
            print(f"Error al convertir 'fecha_resolucion' a datetime: {e}. Se mantiene como object.")

        # Intentar convertir 'vigencia_desde' y 'vigencia_hasta' a formato datetime
        # Usamos errors='coerce' para que los valores que no puedan convertirse se conviertan en NaT (Not a Time)
        # Esto es más robusto si hay inconsistencias en los datos.
        try:
            df_transformed['vigencia_desde'] = pd.to_datetime(df_transformed['vigencia_desde'], errors='coerce', format='%d/%m/%Y')
            print("Columna 'vigencia_desde' convertida a datetime (valores inválidos a NaT).")
        except Exception:
            print("No se pudo convertir 'vigencia_desde' a datetime. Se mantiene como está.")

        try:
            df_transformed['vigencia_hasta'] = pd.to_datetime(df_transformed['vigencia_hasta'], errors='coerce', format='%d/%m/%Y')
            print("Columna 'vigencia_hasta' convertida a datetime (valores inválidos a NaT).")
        except Exception:
            print("No se pudo convertir 'vigencia_hasta' a datetime. Se mantiene como está.")

        # Convertir 'tasa_interes_ea' a numérico (float)
        # Los datos pueden venir con '%' y el punto como separador decimal.
        try:
            df_transformed['tasa_interes_ea'] = df_transformed['tasa_interes_ea'].astype(str).str.replace('%', '', regex=False)
            df_transformed['tasa_interes_ea'] = pd.to_numeric(df_transformed['tasa_interes_ea'], errors='coerce')
            print("Columna 'tasa_interes_ea' convertida a numérico (sin '%').")
        except Exception as e:
            print(f"Error al convertir 'tasa_interes_ea' a numérico: {e}. Se mantiene como está.")


        # 3. Manejo de valores faltantes (NaT para fechas, NaN para números)
        # Informamos si se encuentran valores nulos después de las conversiones
        if df_transformed.isnull().sum().any():
            print("\n¡Advertencia! Se encontraron valores nulos después de la transformación:")
            print(df_transformed.isnull().sum())
        else:
            print("\nNo se encontraron valores nulos después de la transformación.")

        print("Transformación de datos completada.")
        return df_transformed

def load_data(df: pd.DataFrame, db_name: str, table_name: str):
        """
        Carga el DataFrame transformado en una tabla de una base de datos SQLite.

        Args:
            df (pd.DataFrame): DataFrame con los datos a cargar.
            db_name (str): Nombre del archivo de la base de datos SQLite (ej. 'tibc_db.db').
            table_name (str): Nombre de la tabla donde se cargarán los datos (ej. 'tasas_interes').
        """
        print(f"Iniciando la carga de datos en la base de datos '{db_name}', tabla '{table_name}'...")
        if df.empty:
            print("El DataFrame de entrada para la carga está vacío. No se cargará nada.")
            return

        conn = None # Inicializa conn para asegurar que siempre esté definida
        try:
            # Establece una conexión a la base de datos SQLite
            conn = sqlite3.connect(db_name)
            print(f"Conexión a la base de datos '{db_name}' establecida.")

            # Usa el método to_sql de Pandas para escribir el DataFrame en una tabla SQL
            # if_exists='replace': Si la tabla ya existe, la reemplaza (útil para pruebas).
            #                      Otras opciones: 'append' (añade filas), 'fail' (lanza error).
            # index=False: No escribe el índice del DataFrame como una columna en la tabla.
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Datos cargados exitosamente en la tabla '{table_name}'.")

        except sqlite3.Error as e:
            print(f"Error de SQLite al cargar los datos: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la carga de datos: {e}")
        finally:
            # Cierra la conexión a la base de datos
            if conn: # Verifica si la conexión fue exitosa antes de intentar cerrarla
                conn.close()
                print("Conexión a la base de datos cerrada.")


if __name__ == "__main__":
        print("********** INICIO DE EJECUCIÓN DEL SCRIPT **********")
        csv_url = "https://www.datos.gov.co/api/views/pare-7x5i/rows.csv?accessType=DOWNLOAD"

        print("\n--- INICIO DEL PROCESO ETL ---")

        # Paso de Extracción
        print("\n--- Ejecutando Paso: EXTRACCIÓN ---")
        df_raw = extract_data(csv_url)

        if not df_raw.empty:
            print("\n--- Extracción COMPLETADA. Mostrando datos extraídos ---")
            print("\nPrimeras 5 filas de los datos extraídos:")
            print(df_raw.head().to_string())
            print(f"\nNúmero de filas y columnas: {df_raw.shape}")
            print("\nInformación general del DataFrame (antes de transformar):")
            df_raw.info()

            # Paso de Transformación
            print("\n--- Ejecutando Paso: TRANSFORMACIÓN ---")
            df_transformed = transform_data(df_raw)

            if not df_transformed.empty:
                print("\n--- Transformación COMPLETADA. Mostrando datos transformados ---")
                print("\nPrimeras 5 filas de los datos transformados:")
                print(df_transformed.head().to_string())
                print(f"\nNúmero de filas y columnas del DataFrame transformado: {df_transformed.shape}")
                print("\nInformación general del DataFrame transformado:")
                df_transformed.info()
                print("\n--- PROCESO ETL COMPLETADO EXITOSAMENTE ---")

                # --- INICIO DEL NUEVO CÓDIGO DE CARGA ---
                print("\n--- Ejecutando Paso: CARGA ---")
                db_filename = "tibc_data.db" # Nombre del archivo de la base de datos
                table_name = "tasas_interes_bancario" # Nombre de la tabla en la DB
                load_data(df_transformed, db_filename, table_name)
                print("\n--- Carga COMPLETADA ---")
                # --- FIN DEL NUEVO CÓDIGO DE CARGA ---

            else:
                print("El DataFrame transformado está vacío. No se puede continuar con la carga.")
        else:
            print("No se pudieron extraer los datos o el DataFrame está vacío. No se puede continuar con la transformación.")
        print("\n--- FIN DEL PROCESO ETL ---")
        print("********** FIN DE EJECUCIÓN DEL SCRIPT **********")

