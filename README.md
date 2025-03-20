## FerconsultorAI

FerConsultorAI es un programa simple de Python que automatiza el proceso de descarga de los reportes de la SII de Chile, usando herramientas de Python para obtener los datos de la SII, crear un reporte en formato DOCX y luego guardarlo en la carpeta `reports`.

### Instalación

Para que FerConsultorAI funcione, necesitas instalar los siguientes requisitos previos:

#### Pyenv

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

#### Python con Pyenv

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

#### Pandoc

Pandoc es un compilador de documentos que puede ser útil para la conversión de formatos. En FerConsultorAI, Pandoc se usa para convertir un archivo Markdown a DOCX.

1. Visita este [enlace](https://github.com/jgm/pandoc/releases/tag/3.6.4) para instalar Pandoc.

2. Descarga el archivo `pandoc-3.6.4-windows-x86_64.msi` y sigue los pasos de la instalación.

#### Instalación de dependencias

3. **Entorno Virtual**: Cree un entorno virtual para el proyecto.
4. **Dependencias**: Instale todas las dependencias necesarias.
5. **Pandoc**: Un compilador de documentos que puede ser �til para la conversi�n de formatos.
