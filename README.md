# mlops-pipeline

## Descripción

Este repositorio contiene un pipeline de MLOps auditable y modular diseñado para científicos de datos. El pipeline utiliza **Jupyter Notebooks** para implementar cada etapa, **MLflow** para seguimiento, registro de modelos y gestión de artefactos, **Jenkins** para orquestación y automatización, y entornos virtuales (`venv`) para aislamiento de dependencias. La solución está optimizada para ejecutarse directamente en **Windows** sin necesidad de contenedores (Docker), facilitando su uso para equipos con poca experiencia en DevOps.

Cada etapa del pipeline puede usar una versión específica de Python, configurada en un entorno virtual independiente, para garantizar compatibilidad con las bibliotecas requeridas. Además, los entornos virtuales pueden configurarse como **kernels de Jupyter** para ejecutar las etapas de forma interactiva en un servidor local de Jupyter.

El pipeline incluye las siguientes etapas:
1. **Ingesta y Validación de Datos**: Carga y validación de datos con herramientas AutoML como `ydata-profiling`, `sweetviz` y `dtale`.
2. **Ingeniería de Características**: Generación de características con `autofeat`, `featuretools` y `tsfresh`.
3. **Entrenamiento del Modelo**: Entrenamiento de modelos con `scikit-learn` y visualización con `autoviz`.
4. **Evaluación del Modelo**: Evaluación de modelos con métricas y visualizaciones.
5. **Despliegue del Modelo**: Despliegue del modelo como API local o script de predicción por lotes.

Cada etapa es auditable, con registros y artefactos almacenados en MLflow para trazabilidad.

## Requisitos Previos

