REM Automatización del la generación del kernel de jupyter por etapa
REM Parámetros:
REM      %1: Directorio del venv en el que se basará el kernel
REM      %2: Nombre con el que kernel se visualizará en Jupyter
REM Uso: scripts\setup_jupyter_kernel.bat venv_ingesta Ingesta

@echo off
set VENV_DIR=%1
set KERNEL_NAME=%2
call %VENV_DIR%\Scripts\activate
pip install ipykernel
python -m ipykernel install --user --name=%KERNEL_NAME% --display-name="Python (%KERNEL_NAME%)"
echo Kernel %KERNEL_NAME% configurado para %VENV_DIR%
