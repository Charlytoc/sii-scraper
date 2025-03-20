@echo off
setlocal

:: Verificar si el entorno virtual ya existe
if exist venv (
    echo El entorno virtual ya existe. Activándolo...
) else (
    echo Creando el entorno virtual...
    python -m venv venv
)

:: Activar el entorno virtual
call venv\Scripts\activate

:: Verificar e instalar dependencias sin mostrar el log
echo Verificando dependencias...
pip install -r requirements.txt > nul 2>&1

:: Verificar y crear el archivo .env
python utils/verify_env.py

:: Ejecutar el script principal
echo Ejecutando main.py...
python main.py

echo Proceso completado, FerConsultorAI se despide. 