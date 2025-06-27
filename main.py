from src.AmazonScraping import iniciar_scraping, extraer_productos, extraer_cantidad_paginas, extraer_resultados_busqueda
from src.ExcelManager import guardar_limpiar_dataframe, guardar_dataframe_en_excel_por_paginas
from src.Fuji.get_data import get_datos_id
from src.SqlManager import guardar_datos_en_sql
from src.EmailManager import preparar_correo, enviar_correo
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))



data = get_datos_id('1')

def main():
    print("🔍 Iniciando scraping...")
    driver, wait = iniciar_scraping()
    total_resultados = extraer_resultados_busqueda(driver)
    datos = extraer_productos(driver, wait)
    total_paginas = extraer_cantidad_paginas(driver)
    print(f"Total de resultados: {total_resultados}")
    print(f"✅ Scraping finalizado. Productos extraídos: {len(datos)}")

    print("💾 Procesando y guardando en Excel...")
    df = guardar_limpiar_dataframe(datos)
    guardar_dataframe_en_excel_por_paginas(df, total_paginas)

    print("📦 Guardando en SQL...")
    guardar_datos_en_sql(df, "tabla_faiber")

    #print("📨 Enviando correo...")
    #smtp_info, destinatarios, asunto, cuerpo, ruta_excel = preparar_correo()
    #if smtp_info:
    #    enviar_correo(smtp_info, destinatarios, asunto, cuerpo, ruta_excel)
    #else:
    #    print("Proceso de envío de correo cancelado por falta de credenciales")

if __name__ == "__main__":
    main()
