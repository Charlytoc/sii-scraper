import os
from datetime import datetime


def name_to_slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_").replace(",", "")


def create_file_paths(name: str, SII_REPORTS_DIRECTORY: str):
    NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name_slug = name_to_slug(name)
    TARGET_DIRECTORY = os.path.join(SII_REPORTS_DIRECTORY, name_slug, NOW)

    # Crear la ruta de salida
    UNFORMATTED_FILE = os.path.join(TARGET_DIRECTORY, "informe.md")
    FORMATTED_FILE = os.path.join(TARGET_DIRECTORY, "informe_formatted.md")

    PROFILE_FILE = os.path.join(TARGET_DIRECTORY, "profile.png")
    GW_FORMULARIO_BASE_CELDA_FILE = os.path.join(
        TARGET_DIRECTORY, "gw_formulario_base_celda.png"
    )

    DECLARACIONES_JURADAS_FILE = os.path.join(
        TARGET_DIRECTORY, "declaraciones_juradas.png"
    )

    # Crear el directorio si no existe
    if not os.path.exists(TARGET_DIRECTORY):
        os.makedirs(TARGET_DIRECTORY)

    if not os.path.exists(UNFORMATTED_FILE):
        with open(UNFORMATTED_FILE, "w", encoding="utf-8") as file:
            file.write("# Profile\n\n")

    return (
        TARGET_DIRECTORY,
        UNFORMATTED_FILE,
        FORMATTED_FILE,
        PROFILE_FILE,
        GW_FORMULARIO_BASE_CELDA_FILE,
        DECLARACIONES_JURADAS_FILE,
    )
