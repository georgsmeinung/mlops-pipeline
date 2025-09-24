# 1 Arquitectura propuesta (alto nivel)

1. **GoCD server** en una máquina (o VM). Agentes GoCD corriendo en las máquinas Windows de los data scientists o en una máquina Windows central (cada agente puede manejar múltiples pipelines). GoCD orquesta la ejecución: crea/actualiza venvs, ejecuta papermill contra notebooks y registra artefactos en MLflow.
2. **MLflow Tracking Server** (servicio Windows o proceso) con backend store (SQLite o SQL Server) y artifact store en disco compartido (carpeta accesible por agentes). MLflow sirve como «ledger» auditable de runs, métricas, artefactos y parámetros.
3. **Repositorios Git**: notebooks (sin outputs), scripts .py, YAML de etapas. GoCD toma commit SHA para cada run (se graba en MLflow).
4. **Notebooks Jupyter** por etapa (cada notebook hace su trabajo: ingest, limpieza, features, entrenamiento, evaluación, etc.). Se parametrizan y ejecutan por **papermill**.
5. **Script de creación de venvs** (`create_venv.py`) lee un YAML (por etapa) que especifica python-version y paquetes (lista). El script crea el venv usando el lanzador de Python `py` o `pyenv-win` si se desea automatizar instalación de Pythons. Luego instala paquetes, instala `ipykernel` y registra el kernel para Jupyter con un nombre claro (ej. `stage_ingest_py3.8`).

# 2 Flujo (step-by-step)

1. Data scientist hace commit con cambios, empuja a Git.
2. GoCD detecta commit y lanza pipeline. Cada **stage** en GoCD corresponde a una etapa MLOps (ingest, preprocess, features, train, eval, package).
3. Para cada etapa: GoCD ejecuta pasos (tasks):
   a. `python create_venv.py --spec specs/ingest.yaml --venv-root C:\ml_venvs` — crea/actualiza venv.
   b. `python run_notebook.py --notebook notebooks/ingest.ipynb --params-file params/ingest_params.yaml` — ejecuta notebook con papermill y dentro del notebook se usan llamadas a `mlflow` para loguear artefactos/metrics. El `run_notebook.py` debe inyectar el tracking URI y metadata (git SHA, stage).
4. **Papermill** ejecuta el notebook en ese venv (GoCD ejecuta el comando usando el intérprete del venv) y guarda el notebook ejecutado, que se sube como artifact a MLflow (o a almacenamiento de artefactos).
5. Al finalizar la etapa, se registran en MLflow: parámetros (entrada), métrica(s), artefactos (notebook ejecutado, `requirements.txt`/`pip_freeze.txt`, registro de paquetes y hashes), logs de stdout/stderr, y el Git commit SHA para trazabilidad. MLflow conserva todo para auditoría.

# 3 Esquema de YAML para especificar cada etapa

Archivo `specs/ingest.yaml` (ejemplo):

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
pip_extra_index: null   # opcional
pre_commands:
  - "chcp 65001"        # ejemplo si querés forzar UTF-8 en Windows
post_commands: []
kernel_display_name: "ingest (py3.8)"
```

Nota: lista explícita de librerías que pediste; las versiones exactas se manejan por etapa para evitar incompatibilidades.

# 4 Scripts claves (concepto + snippets)

A continuación ejemplos de scripts minimalistas — adáptalos a tu repositorio. Incluyo el `create_venv.py` y `run_notebook.py`.

## create\_venv.py (esqueleto)

```python
"""
create_venv.py --spec specs/ingest.yaml --venv-root C:\ml_venvs
"""
import argparse, subprocess, sys, yaml, os, shutil

