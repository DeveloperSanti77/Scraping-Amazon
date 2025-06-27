import numpy as np
import pandas as pd


def guardar_limpiar_dataframe(datos):
    # Guardar en Excel
    df = pd.DataFrame(datos)

    # limpieza de datos
    df["precio_actual"] = df["precio_actual"].replace("N/A", "0")
    df["precio_actual"] = pd.to_numeric(df["precio_actual"], errors="coerce")
    df["precio_actual"] = np.where(
        (df["precio_actual"] % 1) >= 0.5,
        np.ceil(df["precio_actual"]),
        np.floor(df["precio_actual"])
    )

    df["precio_full"] = pd.to_numeric(df["precio_full"], errors="coerce")
    df["precio_full"] = df["precio_full"].fillna(df["precio_actual"])

    df = df.sort_values(by="precio_actual", ascending=False)

    df = df[df['titulo'].str.contains('portátil|laptop', case=False, na=False)]
    df = df[~df['titulo'].str.contains('cargador', case=False, na=False)]
    return df

def guardar_dataframe_en_excel_por_paginas(df, total_paginas, nombre_archivo='productos_amazon.xlsx'):
    
    if df.empty:
        print("⚠️ El DataFrame está vacío. No se generó el archivo.")
        return

    partes = np.array_split(df, total_paginas)
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        for i, parte in enumerate(partes):
            parte.to_excel(writer, sheet_name=f'Página_{i+1}', index=False)

    print(f"✅ Archivo guardado correctamente en '{nombre_archivo}' con {total_paginas} hojas.")
    
    return df


#guardar_dataframe_en_excel_por_paginas(df, extraer_cantidad_paginas(driver))