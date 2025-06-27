from src.Fuji.connection import connection


def guardar_datos_en_sql(df, nombre_tabla):
    conn = connection()
    if conn:
        cursor = conn.cursor()
    else:
        print("No se pudo establecer conexión a la base de datos.")
        return
    
    for index, row in df.iterrows():
        # Extraer los valores de cada columna
        try:
            nombre = str(row['titulo'])
        except:
            nombre = None
        
        try:
            calificacion = str(row['calificacion'])
        except:
            calificacion = None
        
        try:
            precio_anterior = str(row['precio_full'])
        except:
            precio_anterior = None
        
        try:
            precio_actual = str(row['precio_actual'])
        except:
            precio_actual = None
        
        try:
            observacion = str(row['observacion'])
        except:
            observacion = None
        
        try:
            descuento = str(row['descuento'])
        except:
            descuento = None

        try:
            cursor.execute(f"""
                INSERT INTO {nombre_tabla} (nombre, precio_anterior, precio_actual, calificacion, observacion, descuento)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            nombre,
            precio_anterior,
            precio_actual,
            calificacion,
            observacion,
            descuento
            )
        except Exception as e:
            print(f"⚠️ Error en fila {index}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Datos insertados correctamente en la tabla SQL Server.")