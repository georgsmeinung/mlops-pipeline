@echo off
ECHO Iniciando la ejecución del notebook de Jupyter como script...

REM Verificar si se proporcionaron todos los parámetros
IF "%1"=="" (
    ECHO Error: Debe especificar el nombre del notebook.
    ECHO Uso: %0 nombre_notebook.ipynb nombre_kernel ruta_entorno_virtual
    EXIT /B 1
)
IF "%2"=="" (
    ECHO Error: Debe especificar el nombre del kernel.
    ECHO Uso: %0 nombre_notebook.ipynb nombre_kernel ruta_entorno_virtual
    EXIT /B 1
)
IF "%3"=="" (
    ECHO Error: Debe especificar la ruta al entorno virtual.
    ECHO Uso: %0 nombre_notebook.ipynb nombre_kernel ruta_entorno_virtual
    EXIT /B 1
)

REM Asignar parámetros a variables
SET NOTEBOOK=%1
SET KERNEL=%2
SET VENV_PATH=%3

REM Verificar si la ruta del entorno virtual existe
IF NOT EXIST "%VENV_PATH%\Scripts\activate.bat" (
    ECHO Error: No se encontró activate.bat en %VENV_PATH%\Scripts
    EXIT /B 1
)

REM Activar el entorno virtual
ECHO Activando entorno virtual en %VENV_PATH%...
CALL "%VENV_PATH%\Scripts\activate.bat"

REM Ejecutar el notebook con el kernel especificado
ECHO Ejecutando %NOTEBOOK% con el kernel %KERNEL%...
jupyter nbconvert --execute --to notebook --inplace --kernel=%KERNEL% %NOTEBOOK%

REM Verificar si la ejecución fue exitosa
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Falló la ejecución del notebook.
    EXIT /B %ERRORLEVEL%
)

REM Desactivar el entorno virtual
ECHO Desactivando entorno virtual...
CALL deactivate

REM Pausar para ver los resultados (opcional)
PAUSE
