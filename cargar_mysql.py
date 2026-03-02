import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

def seleccionar_archivo_limpio():
    carpeta = "salida"
    if not os.path.exists(carpeta):
        print(f"❌ No existe la carpeta '{carpeta}'. Ejecuta primero el limpiador.")
        return None
    
    archivos = [f for f in os.listdir(carpeta) if f.endswith(('.xlsx', '.xls', '.csv'))]
    
    if not archivos:
        print(f"⚠️ No hay archivos limpios en '{carpeta}'.")
        return None
    
    print(f"\n📥 Archivos disponibles para cargar a MySQL:")
    for i, f in enumerate(archivos, 1):
        print(f"{i}. {f}")
    
    try:
        opc = int(input("\nSelecciona el número del archivo: "))
        if 1 <= opc <= len(archivos):
            return os.path.join(carpeta, archivos[opc-1])
        else:
            print("❌ Número fuera de rango.")
            return None
    except ValueError:
        print("❌ Debes ingresar un número.")
        return None

def cargar_a_mysql():
    print("=== CARGADOR DE DATOS LIMPIOS A MYSQL ===\n")
    
    # Seleccionar archivo
    ruta = seleccionar_archivo_limpio()
    if ruta is None:
        return
    
    # Cargar archivo
    print(f"\n✅ Archivo seleccionado: {ruta}")
    if ruta.endswith('.csv'):
        df = pd.read_csv(ruta)
    else:
        df = pd.read_excel(ruta)
    
    print(f"📊 Registros a cargar: {len(df)}")
    print(f"📋 Columnas: {list(df.columns)}")
    print("\n🔍 Previsualización:")
    print(df.head(5).to_string())
    
    if input("\n¿Confirmas que los datos están correctos? (s/n): ").lower() != 's':
        print("🚫 Carga cancelada por el usuario.")
        return
    
    # Credenciales MySQL
    print("\n--- CONEXIÓN A MYSQL ---")
    host = input("Host (Enter para localhost): ") or "localhost"
    user = input("Usuario: ")
    password = quote_plus(input("Contraseña: "))
    database = input("Base de datos: ")
    tabla = input("Nombre de la tabla destino: ")
    
    # Opciones de carga
    print("\n¿Qué hacer si la tabla ya existe?")
    print("1. Reemplazar tabla completa")
    print("2. Agregar registros al final")
    print("3. Cancelar si existe")
    
    while True:
        opcion = input("Opción: ")
        if opcion in ['1', '2', '3']: break
        print("❌ Elige solo 1, 2 o 3.")
    
    if_exists = {'1': 'replace', '2': 'append', '3': 'fail'}[opcion]
    
    # Cargar a MySQL
    try:
        engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
        
        print(f"\n⏳ Cargando {len(df)} registros a MySQL...")
        df.to_sql(tabla, engine, if_exists=if_exists, index=False)
        
        print(f"✅ {len(df)} registros cargados exitosamente!")
        print(f"   Base de datos: {database}")
        print(f"   Tabla: {tabla}")
        
        # Verificar carga
        df_verificacion = pd.read_sql(f"SELECT COUNT(*) as Total FROM {tabla}", engine)
        print(f"   Total en MySQL: {df_verificacion['Total'].values[0]} registros")
        
        engine.dispose()
        
        # Log de carga
        from datetime import datetime
        log_name = os.path.join("salida", f"LOG_CARGA_MYSQL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_name, 'w', encoding='utf-8') as f:
            f.write("=== LOG DE CARGA A MYSQL ===\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivo origen: {ruta}\n")
            f.write(f"Base de datos: {database}\n")
            f.write(f"Tabla: {tabla}\n")
            f.write(f"Registros cargados: {len(df)}\n")
            f.write(f"Modo: {if_exists}\n")
        
        print(f"📄 Log de carga creado: {log_name}")
        
    except Exception as e:
        print(f"❌ Error al cargar a MySQL: {e}")

if __name__ == "__main__":
    cargar_a_mysql()

'''
**El flujo ahora queda así:**
```
1. Ejecutas clean.py → genera Excel/CSV limpio + log auditoría
2. Analista revisa ambos archivos
3. Si aprueba ejecutas cargar_mysql.py → carga a MySQL + log de carga
'''