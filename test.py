# Librerías
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
import time
import re
from src.Fuji.get_data import get_datos_id
from src.Fuji.connection import connection

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")

busqueda = input('Ingresa una busqueda: ')

# Abrir navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Parámetros
url = "https://www.amazon.com/"
driver.get(url)

max_reintentos = 10

for intento in range(max_reintentos):
    try:
        wait = WebDriverWait(driver, 15)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.send_keys(busqueda)
        search_box.send_keys(Keys.RETURN)
        break
    except TimeoutException:
        print(f"No se encontró el campo de búsqueda. Recargando... (Intento {intento + 1})")
        driver.refresh()
        time.sleep(2)
else:
    print("No se pudo encontrar el campo después de varios intentos.")

# Rutas XPATH
titulo = './/h2'
precioWhole = './/span[contains(@class,"a-price-whole")]'
precioFraction = './/span[@class="a-price-fraction"]'
precio2 = ".//div[@class='a-section a-spacing-none a-spacing-top-mini']//div[@class='a-row a-size-base a-color-secondary']//span[@class='a-color-base']"
calificacion = (
    ".//div[@class='a-row a-size-small']//span//a//i//span | .//div[@class='a-icon-row']//a//i//span"
)
observacion = ".//div[@class='a-row a-spacing-micro']//span//a//span[@class='a-color-secondary']"
xpath_titulo = (
    ".//div[contains(@class, 's-title-instructions-style')]//h2//span"
    " | .//div[contains(@class, 's-title-instructions-style')]//h2"
    " | .//h2//span"
    " | .//h2"
)

def extraer_cantidad_paginas(driver):
    try:
        wait = WebDriverWait(driver, 10)
        paginas = driver.find_elements(By.XPATH,
                                       "//*[contains(@class,'s-pagination-item') and not(contains(@class,'dots'))]")

        num_paginas = [int(i.text) for i in paginas if i.text.isdigit()]

        total_pages = max(num_paginas, default=1)

        print("Total páginas:", total_pages)
        return total_pages
    except Exception as e:
        print(f"Error al extraer la cantidad de páginas: {e}")
        return 1


def extraer_nombre(item):
    try:
        nombre = item.find_element(By.XPATH, xpath_titulo).text
        nombre = nombre[:35]
    except:
        nombre = "N/A"
    return nombre

def extraer_precio(elemento):
    try:
        whole = elemento.find_element(By.XPATH, precioWhole).text.strip().replace(",", "")
        fraction = elemento.find_element(By.XPATH, precioFraction).text.strip()
        precio_actual = f"{whole}.{fraction}"
    except:
        try:
            precio_actual = elemento.find_element(By.XPATH, precio2).text.strip().split("$")[1]
            precio_actual = precio_actual.replace(",", "")
        except:
            precio_actual = "N/A"
    return precio_actual

def extraer_precio_full(elemento):
    try:
        precio_full = elemento.find_element(By.XPATH,
                                            ".//span[@class='a-price a-text-price']//span[@class='a-offscreen']")
        precio_full = precio_full.get_attribute("textContent").strip().split("$")[1]
        precio_full = precio_full.replace(",", "")
    except:
        precio_full = "N/A"
    return precio_full

def extraer_descuento(precio_full, precio_actual):
    try:
        precio_actual = float(precio_actual) if precio_actual != "N/A" else 0
        precio_full = float(precio_full) if precio_full != "N/A" else 0
        descuento = precio_full - precio_actual
        if descuento < 0:
            descuento = 0
    except:
        return "Error"
    return descuento

def extraer_calificacion(elemento):
    try:
        calificacion_elem = elemento.find_element(By.XPATH, calificacion)
        return calificacion_elem.get_attribute("textContent").strip().split(" ")[0]
    except:
        return "N/A"

def es_patrocinado(elemento):
    try:
        elemento.find_element(By.XPATH, ".//span[contains(text(),'Patrocinado') or contains(text(),'Sponsored')]")
        return "Patrocinado"
    except:
        try:
            ancestor = elemento.find_element(By.XPATH, ".//ancestor::div[contains(@class,'AdHolder')]")
            return "Patrocinado"
        except:
            try:
                badge = elemento.find_element(By.XPATH, ".//*[contains(text(),'Sponsored') or contains(text(),'Patrocinado')]")
                return "Patrocinado"
            except:
                return "General"

def extraer_todos_los_carruseles(driver):
    productos_carrusel = []
    carruseles = driver.find_elements(By.XPATH, '//div[contains(@class,"a-carousel-viewport")]//ancestor::div[contains(@class,"a-carousel")]')
    for carrusel in carruseles:
        try:
            carrusel.find_element(By.XPATH, ".//*[contains(text(),'Sponsored') or contains(text(),'Patrocinado')]")
            es_patro = "Patrocinado"
        except:
            es_patro = "Patrocinado" if "AdHolder" in carrusel.get_attribute("class") else "General"

        while True:
            try:
                siguiente = carrusel.find_element(By.XPATH, './/li[contains(@class, "a-carousel-card") and contains(@aria-hidden, "true")]')
                flecha = carrusel.find_element(By.XPATH, './/a[contains(@class, "a-carousel-goto-nextpage")]')
                if "a-disabled" in flecha.get_attribute("class"):
                    break
                driver.execute_script("arguments[0].click();", flecha)
                time.sleep(1.5)
            except:
                break

        items = carrusel.find_elements(By.XPATH, './/li[contains(@class,"a-carousel-card")]')
        for i in items:
            i.set_attribute = lambda k, v: None
            i.observacion_personalizada = es_patro
        productos_carrusel.extend(items)
    return productos_carrusel

datos = []

while True:
    wait.until(EC.presence_of_element_located((By.XPATH, './/div[contains(@class,"s-card-container")]')))
    main_products = driver.find_elements(By.XPATH, './/div[contains(@class,"s-card-container")]')
    carousel_products = extraer_todos_los_carruseles(driver)
    all_products = main_products + carousel_products

    for prod in all_products:
        obs = getattr(prod, 'observacion_personalizada', es_patrocinado(prod))
        info = {
            "titulo": extraer_nombre(prod),
            "precio_actual": extraer_precio(prod),
            "precio_full": extraer_precio_full(prod),
            "descuento": extraer_descuento(extraer_precio_full(prod), extraer_precio(prod)),
            "calificación": extraer_calificacion(prod),
            "observación": obs
        }
        datos.append(info)

    print("Página procesada")
    try:
        next_page = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                           '//a[contains(@class, "s-pagination-next") and not(contains(@class, "s-pagination-disabled"))]')))
        driver.execute_script("arguments[0].click();", next_page)
    except:
        print("No hay más páginas.")
        break

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




def guardar_dataframe_en_excel_por_paginas(df, total_paginas, nombre_archivo='productos_amazon.xlsx'):
    
    if df.empty:
        print("⚠️ El DataFrame está vacío. No se generó el archivo.")
        return

    partes = np.array_split(df, total_paginas)
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        for i, parte in enumerate(partes):
            parte.to_excel(writer, sheet_name=f'Página_{i+1}', index=False)

    print(f"✅ Archivo guardado correctamente en '{nombre_archivo}' con {total_paginas} hojas.")


guardar_dataframe_en_excel_por_paginas(df, extraer_cantidad_paginas(driver))


data = get_datos_id('1')

print(data)
