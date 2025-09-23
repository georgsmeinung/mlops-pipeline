@echo off
REM ===========================================================================
REM Nombre: setup_venv.bat
REM Descripción: Script para crear y configurar un entorno virtual de Python.
REM              Instala dependencias desde un archivo de requisitos especificado.
REM
REM Parámetros:
REM     %1: Directorio donde se creará el entorno virtual (e.g., venv_ingesta).
REM     %2: Ruta al ejecutable de Python (e.g., C:\Python39\python.exe).
REM     %3: Ruta al archivo de requisitos (e.g., .\requirements\requirements_ingesta.txt).
REM
REM Uso: setup_venv.bat <directorio_venv> <ruta_python_exe> <ruta_requirements>
REM Ejemplo: setup_venv.bat venv_ingesta C:\Python39\python.exe .\requirements\requirements_ingesta.txt
REM
REM Notas:
REM     - Asegúrate de que el ejecutable de Python especificado existe y es válido.
REM     - El archivo de requisitos debe existir en la ruta proporcionada.
REM     - El script actualiza pip antes de instalar los requisitos.
REM ===========================================================================

REM --- Validación de parámetros ---
if "%1"=="" (
    echo ERROR: No se especificó el directorio del entorno virtual.
    echo Uso: %0 ^<directorio_venv^> ^<ruta_python_exe^> ^<ruta_requirements^>
    exit /b 1
)
if "%2"=="" (
    echo ERROR: No se especificó la ruta al ejecutable de Python.
    echo Uso: %0 ^<directorio_venv^> ^<ruta_python_exe^> ^<ruta_requirements^>
    exit /b 1
)
if "%3"=="" (
    echo ERROR: No se especificó la ruta al archivo de requisitos.
    echo Uso: %0 ^<directorio_venv^> ^<ruta_python_exe^> ^<ruta_requirements^>
    exit /b 1
)

REM --- Asignación de parámetros ---
set "VENV_DIR=%1"
set "PYTHON_EXEC=%2"
set "REQ_FILE=%3"

REM --- Verificación de existencia del ejecutable de Python ---
if not exist "%PYTHON_EXEC%" (
    echo ERROR: El ejecutable de Python no se encuentra en %PYTHON_EXEC%.
    exit /b 1
)

REM --- Verificación de existencia del archivo de requisitos ---
if not exist "%REQ_FILE%" (
    echo ERROR: El archivo de requisitos no se encuentra en %REQ_FILE%.
    exit /b 1
)

REM --- Creación del entorno virtual ---
echo Creando entorno virtual en %VENV_DIR%...
%PYTHON_EXEC% -m venv %VENV_DIR%
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual.
    exit /b %ERRORLEVEL%
)

REM --- Activación del entorno virtual ---
echo Activando entorno virtual...
call %VENV_DIR%\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual.
    exit /b %ERRORLEVEL%
)

REM --- Actualización de pip ---
echo Actualizando pip...
pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo actualizar pip.
    exit /b %ERRORLEVEL%
)

REM --- Instalación de requisitos ---
echo Instalando requisitos desde %REQ_FILE%...
pip install -r %REQ_FILE%
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudieron instalar los requisitos desde %REQ_FILE%.
    exit /b %ERRORLEVEL%
)

REM --- Mensaje de éxito ---
echo.
echo Entorno virtual creado y configurado exitosamente en %VENV_DIR%!
echo Python: %PYTHON_EXEC%
echo Requisitos: %REQ_FILE%

REM --- Limpieza de variables ---
set VENV_DIR=
set PYTHON_EXEC=
set REQ_FILE=

exit /b 0
