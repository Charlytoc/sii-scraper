# FerconsultorAI

FerConsultorAI es un programa simple de Python que automatiza el proceso de descarga de los reportes de la SII de Chile, usando herramientas de Python para obtener los datos de la SII, crear un reporte en formato DOCX y luego guardarlo en la carpeta `reports`.

## Instalación

Para que FerConsultorAI funcione, necesitas instalar los siguientes requisitos previos:

### Pyenv

Pyenv es un gestor de versiones de Python. Con él se pueden instalar múltiples versiones de Python en una misma máquina.

Para instalar pyenv en Windows, puedes seguir estos pasos:

1. Abrir una terminal de PowerShell.
2. Ejecutar el siguiente comando para instalar pyenv:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

> Nota: Si estás obteniendo un error al ejecutar el comando, abre una terminal de PowerShell como administrador y ejecuta este comando:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

### Python con Pyenv

Para instalar Python con pyenv, puedes seguir estos pasos:

1. Abrir una terminal de PowerShell.
2. Ejecutar el siguiente comando para instalar Python:

```powershell
pyenv install 3.12.7
```

3. Haz que la nueva versión de Python sea la que se usará por defecto:

```powershell
pyenv global 3.12.7
```

### Pandoc

Pandoc es un compilador de documentos que puede ser útil para la conversión de formatos. En FerConsultorAI, Pandoc se usa para convertir un archivo Markdown a DOCX.

1. Visita este [enlace](https://github.com/jgm/pandoc/releases/tag/3.6.4) para instalar Pandoc.

2. Descarga el archivo `pandoc-3.6.4-windows-x86_64.msi` y sigue los pasos de la instalación.

### Ejecutar FerConsultorAI

Para ejecutar FerConsultorAI, puedes ejecutar el siguiente comando:

```powershell
./run.bat
```

Este comando se encargará de instalar las dependencias, crear el entorno virtual y ejecutar el script principal. Las primeras dos acciones solo se ejecutarán si el entorno virtual no existe.

## Configuración

Puedes agregar una lista de empresas en el archivo `reports/config/empresas.csv`.

Cada fila de este archivo debe tener el siguiente formato:

```
NOMBRE EMPRESA,RUT EMPRESA,CLAVE SII
nombre_de_la_empresa,rut_de_la_empresa,nombre_del_asesor
nombre_de_la_empresa,rut_de_la_empresa,nombre_del_asesor
nombre_de_la_empresa,rut_de_la_empresa,nombre_del_asesor
nombre_de_la_empresa,rut_de_la_empresa,nombre_del_asesor
```

La primera columna es el nombre de la empresa, la segunda es el RUT de la empresa y la tercera es la clave SII de la empresa.

## Uso

Para usar FerConsultorAI, solo necesitas ejecutar el script principal.

```powershell
./run.bat
```

En la línea de comandos se te va a preguntar si quieres ejecutar una empresa (tendrás que ingresar los datos) o si quieres ejecutar todas las empresas (se usarán los datos de la lista de empresas en el archivo `reports/config/empresas.csv`).

Si es la primera vez que ejecutas el script, se te pedirá que ingreses una clave de OpenAI para usar un modelo de IA y darle un formato amigable al informe final.

## Reportes

Los reportes se guardarán en la carpeta `reports/nombre_de_la_empresa/fecha_del_reporte`.

Dentro de esta carpeta encontrarás luego de finalizar el proceso el informe en formato DOCX y todas las imágenes que se han descargado.
