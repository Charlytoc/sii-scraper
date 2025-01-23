import inquirer


def select_from_list(options: list[str]) -> str:
    """
    Permite al usuario seleccionar una opción desde una lista en la CLI.

    Args:
        opciones (list): Lista de opciones a mostrar.

    Returns:
        str: Opción seleccionada por el usuario.
    """
    if not options or not isinstance(options, list):
        raise ValueError("Debes proporcionar una lista válida de opciones.")

    pregunta = [
        inquirer.List("seleccion", message="Selecciona una opción:", choices=options)
    ]

    respuesta = inquirer.prompt(pregunta)
    return respuesta["seleccion"]
