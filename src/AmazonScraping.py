# Librerías
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")


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

def iniciar_scraping():
    busqueda = input('Ingresa una busqueda: ')
    # Abrir navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://www.amazon.com/"
    driver.get(url)


    #Recargar pagína si no es valida
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
    return driver, wait

def extraer_resultados_busqueda(driver):
    try:
        # Extraigo el texto de la página de resultados de búsqueda
        result_text = driver.find_element(By.XPATH, "//span[contains(text(),'resultados para')]").text
        print("Texto extraído:", result_text)

        # Convertimos el texto extraído a un número
        match = re.search(r'(\d+)\s+a\s+(\d+)', result_text)
        if match:
            numero_deseado = int(match.group(2))
            print(result_text)
        else:
            numero_deseado = 0
        return numero_deseado
    except Exception as e:
        print(f"Error al extraer resultados de búsqueda: {e}")
        return 0

def extraer_cantidad_paginas(driver):
    try:
        paginas = driver.find_elements(By.XPATH, "//*[contains(@class,'s-pagination-item') and not(contains(@class,'dots'))]")

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

def extraer_precio(item):
    try:
        whole = item.find_element(By.XPATH, precioWhole).text.strip().replace(",", "")
        fraction = item.find_element(By.XPATH, precioFraction).text.strip()
        precio_actual = f"{whole}.{fraction}"
    except:
        try:
            precio_actual = item.find_element(By.XPATH, precio2).text.strip().split("$")[1]
            precio_actual = precio_actual.replace(",", "")
        except:
            precio_actual = "N/A"
    return precio_actual

def extraer_precio_full(item):
    try:
        precio_full = item.find_element(By.XPATH,
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

def extraer_calificacion(item):
    try:
        calificacion_elem = item.find_element(By.XPATH, calificacion)
        return calificacion_elem.get_attribute("textContent").strip().split(" ")[0]
    except:
        return "N/A"

def es_patrocinado(item):
    try:
        item.find_element(By.XPATH, ".//span[contains(text(),'Patrocinado') or contains(text(),'Sponsored')]")
        return "Patrocinado"
    except:
        try:
            ancestor = item.find_element(By.XPATH, ".//ancestor::div[contains(@class,'AdHolder')]")
            return "Patrocinado"
        except:
            try:
                badge = item.find_element(By.XPATH, ".//*[contains(text(),'Sponsored') or contains(text(),'Patrocinado')]")
                return "Patrocinado"
            except:
                return "General"

def extraer_todos_los_carruseles(driver):
    productos_carrusel = []
    carruseles = driver.find_elements(By.XPATH, '//div[contains(@class,"a-carousel-viewport")]//ancestor::div[contains(@class,"a-carousel")]')
    
    for carrusel in carruseles:
        # Desplazar todo el carrusel (si aplica)
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

        # Extraer todos los ítems visibles del carrusel
        items = carrusel.find_elements(By.XPATH, './/li[contains(@class,"a-carousel-card")]')
        
        for item in items:
            # Evaluar si ese item es patrocinado
            observacion = es_patrocinado(item)
            item.set_attribute = lambda k, v: None  # Para simular setattr
            item.observacion_personalizada = observacion
            productos_carrusel.append(item)

    return productos_carrusel


def extraer_productos(driver, wait):
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
                    "calificacion": extraer_calificacion(prod),
                    "observacion": obs
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

        return datos