def run(cmd, env=None):
    print(">", cmd)
    proc = subprocess.run(cmd, shell=True, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout.decode(errors='ignore'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--venv-root", required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(open(args.spec))
    venv_name = spec["venv_name"]
    py_ver = spec["python_version"]
    venv_path = os.path.join(args.venv_root, venv_name)

    # 1) Create venv using Python launcher (py -3.8 -m venv)
    # On Windows, 'py -3.8' will call the installed Python 3.8. Requires Python versions installed.
    create_cmd = f'py -{py_ver} -m venv "{venv_path}"'
    run(create_cmd)

    # 2) Upgrade pip and install wheel
    pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
    run(f'"{pip_exec}" install --upgrade pip setuptools wheel')

    # 3) Install packages from spec
    packages = spec.get("packages", [])
    if packages:
        pkg_list = " ".join(packages)
        run(f'"{pip_exec}" install {pkg_list}')

    # 4) Install ipykernel and register kernel
    run(f'"{pip_exec}" install ipykernel')
    python_exec = os.path.join(venv_path, "Scripts", "python.exe")
    kernel_name = venv_name
    display_name = spec.get("kernel_display_name", kernel_name)
    run(f'"{python_exec}" -m ipykernel install --user --name "{kernel_name}" --display-name "{display_name}"')

    # 5) Save pip freeze for audit
    run(f'"{pip_exec}" freeze > "{venv_path}_pip_freeze.txt"')

    print("Venv ready:", venv_path)

if __name__ == "__main__":
    main()
```

Comentarios importantes:

* En Windows recomiendo usar el **Python Launcher** (`py -3.8`) para crear venv con la versión específica si ya tenés esa versión instalada. Si necesitás instalar versiones de Python automáticamente, usar **pyenv-win** o instaladores silenciosos (winget/choco) es una opción. 

## run\_notebook.py (esqueleto)

```python
"""
run_notebook.py --venv C:\ml_venvs\ml_ingest_py38 --notebook notebooks/ingest.ipynb --output out/ingest_out.ipynb
"""
import argparse, subprocess, os, sys, yaml

def run(cmd, env=None):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True)
    parser.add_argument("--notebook", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--params-file", required=False)
    args = parser.parse_args()

    python_exec = os.path.join(args.venv, "Scripts", "python.exe")
    papermill = f'"{python_exec}" -m papermill "{args.notebook}" "{args.output}"'
    if args.params_file:
        papermill += f' -f "{args.params_file}"'

    # Optional: set MLflow tracking URI (env var) before running
    # os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-server:5000"
    run(papermill)

if __name__ == "__main__":
    main()
```

# 5 Cómo queda la auditoría (qué se guarda y dónde)

Para que cada ejecución sea auditable, graba lo siguiente en MLflow y como artefactos (archivo en disco):

* **Git commit SHA** (desde GoCD): lo pasás como param a papermill / MLflow.
* **Notebook original (clean)** y **notebook ejecutado** (papermill produce `out.ipynb`). Guardar ambos. 
* **Environment spec**: el `specs/*.yaml` usado.
* **requirements/pip-freeze** del venv (`pip freeze > pip_freeze.txt`) y/o `pip list --format=json`.
* **Python version** y path del venv (`sys.version`, `sys.executable`).
* **System logs** (stdout/stderr capturado por GoCD).
* **MLflow run**: métricas, parámetros, artefactos (notebook ejecutado, modelos, etc.). Todo esto queda indexado y recuperable. 

# 6 Gestión de múltiples versiones de Python en Windows

**pyenv-win**: permite instalar y gestionar múltiples Pythons programáticamente (similar a pyenv en Unix). Útil si necesitás que GoCD instale automáticamente Pythons no presentes. Requiere instalación y elevación inicial.
Decisión práctica: para un equipo de data scientists no tan técnicos, recomiendo **preinstalar** las versiones de Python más comunes en las máquinas agentes (o centralizar agentes con las versiones necesarias). Automatizar instalaciones con `winget` o `choco` es posible pero agrega complejidad.

# 7 GoCD: cómo modelar el pipeline (ideas concretas)

* **Pipeline**: `mlops_pipeline`
* **Stages**: `setup_env_ingest` -> `run_ingest` -> `setup_env_features` -> `run_features` -> `setup_env_train` -> `run_train` ...
* **Jobs/Tasks**: cada `setup_env_*` corre `create_venv.py --spec specs/<stage>.yaml`; cada `run_*` corre `run_notebook.py` apuntando al venv correspondiente.
* **Artifacts**: configurar GoCD para recoger artefactos (notebook ejecutado, pip\_freeze, logs) y subirlos al artifact store; además se suben a MLflow en cada run.

# 8 Pautas prácticas y recomendaciones (problemas y mitigaciones)

* **Incompatibilidades entre paquetes**: muchas de las librerías que pediste tienen dependencias complejas. Evitar forzar versiones globales; especificar versiones por etapa y testear localmente.
* **Tamaño / tiempo de instalación**: instalar docenas de librerías en cada run es lento. Estrategia: crear venvs «persistentes» por etapa (no recrear siempre) y sólo actualizar si cambia el YAML (GoCD puede comparar checksum del YAML y recrear solo si cambió).
* **Seguridad / privilegios**: registro de kernels ipykernel --user no requiere admin. Instalar Python a nivel sistema o pyenv-win puede requerir permisos.
* **MLflow artifact store**: para auditoría robusta, usar un disco compartido con backups o un storage central.
* **Testing local**: proveer scripts `dev_bootstrap.bat` para que el data scientist pueda crear venvs y kernels localmente (misma lógica que GoCD).

# 9 Ejemplo de minimal MLflow usage dentro del notebook

Dentro de la primera celda del notebook:

```python
import mlflow, mlflow.sklearn, getpass, platform, json, subprocess, sys

mlflow.set_tracking_uri("file:///C:/mlflow_artifacts")  # o http://mlflow-server:5000
mlflow.set_experiment("ingest-experiment")

with mlflow.start_run(run_name="ingest"):
    mlflow.log_param("git_commit", "<GIT_SHA_FROM_ENV>")
    mlflow.log_param("stage", "ingest")
    mlflow.log_param("python_version", sys.version)
    # guardar pip freeze
    import pkg_resources, io
    freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode()
    mlflow.log_text(freeze, "pip_freeze.txt")
    # ... resto del notebook ... 
    mlflow.log_artifact("out/ingest_out.ipynb")
```

(Mantener este fragmento en la plantilla de notebook para asegurar consistencia).

# 10 Comprobaciones y referencias rápidas

* Registrar kernel con ipykernel: `python -m ipykernel install --user --name "venvname" --display-name "Display Name"`.
* Papermill doc y uso de parámetros: papermill CLI / API.
* MLflow Projects / Pipelines para reproducibilidad y tracking.
* GoCD Agent Windows install (para desplegar agentes Windows).
* pyenv-win para multi-versiones en Windows.

# 11 Lista de chequeo para puesta en marcha (quick checklist)

1. Instalar GoCD server + al menos 1 agente Windows (documentación oficial). 
2. Instalar Python Launcher y las versiones de Python requeridas o pyenv-win. 
3. Clonar repo con notebooks, specs y scripts.
4. Configurar MLflow Tracking Server (SQLite para PoC). 
5. Crear pipelines en GoCD que llamen a `create_venv.py` y `run_notebook.py`.
6. Probar con una etapa simple (ingest) y revisar que MLflow tiene run + artefactos.

# 12 Riesgos técnicos y alternativas

* Si la instalación de múltiples Pythons en cada estación resulta engorrosa, la alternativa más simple y robusta es: **centralizar agentes** en una máquina Windows con todas las versiones instaladas, y que los DS trabajen en sus máquinas localmente sólo para prototipado.
* Si luego querés escalar a producción, pasar a contenedores o entornos administrados (Azure ML, SageMaker) facilitará despliegues reproducibles — pero entiendo que querés evitar Docker ahora.