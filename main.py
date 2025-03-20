import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from utils.inquiries import select_from_list

# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
from utils.constants import selectors, convertir_markdown_a_docx, extraer_markdown
from utils.printer import Printer
from utils.openai_calls import create_completion_openai
import os
from utils.files import create_file_paths, open_docx

"""
EXAMPLE CSV:

NOMBRE EMPRESA,RUT EMPRESA,CLAVE SII
SAAVEDRA Y CIA LTDA,77817720-K,1978381
"""


# Cargar las variables del archivo .env
load_dotenv()
# desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
# SII_REPORTS_DIRECTORY = os.path.join(desktop_path, "sii_reports")
SII_REPORTS_DIRECTORY = os.path.join(os.getcwd(), "reports")

if not os.path.exists(SII_REPORTS_DIRECTORY):
    os.makedirs(SII_REPORTS_DIRECTORY)
LOGIN_PAGE = "https://misiir.sii.cl/cgi_misii/siihome.cgi"
EMPRESAS_CSV = os.path.join(SII_REPORTS_DIRECTORY, "config", "empresas.csv")
PLANTILLA_DOCX = os.path.join(SII_REPORTS_DIRECTORY, "config", "plantilla.docx")
MAX_RETRIES = 3


def get_relative_path(path: str) -> str:
    return os.path.relpath(path, SII_REPORTS_DIRECTORY)


def format_markdown(markdown_content: str, from_company: str) -> str:
    Printer.blue(
        f"FerConsultorAI está terminando el markdown de la empresa {from_company}..."
    )
    markdown = create_completion_openai(
        system_prompt=f"You are a helpful assistant capable of formatting HTML content to markdown in an engaging way. Use rich formatting when needed, lists, headings, etc. Return only the markdown content, no other text or comments. If there are images present in the original content, include them in the resulting markdown file using the exact path provided in the original file. You need also to convert table into lists, after your formatting, Pandoc will be used to convert your response to docx.\n\n You can use a frontmatter to add the title and the date of the report. The title should be 'Reporte SII para {from_company}' The author should be 'FerConsultorAI': Today is: {datetime.now().strftime('%d/%m/%Y')}",
        user_prompt=markdown_content,
    )
    return extraer_markdown(markdown)


def test_ai_answer(question: str) -> str:
    return create_completion_openai(
        system_prompt="You are a helpful assistant that answer yes or no to the user's question. You are not allowed to answer anything else.",
        user_prompt=question,
    )


def create_file(content: str, path: str) -> None:
    Printer.blue("Creating file...")
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def login(driver, rut, clave):
    driver.get(LOGIN_PAGE)
    usuario = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "rutcntr"))
    )
    usuario.send_keys(rut)

    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "clave"))
    )
    password.send_keys(clave)

    boton_ingresar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "bt_ingresar"))
    )
    boton_ingresar.click()

    return driver


def capture_modal(driver, TARGET_DIRECTORY, UNFORMATTED_FILE) -> bool:
    try:
        Printer.blue("Checking if modal is present...")
        modal_emergente = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#ModalEmergente .modal-content")
            )
        )

        Printer.blue("Modal is present, taking screenshot...")
        modal_path = os.path.join(TARGET_DIRECTORY, "modal_emergente_cerrada.png")
        modal_emergente.screenshot(modal_path)
        modal_text = modal_emergente.text

        with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:
            markdown_file.write(
                f"## Modal emergente cerrada, un asesor debe revisar la información \n\n![Modal emergente cerrada]({modal_path})\n\n"
            )
            markdown_file.write(f"## Texto del modal \n\n{modal_text}\n\n")

        # And the close the modal clicking the button #ModalEmergente button.close
        boton_cerrar_modal = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#ModalEmergente button.close")
            )
        )
        boton_cerrar_modal.click()
        return True
    except TimeoutException:
        Printer.blue("Modal is not present, skipping...")
        return False


