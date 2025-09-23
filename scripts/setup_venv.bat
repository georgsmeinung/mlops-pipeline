REM Parámetros:
REM     %1: Directorio del venv (e.g., venv_ingesta).
REM     %2: Ruta al ejecutable de Python (e.g., C:\Python39\python.exe).
REM     %3: Ruta al archivo de requirements
REM  Uso: setup_venv.bat venv_ingesta C:\Python39\python.exe .\requirements\requirements_ingesta.txt

@echo off
set VENV_DIR=%1
set PYTHON_EXEC=%2
set REQ_FILE=%3
%PYTHON_EXEC% -m venv %VENV_DIR%
call %VENV_DIR%\Scripts\activate
pip install --upgrade pip
pip install -r %REQ_FILE%
echo Entorno virtual creado en %VENV_DIR% con %PYTHON_EXEC% y requisitos %REQ_FILE%