- **Sistema Operativo**: Windows 10 o superior.
- **Python**: Múltiples versiones instaladas según las necesidades de cada etapa (e.g., Python 3.9 para ingesta, Python 3.10 para entrenamiento). Asegúrate de que los ejecutables de Python estén disponibles (e.g., `C:\Python39\python.exe`, `C:\Python310\python.exe`).
- **Jenkins**: Instalado en Windows (descargar el instalador MSI desde [Jenkins](https://www.jenkins.io/download/)).
- **Git**: Instalado para control de versiones (descargar desde [Git](https://git-scm.com/downloads)).
- **Dependencias**: Especificadas en archivos `requirements_*.txt` para cada etapa (se instalan automáticamente en los entornos virtuales).
- **Jupyter**: Servidor local para ejecución interactiva de notebooks (opcional).

## Estructura del Repositorio

```
mlops-pipeline/
├── notebooks/
│   ├── 01_ingesta_datos.ipynb                # Ingesta y validación de datos
│   ├── 02_ingenieria_caracteristicas.ipynb   # Ingeniería de características
│   ├── 03_entrenamiento_modelo.ipynb         # Entrenamiento de modelos
│   ├── 04_evaluacion_modelo.ipynb            # Evaluación de modelos
│   ├── 05_despliegue_modelo.ipynb            # Despliegue de modelos
├── scripts/
│   ├── setup_venv.bat                        # Script para crear entorno virtual
│   ├── run_notebook.bat                      # Script para ejecutar notebooks
│   ├── setup_jupyter_kernel.bat              # Script para configurar kernels de Jupyter
├── requirements/
│   ├── requirements_ingesta.txt              # Dependencias para ingesta (e.g., Python 3.9)
│   ├── requirements_ingenieria.txt           # Dependencias para ingeniería de características
│   ├── requirements_entrenamiento.txt        # Dependencias para entrenamiento
│   ├── requirements_evaluacion.txt           # Dependencias para evaluación
│   ├── requirements_despliegue.txt           # Dependencias para despliegue
├── mlruns/                                   # Artefactos y registros de MLflow
├── data/
│   ├── raw/                                  # Datos crudos de entrada
│   ├── processed/                            # Datos procesados
├── jenkins/
│   ├── Jenkinsfile                           # Configuración del pipeline de Jenkins
├── logs/                                     # Registros de ejecución
└── README.md                                 # Este archivo
```

## Configuración de Versiones de Python

El pipeline permite usar diferentes versiones de Python para cada etapa. Asegúrate de:

1. Instalar las versiones requeridas de Python (e.g., 3.9 y 3.10) en rutas específicas (e.g., `C:\Python39`, `C:\Python310`).
2. Actualizar el `Jenkinsfile` con las rutas correctas de los ejecutables de Python.
3. Verificar la compatibilidad de las dependencias en cada `requirements_*.txt` con la versión de Python correspondiente.

Por ejemplo:
- La etapa de ingesta de datos usa Python 3.9 con `requirements_ingesta.txt`.
- La etapa de entrenamiento usa Python 3.10 con `requirements_entrenamiento.txt`.

Consulta la documentación de cada biblioteca en `requirements/` para asegurar compatibilidad.

## Instalación y Configuración

### 1. Clonar el Repositorio
Clona el repositorio en tu máquina local:
```bash
git clone https://github.com/georgsmeinung/mlops-pipeline
cd automl-pipeline
```

### 2. Instalar Versiones de Python
1. Descarga e instala las versiones de Python requeridas (e.g., Python 3.9 y 3.10) desde [python.org](https://www.python.org/downloads/). Alternativamente, usa `pyenv-win` para gestionar múltiples versiones.
2. Asegúrate de que cada versión esté disponible en el sistema (e.g., `C:\Python39\python.exe`, `C:\Python310\python.exe`).
3. Verifica las versiones instaladas:
   ```bash
   C:\Python39\python.exe --version
   C:\Python310\python.exe --version
   ```

### 3. Instalar Jenkins
1. Descarga el instalador MSI de Jenkins desde [Jenkins](https://www.jenkins.io/download/).
2. Sigue las instrucciones de instalación.
3. Accede a Jenkins en `http://localhost:8080` y completa la configuración inicial.
4. Instala los plugins necesarios:
   - **Pipeline**: Para definir pipelines.
   - **Python**: Para soporte de Python en Jenkins.
   Configura los plugins en `Administrar Jenkins > Administrar Plugins`.

### 4. Configurar MLflow
1. Inicia el servidor de MLflow usando una versión base de Python (e.g., Python 3.9):
   ```bash
   C:\Python39\python.exe -m mlflow server --backend-store-uri file://C:/mlops_project/mlruns --default-artifact-root file://C:/mlops_project/mlruns
   ```
2. Accede a la interfaz de MLflow en `http://localhost:5000` para auditar experimentos y artefactos.

### 5. Configurar Jenkins
1. Crea un nuevo job de tipo **Pipeline** en Jenkins.
2. Apunta el job al archivo `Jenkinsfile` en el directorio `jenkins/`.
3. Configura las rutas de los ejecutables de Python en el `Jenkinsfile` (e.g., `C:\\Python39\\python.exe`, `C:\\Python310\\python.exe`).

### 6. Configurar Entornos Virtuales
Cada etapa del pipeline usa un entorno virtual con una versión específica de Python y sus dependencias. Los entornos se crean automáticamente durante la ejecución del pipeline, pero puedes crearlos manualmente para pruebas:
```bash
scripts\setup_venv.bat venv_ingesta C:\Python39\python.exe requirements\requirements_ingesta.txt
```

### 7. Configurar Kernels de Jupyter
Para ejecutar las etapas de forma interactiva en un servidor local de Jupyter, configura los entornos virtuales como kernels:

1. Crea un entorno virtual para una etapa:
   ```bash
   scripts\setup_venv.bat venv_ingesta C:\Python39\python.exe requirements\requirements_ingesta.txt
   ```
2. Activa el entorno virtual:
   ```bash
   venv_ingesta\Scripts\activate
   ```
3. Instala el kernel de Jupyter:
   ```bash
   pip install ipykernel
   python -m ipykernel install --user --name=venv_ingesta --display-name="Python 3.9 (Ingesta)"
   ```
4. Repite para cada etapa, usando nombres descriptivos para los kernels (e.g., `venv_ingenieria`, `venv_entrenamiento`).
5. Opcionalmente, usa el script `setup_jupyter_kernel.bat` para automatizar:
   ```bat
   @echo off
   set VENV_DIR=%1
   set KERNEL_NAME=%2
   call %VENV_DIR%\Scripts\activate
   pip install ipykernel
   python -m ipykernel install --user --name=%KERNEL_NAME% --display-name="Python (%KERNEL_NAME%)"
   echo Kernel %KERNEL_NAME% configurado para %VENV_DIR%
   ```

   Ejemplo:
   ```bash
   scripts\setup_jupyter_kernel.bat venv_ingesta Ingesta
   ```

6. Inicia un servidor local de Jupyter:
   ```bash
   C:\Python39\python.exe -m jupyter notebook
   ```
7. Abre un navegador en `http://localhost:8888` y selecciona el kernel correspondiente (e.g., `Python 3.9 (Ingesta)`) para ejecutar un notebook.

### 8. Preparar los Datos
Coloca los datos crudos en la carpeta `data/raw/` (e.g., `input.csv`).

## Uso del Pipeline

### Ejecución Automática (Jenkins)
1. Inicia el servidor de MLflow (ver paso 4 de la configuración).
2. En Jenkins, selecciona el job del pipeline y haz clic en **Build Now**.
3. Monitorea la ejecución en la consola de Jenkins y revisa los artefactos en `mlruns/`.

### Ejecución Interactiva (Jupyter)
1. Configura los kernels de Jupyter para cada etapa (ver paso 7 de la configuración).
2. Inicia el servidor de Jupyter:
   ```bash
   C:\Python39\python.exe -m jupyter notebook
   ```
3. Abre el notebook correspondiente (e.g., `notebooks/01_ingesta_datos.ipynb`), selecciona el kernel adecuado (e.g., `Python 3.9 (Ingesta)`) y ejecuta las celdas interactivamente.
4. Los resultados se registran en MLflow si el servidor está activo.

### Monitoreo y Auditoría
- **Jenkins**: Revisa los logs en `logs/` y la consola de Jenkins para detalles de ejecución.
- **MLflow**: Accede a `http://localhost:5000` para ver experimentos, métricas, artefactos y modelos registrados. Cada etapa registra la versión de Python utilizada como parámetro (`python_version`).
- **Jupyter**: Usa la interfaz de Jupyter para inspeccionar resultados intermedios y artefactos generados.

## Dependencias

Cada etapa tiene su propio archivo de requisitos en el directorio `requirements/`:
- `requirements_ingesta.txt` (e.g., Python 3.9):
  ```
  autofeat==2.0.10
  autoviz==0.1.905
  dask==2024.8.1
  dtale==3.13.1
  ydata-profiling==4.10.0
  sweetviz==2.3.1
  mlflow==2.17.0
  papermill==2.6.0
  jupyter==1.1.1
  ipykernel==6.29.5
  ```
- `requirements_entrenamiento.txt` (e.g., Python 3.10):
  ```
  scikit-learn==1.5.2
  featuretools==1.31.0
  tsfresh==0.20.3
  autoviz==0.1.905
  tabulate==0.9.0
  mlflow==2.17.0
  papermill==2.6.0
  jupyter==1.1.1
  ipykernel==6.29.5
  ```

Verifica la compatibilidad de cada biblioteca con la versión de Python correspondiente en [PyPI](https://pypi.org/).

## Configuración de Versiones de Python

El pipeline permite usar diferentes versiones de Python para cada etapa, según los requisitos de las bibliotecas:
- **Ingesta de Datos**: Usa Python 3.9 para compatibilidad con `ydata-profiling` y `dtale`.
- **Ingeniería, Entrenamiento, Evaluación, Despliegue**: Usa Python 3.10 para optimizaciones en `scikit-learn` y `tsfresh`.
- Asegúrate de que las versiones de Python estén instaladas y accesibles.
- Actualiza el `Jenkinsfile` con las rutas correctas de los ejecutables de Python.
- Verifica la compatibilidad de las dependencias en cada `requirements_*.txt`.

Para pruebas locales:
```bash
C:\Python39\python.exe -m venv venv_test
venv_test\Scripts\activate
pip install -r requirements\requirements_ingesta.txt
```

## Notas Importantes
- **Entornos Virtuales**: Se crea un `venv` específico para cada etapa durante la ejecución del pipeline, garantizando aislamiento y compatibilidad.
- **Kernels de Jupyter**: Los entornos virtuales se configuran como kernels para ejecución interactiva, facilitando el desarrollo y depuración.
- **Auditabilidad**: Cada etapa registra parámetros, métricas, artefactos y la versión de Python utilizada en MLflow.
- **Compatibilidad**: Algunas bibliotecas pueden requerir dependencias adicionales en Windows (e.g., `Microsoft Visual C++ Build Tools` para `tsfresh`).
- **Rendimiento**: Usa `dask` para procesar datasets grandes en paralelo.

## Solución de Problemas
- **Conflictos de Dependencias**: Si `pip install` falla, intenta con `pip install --no-cache-dir -r requirements_*.txt`.
- **Errores en Notebooks**: Revisa los logs en `logs/` y verifica que los datos en `data/raw/` estén en el formato correcto.
- **MLflow No Accesible**: Asegúrate de que el servidor de MLflow esté corriendo antes de ejecutar el pipeline o los notebooks.
- **Jupyter No Muestra Kernels**: Verifica que `ipykernel` esté instalado en el `venv` y que el kernel esté registrado con `python -m ipykernel install`.