def take_screenshot_to_responsabilities(driver, TARGET_DIRECTORY, UNFORMATTED_FILE):
    Printer.blue("Trying to screenshot responsabilidades tributarias...")
    contenido_obligaciones = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "contenidoObligaciones"))
    )

    contenido_obligaciones.screenshot(
        os.path.join(TARGET_DIRECTORY, "responsabilidades_tributarias.png")
    )
    ss_path = os.path.join(TARGET_DIRECTORY, "responsabilidades_tributarias.png")
    with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:
        markdown_file.write(
            f"## Responsabilidades tributarias \n\n![Responsabilidades tributarias]({ss_path})\n\n"
        )


# tries = 0
steps = [
    "responsabilidades_tributarias_screenshot",
    "datos_contribuyente_screenshot",
    "selectors_processed",
    "f29_screenshot",
    "declaraciones_juradas_screenshot",
]
# done_steps = []


def main(rut, clave, company_name, rest_tries=3):

    if not rut or not clave:
        Printer.red("Las credenciales no se cargaron correctamente.")
        exit()

    (
        TARGET_DIRECTORY,
        UNFORMATTED_FILE,
        FORMATTED_FILE,
        PROFILE_FILE,
        GW_FORMULARIO_BASE_CELDA_FILE,
        DECLARACIONES_JURADAS_FILE,
    ) = create_file_paths(company_name, SII_REPORTS_DIRECTORY)

    done_steps = [
        # "responsabilidades_tributarias_screenshot",
        # "datos_contribuyente_screenshot",
        # "selectors_processed",
        # "f29_screenshot",
        # "declaraciones_juradas_screenshot",
        # "consulta_estado_declaracion_tres_ultimos_periodos",
    ]
    tries = rest_tries

    tries += 1
    Printer.blue(f"¡Iniciando programa para {company_name}!")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Desactiva para depuración
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--window-size=1920,1080"
    )  # Establece una resolución fija
    chrome_options.add_argument("--start-maximized")  # Maximiza la ventana al iniciar

    driver = webdriver.Chrome(options=chrome_options)

    Printer.green("¡Driver inicializado!")

    Printer.yellow(
        "Puedes ver cómo se van creando los archivos en: " + TARGET_DIRECTORY
    )
    try:
        # Abrir la página de inicio de sesión
        Printer.blue(f"Iniciando sesión para {company_name}...")
        driver = login(driver, rut, clave)
        Printer.green("¡Sesión iniciada exitosamente!")

        time.sleep(3)

        capture_modal(driver, TARGET_DIRECTORY, UNFORMATTED_FILE)

        if "responsabilidades_tributarias_screenshot" not in done_steps:
            take_screenshot_to_responsabilities(
                driver, TARGET_DIRECTORY, UNFORMATTED_FILE
            )
            done_steps.append("responsabilidades_tributarias_screenshot")
            Printer.green("¡Screenshot de responsabilidades tributarias guardado!")

        if "datos_contribuyente_screenshot" not in done_steps:
            datos_personales = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "menu_datos_contribuyente"))
            )
            datos_personales.click()

            # Esperar a que el div con id="profile" esté presente
            profile_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "profile"))
            )

            # Capturar el div y guardar la imagen
            profile_div.screenshot(PROFILE_FILE)

            profile_text = profile_div.text
            with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:
                markdown_file.write(
                    "## Datos personales y tributarios del contribuyente\n\n"
                )
                markdown_file.write(str(profile_text))
                markdown_file.write("\n\n---\n\n")
                markdown_file.write(
                    f"![Datos personales y tributarios]({PROFILE_FILE})\n\n"
                )

            done_steps.append("datos_contribuyente_screenshot")
            Printer.green(
                "¡Screenshot de datos personales y tributarios guardado! Información agregada al archivo markdown."
            )

        if "selectors_processed" not in done_steps:
            # Crear o abrir el archivo de Markdown
            with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:

                # Procesar los selectores
                for index, selector in enumerate(selectors):
                    try:
                        # Hacer clic en el opener
                        try:
                            opener = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(
                                    (By.CSS_SELECTOR, selector["opener"])
                                )
                            )
                            opener.click()
                            Printer.green(
                                f"[{index + 1}] Opener '{selector['opener']}' abierto."
                            )
                        except Exception as e:
                            Printer.red(f"ERROR EN EL OPENER [{index + 1}]")
                            Printer.red(e)

                            # Try to close all the ul.dropdown-menu
                            try:
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, "ul.dropdown-menu")
                                    )
                                )
                                driver.execute_script(
                                    "document.querySelectorAll('ul.dropdown-menu').forEach(menu => menu.style.display = 'none');"
                                )
                                Printer.green("¡Todos los menús desplegables cerrados!")
                                # Click the opener again
                                opener.click()
                                Printer.green("Opener clickeado nuevamente")
                            except Exception as e:
                                Printer.red(e)
                                continue

                        # Esperar 2 segundos para que el contenido cargue
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, selector["content"])
                            )
                        )

                        time.sleep(2)

                        # Extraer el contenido del div
                        content = driver.find_element(
                            By.CSS_SELECTOR, selector["content"]
                        )
                        content_html = content.get_attribute("innerHTML")

                        # Escribir el contenido en el archivo Markdown
                        markdown_file.write(f"### Sección {index + 1}\n\n")
                        markdown_file.write(content_html)
                        markdown_file.write("\n\n---\n\n")

                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", opener
                        )
                        # Cerrar el opener
                        opener.click()
                        Printer.green(f"Sección  {index + 1} procesada!")
                        time.sleep(2)

                    except Exception as e:
                        print(
                            f"[{index + 1}] ¡Error al procesar el selector '{selector['opener']}': {e}"
                        )

            done_steps.append("selectors_processed")

        # Click en <a href="https://www.sii.cl/servicios_online/">Servicios online <i class="fa fa-caret-down" aria-hidden="true"></i></a>

        if "f29_screenshot" not in done_steps:
            Printer.blue("Obteniendo formulario F29...")
            servicios_online = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a[href='https://www.sii.cl/servicios_online/']")
                )
            )
            Printer.green("¡Servicios online encontrado!")
            servicios_online.click()

            Printer.blue("Obteniendo impuestos mensuales...")
            impuestos_mensuales = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[id='linkpadre_1042']")
                )
            )
            impuestos_mensuales.click()
            Printer.green("¡Impuestos mensuales encontrado!")

            # Esperar que el elemento: <a href="1042-3266.html" target="_self">Consulta y seguimiento (F29 y F50) <i class="fa fa-chevron-circle-right pull-right fa-lg" aria-hidden="true"></i></a> termine de cargar
            consulta_seguimiento = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href='1042-3266.html']")
                )
            )
            consulta_seguimiento.click()

            # esperar que el elemento <a> con texto: 'Consulta Integral F29' termine de cargar
            consulta_integral_f29 = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//a[text()='Consulta Integral F29']",
                    )
                )
            )
            consulta_integral_f29.click()

            # esperar que el elemento: <a href="#29">F29 (-)</a> termine de cargar
            f29 = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='F29 (+)']"))
            )
            FOUND_PROBLEMS = False

            try:
                driver.find_element(By.CSS_SELECTOR, ".gw-panel-center-alert")
                Printer.red(
                    "Se encontró el elemento 'gw-panel-center-alert', hay que chequear el formulario F29"
                )
                FOUND_PROBLEMS = True
            except Exception as e:
                print(e)
                Printer.green("No se encontró el elemento '.gw-panel-center-alert'")

            f29.click()

            # Esperar que el elemento <div class="gw-par">Diciembre</div> sea visible
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.gw-par"))
            )

            gw_formulario_base_celda = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.gw-sii-tabla-interior")
                )
            )
            gw_formulario_base_celda.screenshot(GW_FORMULARIO_BASE_CELDA_FILE)

            with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:
                # Manten esta imagen en el archivo markdown
                markdown_file.write("## Formulario F29 \n\n")
                if FOUND_PROBLEMS:
                    markdown_file.write(
                        "> Comentario de FerConsultorAI: Problemas encontrados en el formulario F29, por favor chequear manualmente \n\n"
                    )
                else:
                    markdown_file.write(
                        "> Comentario de FerConsultorAI: Aparentemente no se encontraron problemas en el formulario F29, chequear imagen adjunta \n\n"
                    )
                markdown_file.write(
                    f"![GW Formulario Base Celda]({GW_FORMULARIO_BASE_CELDA_FILE})\n\n"
                )

            Printer.green("¡Screenshot del formulario F29 guardado!")
            done_steps.append("f29_screenshot")

        if "declaraciones_juradas_screenshot" not in done_steps:
            Printer.blue("Obteniendo Declaraciones juradas...")
            driver.get("https://www.sii.cl/servicios_online/")

            declaraciones_juradas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[id='linkpadre_1043']")
                )
            )
            Printer.green("¡Declaraciones juradas encontrado! Clickeando...")
            declaraciones_juradas.click()

            declaraciones_juradas_renta = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href='1043-1518.html']")
                )
            )
            Printer.green("¡Declaraciones juradas renta encontrado! Clickeando...")
            time.sleep(2)
            
            declaraciones_juradas_renta.click()

            consulta_declaraciones_juradas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href='#collapseConsultas']")
                )
            )
            Printer.green("¡Consulta declaraciones juradas encontrado! Clickeando...")
            consulta_declaraciones_juradas.click()

            # Go to https://www4.sii.cl/djconsultarentaui/internet/#/
            driver.get("https://www4.sii.cl/djconsultarentaui/internet/#/")

            # Esperar que el elemento con id 'consulta' y clase 'tab-content' termine de cargar
            consulta_estado_giros_emitidos = WebDriverWait(driver, 100).until(
                EC.presence_of_element_located((By.ID, "consulta"))
            )
            Printer.green("¡Consulta estado giros emitidos encontrado!")

            time.sleep(5)

            Printer.blue("Tomando screenshot de la tabla...")
            # Tomarle screenshot de la tabla
            consulta_estado_giros_emitidos.screenshot(
                os.path.join(TARGET_DIRECTORY, "consulta_estado_giros_emitidos.png")
            )
            ss_path = os.path.join(
                TARGET_DIRECTORY, "consulta_estado_giros_emitidos.png"
            )

            FOUND_PROBLEMS = False
            # Buscar si existe algun elemeto con texto: "Observada"
            try:
                driver.find_element(By.XPATH, "//span[text()='Observada']")
                Printer.red(
                    "Se encontró el elemento 'Observada', hay que chequear el estado de las declaraciones juradas de la empresa "
                    + company_name
                )
                FOUND_PROBLEMS = True
            except Exception as e:
                # print(e)
                Printer.green("No se encontró el elemento 'Observada'")

            with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:
                markdown_file.write(
                    "## Consulta estado y giros emitidos (declaraciones juradas de renta) \n\n"
                )
                if FOUND_PROBLEMS:
                    markdown_file.write(
                        "> Comentario de FerConsultorAI: Problemas encontrados en el estado de las declaraciones juradas de la empresa, se encontraron declaraciones observadas \n\n"
                    )
                else:
                    markdown_file.write(
                        "> Comentario de FerConsultorAI: Aparentemente no se encontraron problemas en el estado de las declaraciones juradas de la empresa, chequear imagen adjunta para confirmar \n\n"
                    )

                markdown_file.write(
                    f"![Consulta estado y giros emitidos]({ss_path})\n\n"
                )
            done_steps.append("declaraciones_juradas_screenshot")

            Printer.green("¡Screenshot de consulta estado y giros emitidos guardado!")

        if "consulta_estado_declaracion_tres_ultimos_periodos" not in done_steps:
            driver.get("https://www.sii.cl/servicios_online/")

            declaracion_renta = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[id='linkpadre_1044']")
                )
            )
            declaracion_renta.click()

            consulta_seguimiento = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href='1044-2696.html']")
                )
            )
            consulta_seguimiento.click()

            # Esperar al elemento: <a href="https://www4.sii.cl/consultaestadof22ui/" target="_self">Consultar estado de declaración</a> termine de cargar
            consultar_estado_declaracion = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "a[href='https://www4.sii.cl/consultaestadof22ui/']",
                    )
                )
            )
            consultar_estado_declaracion.click()
            # get the current url
            select_url = "https://www4.sii.cl/consultaestadof22ui/"
            # Select the first three options one by one
            for i in range(3):
                select_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "select.form-control")
                    )
                )

                time.sleep(5)
                select = Select(select_element)
                # select.options
                select.select_by_index(i)

                boton_consultar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "#formulario-periodo button")
                    )
                )
                boton_consultar.click()
                # Esperar que el elemento div.web-sii cuerpo termine de cargar
                cuerpo = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.web-sii.cuerpo")
                    )
                )

                time.sleep(5)

                ss_path = os.path.join(
                    TARGET_DIRECTORY, f"consulta_estado_declaracion_{i + 1}.png"
                )
                cuerpo.screenshot(ss_path)

                with open(UNFORMATTED_FILE, "a", encoding="utf-8") as markdown_file:
                    markdown_file.write(
                        f"## Consulta estado de declaración {i + 1} \n\n![Consulta estado de declaración {i + 1}]({ss_path})\n\n"
                    )

                driver.get(select_url)

                time.sleep(5)

        driver.quit()
        with open(UNFORMATTED_FILE, "r", encoding="utf-8") as markdown_file:
            formatted_markdown = format_markdown(markdown_file.read(), company_name)
            create_file(formatted_markdown, FORMATTED_FILE)
            OUTPUT_DOCX = os.path.join(TARGET_DIRECTORY, "informe.docx")
            convertir_markdown_a_docx(FORMATTED_FILE, PLANTILLA_DOCX, OUTPUT_DOCX)
            # open_docx(OUTPUT_DOCX)

    except Exception as e:
        print(f"¡Error durante la automatización!: {e}")
        driver.quit()
        if tries < MAX_RETRIES:
            print(f"Reintentando... ({tries + 1}/{MAX_RETRIES})")
            tries += 1
            main(rut, clave, company_name, rest_tries=tries)
        else:
            print(
                "¡Se han agotado los intentos! No se pudo completar la automatización."
            )
            driver.quit()


