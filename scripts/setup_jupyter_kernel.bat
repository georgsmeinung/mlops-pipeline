@echo off
setlocal EnableDelayedExpansion

REM Script para automatizar la creación de un kernel de Jupyter basado en un entorno virtual.
REM Parámetros:
REM   %1: Ruta al directorio del entorno virtual (venv).
REM   %2: Nombre del kernel para mostrar en Jupyter.
REM Ejemplo de uso: scripts\setup_jupyter_kernel.bat venv_ingesta Ingesta

REM Validar que se proporcionen los parámetros requeridos
if "%1"=="" (
    echo ERROR: Debe especificar el directorio del entorno virtual.
    echo Uso: %0 directorio_venv nombre_kernel
    exit /b 1
)
if "%2"=="" (
    echo ERROR: Debe especificar el nombre del kernel.
    echo Uso: %0 directorio_venv nombre_kernel
    exit /b 1
)

REM Asignar parámetros a variables
set "VENV_DIR=%1"
set "KERNEL_NAME=%2"

REM Verificar si el directorio del entorno virtual existe
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ERROR: El directorio del entorno virtual "%VENV_DIR%" no existe o no es valido.
    exit /b 1
)

REM Activar el entorno virtual
echo Activando el entorno virtual "%VENV_DIR%"...
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual.
    exit /b 1
)

REM Instalar ipykernel en el entorno virtual
echo Instalando ipykernel...
pip install ipykernel
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo instalar ipykernel.
    exit /b 1
)

REM Crear el kernel de Jupyter
echo Creando kernel "%KERNEL_NAME%"...
python -m ipykernel install --user --name="%KERNEL_NAME%" --display-name="Python (%KERNEL_NAME%)"
if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo crear el kernel de Jupyter.
    exit /b 1
)

REM Mensaje de éxito
echo.
echo Kernel "%KERNEL_NAME%" configurado correctamente para el entorno virtual "%VENV_DIR%".
echo Puede seleccionarlo en Jupyter como "Python (%KERNEL_NAME%)".

REM Desactivar el entorno virtual
deactivate

endlocal
exit /b 0
