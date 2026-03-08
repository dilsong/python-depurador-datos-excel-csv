import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime


# Configuración visual
warnings.filterwarnings('ignore', category=FutureWarning)
sns.set_theme(style="whitegrid")
# NUEVA FUNCIÓN PARA EL LOG ---
def generar_log_txt(nombre_archivo, reg_ini, reg_fin, historial_cambios):
    if not os.path.exists("salida"): os.makedirs("salida")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_log = os.path.join("salida", f"AUDITORIA_{nombre_archivo}_{timestamp}.txt")
    
    with open(nombre_log, "w", encoding="utf-8") as f:
        f.write(f"=== REPORTE DE AUDITORÍA LOGÍSTICA ===\n")
        f.write(f"Archivo procesado: {nombre_archivo}\n")
        f.write(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Registros Iniciales: {reg_ini}\n")
        f.write(f"Registros Finales: {reg_fin}\n")
        f.write("-" * 40 + "\n")
        f.write("DETALLE DE HALLAZGOS POR COLUMNA:\n")
        for log in historial_cambios:
            f.write(f"• {log}\n")
    return nombre_log

def generar_reporte_visual_v17(df_final, matriz_errores, registros_ini, registros_fin, historial_errores):
    print("\n📊 GENERANDO TABLERO DE AUDITORÍA...")
    try:
        fig, axes = plt.subplots(1, 3, figsize=(22, 6))
        fig.suptitle('🔍 REPORTE DE TRANSCRIPCIÓN Y CONFLICTOS', fontsize=18, fontweight='bold')
        
        # 1. Mapa de calor
        sns.heatmap(matriz_errores, yticklabels=False, cbar=True, cmap='YlOrRd', ax=axes[0])
        axes[0].set_title('Mapa de Calor de Errores', fontsize=14)

        # 2. Volumen de datos
        datos_vol = pd.DataFrame({'Fase': ['Entrada', 'Salida'], 'Registros': [registros_ini, registros_fin]})
        sns.barplot(x='Fase', y='Registros', data=datos_vol, palette='Blues_d', ax=axes[1])
        axes[1].set_title('Volumen de Datos', fontsize=14)

        # 3. Top Errores
        if historial_errores:
            err_df = pd.DataFrame(list(historial_errores.items()), columns=['Columna', 'Errores'])
            err_df = err_df[err_df['Errores'] > 0].sort_values(by='Errores', ascending=False).head(5)
            if not err_df.empty:
                sns.barplot(x='Errores', y='Columna', data=err_df, palette='Reds_r', ax=axes[2])
                axes[2].set_title('Top Errores por Columna', fontsize=14)
        
        plt.tight_layout()
        plt.show() # En VS Code esto abrirá una ventana nueva con los gráficos
    except Exception as e: 
        print(f"⚠️ Gráfico no disponible: {e}")

# --- CONFIGURACIÓN DE CARPETAS ---
CARPETA_DATOS = "entradas"  # Puedes ponerle el nombre que quieras

def seleccionar_archivo_de_carpeta():
    # 1. Crear la carpeta si no existe para que no de error
    if not os.path.exists(CARPETA_DATOS):
        os.makedirs(CARPETA_DATOS)
        print(f"📁 Se ha creado la carpeta '{CARPETA_DATOS}'.")
        print(f"👉 Por favor, mete tus archivos Excel/CSV ahí y vuelve a ejecutar.")
        return None

    # 2. Listar archivos dentro de esa carpeta específica
    archivos = [f for f in os.listdir(CARPETA_DATOS) if f.endswith(('.xlsx', '.xls', '.csv'))]
    
    if not archivos:
        print(f"⚠️ La carpeta '{CARPETA_DATOS}' está vacía.")
        print(f"📍 Ruta completa: {os.path.abspath(CARPETA_DATOS)}")
        return None

    print(f"\n📥 Archivos listos para depurar en '{CARPETA_DATOS}':")
    for i, f in enumerate(archivos, 1):
        print(f"{i}. {f}")
    
    try:
        opc = int(input("\nSelecciona el número del archivo: "))
        if 1 <= opc <= len(archivos):
            # IMPORTANTE: Unimos el nombre de la carpeta con el nombre del archivo
            return os.path.join(CARPETA_DATOS, archivos[opc-1])
        else:
            print("❌ Número fuera de rango.")
            return None
    except ValueError:
        print("❌ Debes ingresar un número.")
        return None
def depurador_violento_v17_vscode():
    # --- SELECCIÓN DE ARCHIVO LOCAL EN CARPETA ESPECÍFICA ---
    df = None          
    matriz_errores = None 
    ruta_archivo = seleccionar_archivo_de_carpeta()

    if ruta_archivo is None:
        print("🚫 Operación cancelada: No se seleccionó ningún archivo.")
        return
    else:
        nombre_base = os.path.basename(ruta_archivo)
        print(f"✅ Procesando: {ruta_archivo}")
        # Cargar según la extensión
        if ruta_archivo.endswith('.csv'):
            df = pd.read_csv(ruta_archivo)
        else:
            df = pd.read_excel(ruta_archivo)   
    # --- LÓGICA DE DEPURACIÓN ---
    matriz_errores = pd.DataFrame(0, index=df.index, columns=df.columns)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.replace('', np.nan, inplace=True)

    registros_iniciales = len(df)
    detalles_auditoria = []
    historial_errores = {col: 0 for col in df.columns}    

    if "Robot_ms" not in df.columns:
        df["Robot_ms"] = np.nan

    # Actualizar historial_errores para incluir Robot_ms
    historial_errores = {col: 0 for col in df.columns}
    
    
    # Auditoría inicial de nulos + registro en Robot_ms
    for col in df.columns:
        if col == "Robot_ms": continue
        nulos = df[col].isna().sum()
        if nulos > 0:
            detalles_auditoria.append(f"Columna [{col}]: Encontrados {nulos} valores nulos.")
            matriz_errores[df[col].isna()] = 1
            historial_errores[col] += nulos
            
            # Registrar en Robot_ms qué campo estaba vacío
            mask_nulos = df[col].isna()
            df.loc[mask_nulos, "Robot_ms"] = df.loc[mask_nulos, "Robot_ms"].fillna('') + f"[{col}:VACIO] "  
    # fin de auditoría de nulos

    matriz_errores[df.isna()] = 1
    for col in df.columns: 
        if col == "Robot_ms": continue
        historial_errores[col] += df[col].isna().sum()

    df = df.dropna(how='all')
    matriz_errores = matriz_errores.loc[df.index]

    # hallar duplicados
    # Detección inteligente de duplicados
    print("\n--- DETECCIÓN DE DUPLICADOS ---")

    # Preguntar campo clave al inicio
    col_clave_usuario = None
    if input("¿Tienes un campo clave único para validar duplicados? (s/n): ").lower() == 's':
        while True:
            print(f"Columnas disponibles: {list(df.columns)}")
            col_clave_usuario = input("Nombre exacto del campo clave: ")
            if col_clave_usuario in df.columns:
                break
            print(f"❌ '{col_clave_usuario}' no existe. Disponibles: {list(df.columns)}")

    # Duplicados exactos
    dup_exactos = df.duplicated().sum()
    print(f"\nDuplicados exactos encontrados: {dup_exactos}")
    if dup_exactos > 0:
        print("\nMostrando primeros duplicados exactos:")
        print(df[df.duplicated(keep=False)].head(10).to_string())
        if input(f"\n¿Eliminar {dup_exactos} duplicados conservando uno? (s/n): ").lower() == 's':
            df = df.drop_duplicates()
            df = df.reset_index(drop=True)
            matriz_errores = matriz_errores.loc[df.index].reset_index(drop=True)
            detalles_auditoria.append(f"Eliminados {dup_exactos} duplicados exactos.")
            print(f"✅ {dup_exactos} duplicados eliminados.")

    # Duplicados por campo clave
    if col_clave_usuario:
        cols_validar = [col_clave_usuario]
    else:
        cols_validar = [col for col in df.columns if 'id' in col.lower() or
                    'codigo' in col.lower() or 'code' in col.lower()]
        if cols_validar:
            print(f"\nColumnas ID detectadas automáticamente: {cols_validar}")

    for col_id in cols_validar:
        dup_id = df.duplicated(subset=[col_id], keep=False).sum()
        if dup_id > 0:
            print(f"\n⚠️ {dup_id} registros con [{col_id}] duplicado:")
            print(df[df.duplicated(subset=[col_id], keep=False)][[col_id]].value_counts().head(10).to_string())
            print("\nDetalle de registros duplicados:")
            print(df[df.duplicated(subset=[col_id], keep=False)].head(10).to_string())
            if input(f"\n¿Eliminar duplicados por [{col_id}] conservando el primero? (s/n): ").lower() == 's':
                antes = len(df)
                df = df.drop_duplicates(subset=[col_id], keep='first')
                df = df.reset_index(drop=True)
                matriz_errores = matriz_errores.loc[df.index].reset_index(drop=True)
                eliminados = antes - len(df)
                detalles_auditoria.append(f"Eliminados {eliminados} duplicados por [{col_id}].")
                print(f"✅ {eliminados} duplicados eliminados por [{col_id}].")
        else:
            print(f"✅ No hay duplicados por [{col_id}].")
        # fin de detec``ción de duplicados

    for col in df.columns:
        if col == "Robot_ms": continue
        while True: 
            print(f"\n--- COLUMNA: [{col}] ---")
            print("1. Texto | 2. Numérico | 3. Fecha | 4. Omitir")
            sel = input("Opción: ")
            if sel in ['1', '2', '3', '4']: break
            print("❌ Elige solo 1, 2, 3 o 4.")
        
        if sel == '1':
            while True:
                fmt = input("Formato: 1. MAYÚS | 2. minús | 3. Título: ")
                if fmt in ['1', '2', '3']: break
                print("❌ Elige solo 1, 2 o 3.")

            df[col] = df[col].astype(str).replace('nan', np.nan)
            if fmt == '1': df[col] = df[col].str.upper()
            elif fmt == '2': df[col] = df[col].str.lower()
            else: df[col] = df[col].str.title()

            if input("¿Corregir por Código relacionado? (s/n): ").lower() == 's':
                while True: # VALIDACIÓN DE COLUMNA EXISTENTE
                    col_cod = input("Nombre exacto de columna CÓDIGO: ")
                    if col_cod in df.columns:
                        mapeo = df.groupby(col_cod)[col].apply(lambda x: x.mode()[0] if not x.mode().empty else np.nan).to_dict()
                        df[col] = df[col_cod].map(mapeo)
                        detalles_auditoria.append(f"Columna [{col}]: Homogeneizada usando códigos de [{col_cod}].")
                        break
                    else:
                        print(f"❌ '{col_cod}' no existe. Disponibles: {list(df.columns)}")
                        if input("¿Cancelar (s/n)?: ").lower() == 's': break

        elif sel == '2':
            antes_num = df[col].copy()
            while True:
                tipo_n = input("Tipo numérico: 1. Entero | 2. Decimal: ")
                if tipo_n in ['1', '2']: break
                print("❌ Elige solo 1 o 2.")
            
            # Reset para alinear índices
            df = df.reset_index(drop=True)
            matriz_errores = matriz_errores.reset_index(drop=True)
            antes_num = antes_num.reset_index(drop=True)
            
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(r'[^\d.]', '', regex=True)
            mask_err = antes_num.astype(str).str.contains(r'[a-zA-Z$]', regex=True, na=False)
            
            if mask_err.any():
                detalles_auditoria.append(f"Columna [{col}]: Limpiados {mask_err.sum()} registros con caracteres no numéricos.")
                for idx in df[mask_err].index:
                    matriz_errores.at[idx, col] = 1
                    historial_errores[col] += 1

            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df[col] = df[col].astype(int) if tipo_n == '1' else df[col].astype(float).round(2)

        elif sel == '3':
            if "Robot_ms" not in df.columns: df["Robot_ms"] = np.nan
            
            print("¿Cuál es el formato de fecha?")
            print("1. DD/MM/YYYY (Latinoamérica/Europa)")
            print("2. MM/DD/YYYY (Estados Unidos)")
            print("3. YYYY-MM-DD (ISO/Americano moderno)")
            print("4. Autodetectar")
            while True:
                f_date = input("Opción: ")
                if f_date in ['1', '2', '3', '4']: break
                print("❌ Elige solo 1, 2, 3 o 4.")
            
            # Reset completo de todos los objetos
            df = df.reset_index(drop=True)
            matriz_errores = matriz_errores.reset_index(drop=True)
            
            foto_original = df[col].copy().astype(str)
            if f_date == '1':
                df_f = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
            elif f_date == '2':
                df_f = pd.to_datetime(df[col], dayfirst=False, errors='coerce')
            elif f_date == '3':
                df_f = pd.to_datetime(df[col], format='%Y-%m-%d', errors='coerce')
            else:
                df_f = pd.to_datetime(df[col], infer_datetime_format=True, errors='coerce')
            mask_f = df_f.isna() & df[col].notna()

            if mask_f.any():
                detalles_auditoria.append(f"Columna [{col}]: {mask_f.sum()} fechas inválidas movidas a Robot_ms.")
                for idx in df[mask_f].index:
                    df.at[idx, "Robot_ms"] = foto_original[idx]
                    matriz_errores.at[idx, col] = 1
                    historial_errores[col] += 1

            df[col] = df_f

    # Reporte
    generar_reporte_visual_v17(df, matriz_errores, registros_iniciales, len(df), historial_errores)
    print("\n✅ Previsualización (Primeros 10 registros):")
    print(df.head(10).to_string())

    if input("\n¿Guardar archivo depurado? (s/n): ").lower() == 's':
        nom = input("Nombre del nuevo archivo: ")
        while True:
            ext = input("1. Excel | 2. CSV: ")
            if ext in ['1', '2']: break
            print("❌ Elige solo 1 o 2.")

        final_name = f"{nom}.xlsx" if ext == '1' else f"{nom}.csv"

        if ext == '1': df.to_excel(final_name, index=False)
        else: df.to_csv(final_name, index=False)
        if not os.path.exists("salida"): os.makedirs("salida")
        ruta_final = os.path.join("salida", final_name)
        os.rename(final_name, ruta_final)
        
        # Generar el archivo TXT
        ruta_log = generar_log_txt(nombre_base, registros_iniciales, len(df), detalles_auditoria)
        
        print(f"💾 Archivo guardado como: {os.path.abspath(final_name)}")
        print(f"📄 Log de auditoría creado: {os.path.abspath(ruta_log)}")


if __name__ == "__main__":
    depurador_violento_v17_vscode()