if __name__ == "__main__":
    # Esto es un script de automatizaci�n para procesar informaci�n tributaria.

    # if os.path.exists(EMPRESAS_CSV):
    answer = select_from_list(
        [
            "Procesar una empresa",
            "Procesar todas las empresas",
            "Salir",
        ]
    )

    if answer == "Salir":
        Printer.yellow("¡Hasta luego!")
        exit()

    if answer == "Procesar una empresa":
        rut = input("Ingrese su RUT: ")
        clave = input("Ingrese su clave: ")
        name = input("Ingrese el nombre de la empresa: ")
        main(rut, clave, name)
        exit()

    if answer == "Procesar todas las empresas":
        print("Procesando todas las empresas...")
        if not os.path.exists(EMPRESAS_CSV):
            Printer.red(
                "El archivo empresas.csv no existe. Guardalo en: " + EMPRESAS_CSV
            )
            exit()
        else:
            Printer.blue("Procesando empresas...")
            with open(EMPRESAS_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    nombre_empresa, rut, clave = row
                    if nombre_empresa == "NOMBRE EMPRESA":
                        continue
                    Printer.yellow(f"Processing {nombre_empresa}...")
                    main(rut, clave, nombre_empresa)
            Printer.green("¡Procesamiento de empresas completado!")
