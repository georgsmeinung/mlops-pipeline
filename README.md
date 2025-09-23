# mlops-pipeline con MLflow, Jenkins y Entornos Virtuales Python en Windows

## Descripción General

Este proyecto implementa una solución de **MLOps auditable** en Windows, diseñada para equipos de ciencia de datos que prefieren trabajar directamente con **Jupyter Notebooks**. El flujo completo está orquestado con **MLflow** y **Jenkins**, permitiendo:

* Auditoría de cada etapa del pipeline de ML.
* Ejecución interactiva en notebooks.
* Creación automática de entornos virtuales (`venv`) con dependencias específicas por etapa.
* Gestión de versiones de Python y librerías mediante archivos **YAML**.
* Integración con Jenkins para la automatización y trazabilidad.

## Componentes Clave

### 1. Orquestación del Pipeline

* **MLflow** gestiona:

  * Tracking de experimentos.
  * Registro de modelos.
  * Ejecución de pipelines.

### 2. Automatización DevOps

* **Jenkins** controla la ejecución del pipeline:

  * Disparadores manuales o automáticos (push a `main`, merge PR, cron jobs).
  * Ejecución de scripts `.bat` para creación de entornos.
  * Llamado a notebooks mediante `papermill` o `nbconvert`.

### 3. Gestión de Entornos

* Cada etapa del pipeline define sus requisitos en un archivo YAML:

  ```yaml
  python_version: "3.10"
  dependencies:
    - scikit-learn==1.5.0
    - pycaret
    - ydata-profiling
  ```
* Script `.py` genera el entorno virtual (`python -m venv`) y lo registra como kernel Jupyter.
* Cada entorno se activa dinámicamente en la etapa correspondiente.

### 4. Librerías AutoML soportadas

Los entornos pueden incluir herramientas como:

* `autofeat`
* `autoviz`
* `dask`
* `dtale`
* `featuretools`
* `scikit-learn`
* `pycaret`
* `sweetviz`
* `tabulate`
* `tsfresh`
* `ydata-profiling`

### 5. Auditoría y Trazabilidad

* Cada notebook se ejecuta con parámetros inyectados desde Jenkins.
* Resultados, métricas y modelos se registran automáticamente en **MLflow**.
* Se conserva historial de versiones de código, entornos y outputs.

## Estructura del Repositorio

```
mlops-pipeline/
├── notebooks/
│   ├── 01_ingesta.ipynb
│   ├── 02_preprocesamiento.ipynb
│   ├── 03_entrenamiento.ipynb
│   └── 04_evaluacion.ipynb
├── environments/
│   ├── 01_ingesta.yaml
│   ├── 02_preprocesamiento.yaml
│   ├── 03_entrenamiento.yaml
│   └── 04_evaluacion.yaml
├── scripts/
│   ├── create_env.py
│   ├── run_notebook.py
│   ├── create_env.bat
│   └── run_pipeline.bat
├── jenkins/
│   └── Jenkinsfile
├── mlruns/   # Tracking MLflow
└── README.md
```

## Flujo de Ejecución

1. El usuario actualiza código o notebooks y hace `git push`.
2. Jenkins detecta cambios y ejecuta el pipeline:

   * Lee especificaciones YAML de cada etapa.
   * Crea el `venv` correspondiente.
   * Registra el kernel en Jupyter.
   * Ejecuta el notebook con parámetros.
3. MLflow guarda resultados y métricas.
4. El equipo puede revisar resultados en MLflow UI o Jupyter.

## Requisitos Previos

* **Windows 10/11**
* **Python (múltiples versiones instaladas en el sistema)**
* **Jenkins** instalado como servicio
* **MLflow** instalado globalmente
* **Jupyter Notebook/Lab** instalado globalmente

## Ejemplo de Uso

Crear entorno para la etapa de entrenamiento:

```bash
scripts\create_env.bat environments\03_entrenamiento.yaml
```

Ejecutar pipeline completo:

```bash
scripts\run_pipeline.bat
```

## Posibles Futuras Extensiones

* Integración con Metabase/PowerBI para visualización de resultados.
* Control de versiones de datasets con DVC.
* Soporte para ejecución distribuida con Dask.
