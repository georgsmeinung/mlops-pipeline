# 1 Arquitectura propuesta (alto nivel)

1. **GoCD server** en una máquina (o VM). Agentes GoCD corriendo en máquinas Windows de los data scientists o en un agente central. GoCD orquesta la ejecución: crea/actualiza entornos Conda, ejecuta papermill contra notebooks y registra artefactos en MLflow.
2. **MLflow Tracking Server** con backend store (SQLite o SQL Server) y artifact store en disco compartido. MLflow sirve como «ledger» auditable de runs, métricas, artefactos y parámetros.
3. **Repositorios Git**: notebooks (sin outputs), scripts `.py`, YAML de etapas. GoCD toma commit SHA para cada run (grabado en MLflow).
4. **Notebooks Jupyter** por etapa (ingest, limpieza, features, entrenamiento, evaluación, etc.). Se parametrizan y ejecutan por **papermill**.
5. **Script de creación de entornos Conda** (`create_conda_env.py`) lee un YAML por etapa que especifica `python_version` y `packages`. El script crea un entorno Conda con `-n` o path opcional, instala paquetes con `pip`, instala `ipykernel` y registra el kernel para Jupyter (`stage_ingest_py38`).

---

# 2 Flujo (step-by-step)

1. Data scientist hace commit y push a Git.
2. GoCD detecta commit y lanza pipeline. Cada **stage** en GoCD corresponde a una etapa MLOps.
3. Para cada etapa, GoCD ejecuta pasos:
   a. `python scripts/create_conda_env.py --spec specs/ingest.yaml --env-root C:\ml_envs` — crea/actualiza el entorno Conda.
   b. `python scripts/run_notebook.py --conda-env C:\ml_envs\ml_ingest_py38 --notebook notebooks/ingest.ipynb --params-file params/ingest_params.yaml` — ejecuta notebook con papermill, usando el kernel Conda. Dentro del notebook se usan llamadas a MLflow para loguear artefactos y métricas.
4. **Papermill** ejecuta el notebook en el entorno Conda y guarda el notebook ejecutado, que se sube como artifact a MLflow o almacenamiento compartido.
5. Al finalizar la etapa, se registran en MLflow: parámetros, métricas, artefactos (notebook ejecutado, `pip_freeze.txt`), logs de stdout/stderr y Git commit SHA para trazabilidad.

---

# 3 Esquema de YAML para cada etapa

`specs/ingest.yaml` (ejemplo):

```yaml
stage: ingest
python_version: "3.8"
venv_name: "ml_ingest_py38"   # se usa como nombre de entorno Conda
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
pip_extra_index: null
pre_commands:
  - "chcp 65001"
post_commands: []
kernel_display_name: "ingest (py3.8)"
```

Nota: `venv_name` ahora representa el nombre del entorno Conda.

---

# 4 Scripts claves

## create_conda_env.py (esqueleto)

```python
"""
create_conda_env.py --spec specs/ingest.yaml --env-root C:\ml_envs
"""
import argparse, subprocess, yaml, os

def run(cmd):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--env-root", required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(open(args.spec))
    env_name = spec["venv_name"]
    py_ver = spec["python_version"]
    env_path = os.path.join(args.env_root, env_name)

    # Crear entorno Conda con nombre (-n) o path (-p)
    run(f'conda create -y -p "{env_path}" python={py_ver}')

    # Instalar paquetes con pip
    packages = spec.get("packages", [])
    if packages:
        pkg_list = " ".join(packages)
        run(f'conda run -p "{env_path}" pip install {pkg_list}')

    # Instalar ipykernel y registrar kernel
    run(f'conda run -p "{env_path}" pip install ipykernel')
    display_name = spec.get("kernel_display_name", env_name)
    run(f'conda run -p "{env_path}" python -m ipykernel install --user --name "{env_name}" --display-name "{display_name}"')

    # Guardar freeze
    run(f'conda run -p "{env_path}" pip freeze > "{env_path}_pip_freeze.txt"')

if __name__ == "__main__":
    main()
```

---

## run_notebook.py (esqueleto)

```python
"""
run_notebook.py --conda-env C:\ml_envs\ml_ingest_py38 --notebook notebooks/ingest.ipynb --output out/ingest_out.ipynb
"""
import argparse, subprocess, os

def run(cmd):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conda-env", required=True)
    parser.add_argument("--notebook", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--params-file", required=False)
    args = parser.parse_args()

    cmd = f'conda run -p "{args.conda_env}" -m papermill "{args.notebook}" "{args.output}"'
    if args.params_file:
        cmd += f' -f "{args.params_file}"'

    run(cmd)

if __name__ == "__main__":
    main()
```

---

# 5 Auditoría

* Git commit SHA
* Notebook original y ejecutado (`out.ipynb`)
* YAML de la etapa
* `pip freeze` del entorno Conda
* Python version y path (`sys.version`, `sys.executable`)
* Logs stdout/stderr
* MLflow run (parámetros, métricas, artefactos)

---

# 6 Gestión de múltiples versiones de Python

* **Conda** administra versiones de Python. No se necesita pyenv-win.
* Recomendación: mantener un conjunto de entornos base persistentes por etapa; actualizarlos sólo cuando cambie el YAML.

---

# 7 GoCD: modelado del pipeline

* **Pipeline**: `mlops_pipeline`
* **Stages**: `setup_env_ingest` → `run_ingest` → `setup_env_features` → `run_features` → `setup_env_train` → `run_train` …
* **Jobs/Tasks**:

  * `setup_env_*`: `create_conda_env.py --spec specs/<stage>.yaml`
  * `run_*`: `run_notebook.py --conda-env C:\ml_envs\<env_name> ...`
* Artefactos: notebook ejecutado, `pip_freeze.txt`, logs, subidos a MLflow.

---

# 8 Pautas prácticas

* Evitar conflictos de paquetes: definir versiones por etapa.
* Crear entornos persistentes, no recrear siempre.
* Registrar kernels con `--user`.
* Usar disco compartido para MLflow artifact store.
* Scripts `dev_bootstrap.bat` permiten crear entornos Conda y kernels localmente.

---

# 9 Ejemplo minimal de MLflow en notebook

```python
import mlflow, sys, subprocess

mlflow.set_tracking_uri("file:///C:/mlflow_artifacts")
mlflow.set_experiment("ingest-experiment")

with mlflow.start_run(run_name="ingest"):
    mlflow.log_param("git_commit", "<GIT_SHA_FROM_ENV>")
    mlflow.log_param("stage", "ingest")
    mlflow.log_param("python_version", sys.version)
    freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode()
    mlflow.log_text(freeze, "pip_freeze.txt")
    mlflow.log_artifact("out/ingest_out.ipynb")
```

---

# 10 Lista de chequeo para puesta en marcha

1. Instalar GoCD server + agente Windows.
2. Instalar Conda y versiones de Python necesarias.
3. Clonar repo con notebooks, specs y scripts.
4. Configurar MLflow Tracking Server.
5. Crear pipelines en GoCD con `create_conda_env.py` y `run_notebook.py`.
6. Probar una etapa y validar artefactos en MLflow.

---

# 11 Riesgos técnicos y alternativas

* Centralizar agentes con todos los entornos Conda para evitar instalación masiva de Pythons.
* Escalar a producción: considerar contenedores o entornos administrados (Azure ML, SageMaker), manteniendo reproducibilidad.
