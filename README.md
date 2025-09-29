# MLOps Pipeline en Windows con GoCD, MLflow y Jupyter

Este repositorio contiene una solución **MLOps auditable** para equipos de ciencia de datos que trabajan en **Windows**, sin necesidad de contenedores (Docker/Kubernetes).
El diseño permite ejecutar pipelines reproducibles con **GoCD** y **MLflow**, creando entornos Conda específicos por etapa mediante un archivo YAML, con notebooks ejecutados de forma automatizada usando **papermill** y disponibles como kernels de **Jupyter** para prototipado interactivo.

---

## 🚀 Características principales

* **Orquestación con GoCD**: cada etapa del pipeline es un *stage* en GoCD.
* **Trazabilidad con MLflow**: parámetros, métricas, notebooks ejecutados y entornos quedan registrados.
* **Entornos aislados por etapa**: cada etapa define su propio entorno Conda y versión de Python mediante un archivo YAML.
* **Compatibilidad con múltiples versiones de Python**: administradas mediante Conda.
* **Automatización de notebooks**: notebooks ejecutados con [papermill](https://papermill.readthedocs.io/).
* **Prototipado interactivo**: los entornos creados se registran como kernels de Jupyter.
* **Auditoría completa**: se guarda YAML de especificación, `pip freeze`, notebooks ejecutados y logs de GoCD/MLflow.

---

## 📂 Estructura del repositorio

```
.
├── notebooks/           # Notebooks Jupyter (uno por etapa del pipeline)
│   ├── ingest.ipynb
│   ├── features.ipynb
│   └── train.ipynb
│
├── specs/               # Archivos YAML con especificaciones de entornos por etapa
│   ├── ingest.yaml
│   ├── features.yaml
│   └── train.yaml
│
├── params/              # Archivos YAML con parámetros de notebooks
│   ├── ingest_params.yaml
│   └── train_params.yaml
│
├── scripts/             # Scripts de automatización
│   ├── create_conda_env.py   # Crea entornos Conda desde YAML y registra kernel Jupyter
│   ├── run_notebook.py       # Ejecuta un notebook con papermill en un entorno Conda
│   └── manage_conda_envs.py # Lista y borra entornos Conda y sus kernels
│
├── gocd/                # Ejemplos de configuración de pipelines GoCD
│   └── pipeline_config.xml
│
└── README.md            # Este archivo
```

---

## 📑 Ejemplo de especificación de etapa (YAML)

`specs/ingest.yaml`:

```yaml
stage: ingest
python_version: "3.8"
venv_name: "ml_ingest_py38"
packages:
  - mlflow==1.29.0
  - papermill>=2.4.0
  - pandas
  - requests
  - autofeat
  - autoviz
  - dask
  - dtale
  - featuretools
  - scikit-learn
  - pycaret
  - sweetviz
  - tabulate
  - tsfresh
  - ydata-profiling
kernel_display_name: "Ingest (py3.8)"
```

---

## ⚙️ Uso local (prototipado)

1. **Crear entorno Conda de una etapa**:

```bash
python scripts/create_conda_env.py --spec specs/ingest.yaml --env-root C:\ml_envs
```

Esto:

* Crea `C:\ml_envs\ml_ingest_py38\`
* Instala todas las librerías con `pip`
* Instala `ipykernel` y registra kernel Jupyter con nombre `Ingest (py3.8)`
* Exporta `pip_freeze.txt` para auditoría

2. **Ejecutar un notebook con papermill**:

```bash
python scripts/run_notebook.py \
    --conda-env C:\ml_envs\ml_ingest_py38 \
    --notebook notebooks/ingest.ipynb \
    --output out/ingest_out.ipynb \
    --params-file params/ingest_params.yaml
```

3. **Abrir Jupyter Lab/Notebook** y seleccionar el kernel `Ingest (py3.8)` para edición interactiva.

---

## 🔄 Flujo en GoCD

* Cada pipeline en GoCD incluye dos *jobs* por etapa:

  1. `setup_env_stageX`: ejecuta `create_conda_env.py` para la etapa.
  2. `run_stageX`: ejecuta `run_notebook.py` con el entorno Conda recién creado.

* GoCD recoge artefactos (`out.ipynb`, `pip_freeze.txt`) y los sube a MLflow junto con métricas y parámetros.

---

## 🗄️ Auditoría y MLflow

Cada run en MLflow incluye:

* Parámetros (stage, git SHA, etc.)
* Notebook ejecutado (`*_out.ipynb`)
* Especificación YAML de la etapa
* `pip_freeze.txt`
* Métricas y resultados del notebook

---

## 📌 Requisitos previos

* Windows 10/11
* [GoCD Server & Agent](https://www.gocd.org/download/) instalados en Windows
* [MLflow](https://mlflow.org/) instalado y configurado con backend store (ej: SQLite)
* [Miniconda o Anaconda](https://docs.conda.io/en/latest/miniconda.html) para manejar múltiples versiones de Python
* Jupyter Notebook / Lab instalado en el sistema base
* Git para control de versiones

---

## ✅ Checklist para despliegue inicial

1. Instalar Conda y las versiones de Python necesarias (ej. 3.8, 3.9, 3.10).
2. Configurar MLflow tracking server (ejemplo: `mlflow ui --backend-store-uri sqlite:///mlflow.db`).
3. Crear pipeline en GoCD con stages `setup_env` + `run_notebook` para cada etapa.
4. Ejecutar primer pipeline (`ingest`) y validar que MLflow registra resultados.
5. Confirmar que los kernels de Jupyter aparecen disponibles para edición manual.

---

## 🔮 Futuras mejoras

* Cache de entornos Conda para reducir tiempos de instalación.
* Integración con almacenamiento remoto de artefactos (S3, GCS, Azure Blob).
* Soporte opcional para instalación automática de Python con `winget` o `choco`.
* Posible migración a contenedores en una etapa posterior (no requerido en este diseño).
