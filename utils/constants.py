import pypandoc
import subprocess
import re

selectors = [
    {"opener": "a[href='#collapse1Cntrb']", "content": "div[id='divdirection']"},
    {"opener": "a[href='#collapse11Cntrb']", "content": "div[id='collapse11Cntrb']"},
    {"opener": "a[href='#collapse2Cntrb']", "content": "div[id='collapse2Cntrb']"},
    {"opener": "a[href='#collapse3Cntrb']", "content": "div[id='collapse3Cntrb']"},
    {"opener": "a[href='#collapse4Cntrb']", "content": "div[id='collapse4Cntrb']"},
    {"opener": "a[href='#collapse6Cntrb']", "content": "div[id='collapse6Cntrb']"},
    {"opener": "a[href='#collapse7Cntrb']", "content": "div[id='collapse7Cntrb']"},
    {"opener": "a[href='#collapse13Cntrb']", "content": "div[id='collapse13Cntrb']"},
    {"opener": "a[href='#collapse10Cntrb']", "content": "div[id='collapse10Cntrb']"},
    {"opener": "a[href='#collapse14Cntrb']", "content": "div[id='collapse14Cntrb']"},
    {"opener": "a[href='#collapse9Cntrb']", "content": "div[id='collapse9Cntrb']"},
]


def convertir_markdown_a_docx(markdown_path, plantilla_docx_path, output_docx_path):
    """
    Convierte un archivo Markdown a DOCX utilizando una plantilla personalizada.

    Args:
        markdown_path (str): Ruta del archivo Markdown de entrada.
        plantilla_docx_path (str): Ruta del archivo de plantilla DOCX.
        output_docx_path (str): Ruta de salida para el archivo DOCX generado.

    Returns:
        str: Ruta del archivo DOCX generado si la conversión fue exitosa.
    """
    try:
        command = [
            "pandoc",
            markdown_path,
            "-o",
            output_docx_path,
            "--reference-doc",
            plantilla_docx_path,
        ]
        subprocess.run(command, check=True)
        print(f"Archivo DOCX generado correctamente en: {output_docx_path}")
        return output_docx_path
    except Exception as e:
        print(f"Error durante la conversión: {e}")
        return None


def extraer_markdown(texto):
    """
    Extrae el contenido de un bloque de código Markdown, eliminando las líneas delimitadoras.
    Si no encuentra un bloque válido, retorna el texto original.

    Args:
        texto (str): Texto completo que contiene el bloque de código Markdown.

    Returns:
        str: Contenido del bloque Markdown sin las líneas delimitadoras, o el texto original si no se encuentra un bloque.
    """
    # Expresión regular para encontrar el contenido dentro de ```markdown ... ```
    match = re.search(r"```markdown\n(.*?)\n```", texto, re.DOTALL)

    if match:
        # Retornar solo el contenido capturado dentro del bloque
        return match.group(1).strip()
    else:
        # Retornar el texto original si no se encuentra un bloque válido
        return texto.strip()
