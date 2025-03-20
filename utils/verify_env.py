import os

# Definir el nombre del archivo .env
env_file = ".env"

# Verificar si el archivo .env ya existe
if os.path.exists(env_file):
    print(f"✅ El archivo {env_file} ya existe. No se necesita crear uno nuevo.")
else:
    # Pedir la clave de OpenAI al usuario
    api_key = input("Ingrese su clave de OpenAI: ").strip()

    # Crear el archivo .env con la clave
    with open(env_file, "w", encoding="utf-8") as file:
        file.write(f"OPENAI_API_KEY={api_key}\n")

    print(f"✅ Archivo {env_file} creado con éxito.")
