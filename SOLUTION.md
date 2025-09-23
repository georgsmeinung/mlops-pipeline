# 1 — Arquitectura propuesta (alto nivel)

* Repositorio Git con ramas `main` / `dev`. Estructura mínima:

  ```
  /mlops-repo
    /notebooks
      01-data-prep.ipynb
      02-feature-eng.ipynb
      03-train.ipynb
      04-eval.ipynb
    /env_specs
      stage_data_prep.yaml
      stage_feature_eng.yaml
      stage_train.yaml
      stage_eval.yaml
    /scripts
      create_venv.bat
      create_venv.py
      run_stage.bat
      run_notebook.py
    /mlflow
      (opcional: lugar para artifacts por defecto)
    Jenkinsfile
    MLproject (plantilla para MLflow Projects opcional)
  ```
* Jenkins (instalado en Windows) ejecuta pipelines declarativos que llaman a los `.bat`.
* MLflow tracking server corriendo en Windows (servicio o proceso) con `sqlite` (o SQL Server) como backend store y un artifact root en carpeta compartida. Cada run corresponde a la ejecución de un notebook.
* Auditoría: cada notebook (o la wrapper `run_notebook.py`) registra al inicio:

  * git commit (sha)
  * python version y path del venv
  * `pip freeze` (guardado como artifact)
  * timestamp y run\_id (MLflow)
  * hashes o checksum del notebook original
* Parametrización y ejecución: usar `papermill` para ejecutar notebooks con parámetros desde la línea (ideal para reproducibilidad). `papermill` permite conservar el notebook ejecutado como artifact.

---

# 2 — Convenciones y conceptos clave

* **Each stage YAML**: contiene `name`, `python_exe` (ruta al ejecutable python que se usará para crear el venv), `packages` (lista pip), `notebook` (ruta), `kernel_name`, `env_dir`.
* **Multiple Python versions**: instala varios intérpretes Python en Windows (ej. `C:\Python37\python.exe`, `C:\Python38\python.exe`, `C:\Python39\python.exe`, `C:\Python310\python.exe`) — el YAML referencia el path para la etapa. El script usa ese `python_exe -m venv`.
* **No Docker**: todo local en Windows; Jenkins agentes Windows.
* **Jupyter kernels**: el script registrará `ipykernel` dentro de cada `venv` con un `display_name` legible por etapa.
* **MLflow**: orquesta y registra; cada pipeline step llama a MLflow para iniciar run, y el notebook / wrapper sube artifacts (notebook ejecutado, pip-freeze, modelos, métricas).
* **Notebooks como código**: versionados en Git; ejecución automatizada via `papermill` con parámetros.

---

# 3 — YAML de ejemplo (spec de etapa)

Crea `env_specs/stage_train.yaml` (ejemplo):

```yaml
name: train
python_exe: C:\Python310\python.exe
env_dir: .venv_train
kernel_name: mlops-train-py310
notebook: notebooks/03-train.ipynb
packages:
  - mlflow
  - papermill
  - jupyter
  - ipykernel
  - scikit-learn
  - pandas
  - numpy
  - pycaret
  - autofeat
  - autoviz
  - dask
  - dtale
  - featuretools
  - sweetviz
  - tabulate
  - tsfresh
  - ydata-profiling
  - warnings ; # (nota: warnings es módulo stdlib, está listado para claridad)
  - matplotlib
  - cloudpickle
  - tqdm
  - pip>=22.0
```

(Repite / adapta para otras etapas cambiando `python_exe`, `env_dir`, `packages`.)

---

# 4 — `create_venv.bat` (caller simple)

Archivo `scripts/create_venv.bat`:

```bat
@echo off
REM usage: create_venv.bat ..\env_specs\stage_train.yaml
SETLOCAL
if "%~1"=="" (
  echo Uso: create_venv.bat path\to\spec.yaml
  exit /b 1
)
python scripts\create_venv.py %~1
IF %ERRORLEVEL% NEQ 0 (
  echo create_venv fallo con codigo %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)
echo Entorno creado correctamente.
ENDLOCAL
```

Este `.bat` asume que hay un Python "gestor" disponible en PATH (por ejemplo Python 3.10) para ejecutar `create_venv.py`. Ese script se encargará de usar el `python_exe` indicado dentro del YAML para crear el venv real.

---

# 5 — `create_venv.py` (creador robusto en Python)

Archivo `scripts/create_venv.py`:

```python
# create_venv.py
import sys, os, subprocess, yaml, shutil, hashlib
from pathlib import Path

def read_spec(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run(cmd, env=None):
    print("RUN:", " ".join(cmd))
    res = subprocess.run(cmd, shell=False, env=env)
    if res.returncode != 0:
        raise SystemExit(res.returncode)

def write_requirements(reqs, dest):
    with open(dest, 'w', encoding='utf-8') as f:
        for r in reqs:
            f.write(str(r) + "\n")

def main(spec_path):
    spec = read_spec(spec_path)
    py = spec.get('python_exe')
    env_dir = Path(spec.get('env_dir', '.venv_' + spec['name']))
    packages = spec.get('packages', [])
    kernel_name = spec.get('kernel_name', spec['name'] + '-kernel')

    if not py or not Path(py).exists():
        print(f"ERROR: python_exe {py} no existe.")
        raise SystemExit(2)

    # 1) create venv using the selected python
    if env_dir.exists():
        print("El venv ya existe, lo eliminaremos y recrearemos:", env_dir)
        shutil.rmtree(env_dir)
    run([py, "-m", "venv", str(env_dir)])

    # 2) pip upgrade
    pip_exe = env_dir / "Scripts" / "pip.exe"
    py_in_venv = env_dir / "Scripts" / "python.exe"
    run([str(pip_exe), "install", "--upgrade", "pip", "setuptools", "wheel"])

    # 3) write a requirements file and install
    req_file = env_dir / "requirements.txt"
    write_requirements(packages, req_file)
    run([str(pip_exe), "install", "-r", str(req_file)])

    # 4) install ipykernel (might already be in packages) and register kernel
    run([str(py_in_venv), "-m", "ipykernel", "install", "--user", "--name", kernel_name, "--display-name", f"mlops-{spec['name']} ({kernel_name})"])

    # 5) save pip freeze for audit
    freeze_file = env_dir / "pip-freeze.txt"
    with open(freeze_file, 'wb') as f:
        p = subprocess.run([str(pip_exe), "freeze"], stdout=subprocess.PIPE)
        f.write(p.stdout)

    print("VENV creado:", env_dir)
    print("Kernel registrado:", kernel_name)
    print("Pip freeze guardado en:", freeze_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: create_venv.py path\\to\\spec.yaml")
        raise SystemExit(1)
    main(sys.argv[1])
```

Notas:

* Requiere `pyyaml` para el script gestor (el `python` que ejecuta `create_venv.py`). Si ese Python gestor no tiene `pyyaml`, instálalo con `pip install pyyaml`.
* El script usa el `python_exe` del YAML para crear el venv (así puedes tener varios Pythons instalados).

---

# 6 — Registrar kernel y usarlo interactivo

* El script ya registra el kernel con `ipykernel`. En Jupyter Desktop / Lab aparecerá `mlops-<stage> (kernel_name)`.
* El cientista puede abrir el notebook y seleccionar el kernel para prototipado interactivo.

---

# 7 — Ejecutar notebook y auditar: `run_stage.bat` + `run_notebook.py`

`run_stage.bat`:

```bat
@echo off
REM usage: run_stage.bat env_specs\stage_train.yaml
SETLOCAL
if "%~1"=="" (
  echo Uso: run_stage.bat path\to\spec.yaml
  exit /b 1
)
python scripts\run_notebook.py %~1
IF %ERRORLEVEL% NEQ 0 (
  echo run_stage fallo con codigo %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)
echo Ejecución completada.
ENDLOCAL
```

`run_notebook.py` — ejecuta con papermill y registra en MLflow:

```python
# run_notebook.py
import sys, os, subprocess, yaml, json
from pathlib import Path
import time
import subprocess

def load_spec(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run(cmd, env=None):
    print("RUN:", " ".join(cmd))
    res = subprocess.run(cmd, shell=False, env=env)
    if res.returncode != 0:
        raise SystemExit(res.returncode)

def main(spec_path):
    spec = load_spec(spec_path)
    env_dir = Path(spec.get('env_dir'))
    notebook = Path(spec.get('notebook'))
    name = spec.get('name')
    if not env_dir.exists():
        raise SystemExit(f"Venv {env_dir} no encontrado. Cree el venv primero.")

    py_in_venv = env_dir / "Scripts" / "python.exe"
    pip_freeze = env_dir / "pip-freeze.txt"
    # Ensure papermill is available
    pm = env_dir / "Scripts" / "papermill.exe"
    if not pm.exists():
        # try python -m papermill
        pm_cmd = [str(py_in_venv), "-m", "papermill"]
    else:
        pm_cmd = [str(pm)]

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_nb = notebook.with_name(notebook.stem + f"_executed_{timestamp}.ipynb")

    # metadata to pass as papermill params
    params = {
        "mlflow_tracking_uri": os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"),
        "stage_name": name,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip() if Path(".git").exists() else "no-git",
        "venv_path": str(env_dir),
        "venv_pip_freeze": str(pip_freeze),
    }
    # build papermill command
    cmd = pm_cmd + [str(notebook), str(out_nb), "-p", "params", json.dumps(params)]
    # Alternative: pass parameters as multiple -p key val pairs; here we pass one param named 'params'
    run(cmd)

    # After execution, log artifacts to mlflow using CLI in the venv python:
    # create a small python snippet to call mlflow.log_artifact etc.
    # For simplicity we call mlflow CLI (if installed) or a helper script.
    helper = Path("scripts") / "mlflow_helper.py"
    run([str(py_in_venv), str(helper), str(out_nb), str(pip_freeze), name])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: run_notebook.py path\\to\\spec.yaml")
        raise SystemExit(1)
    main(sys.argv[1])
```

`mlflow_helper.py` (simple, as artifact uploader; se queda en `scripts`):

```python
# mlflow_helper.py
import sys
import mlflow
from pathlib import Path

def main():
    if len(sys.argv) < 4:
        print("Uso: mlflow_helper.py executed_notebook pip_freeze stage_name")
        raise SystemExit(1)
    executed_notebook = Path(sys.argv[1])
    pip_freeze = Path(sys.argv[2]) if sys.argv[2] else None
    stage = sys.argv[3]

    mlflow.set_tracking_uri("http://localhost:5000")
    with mlflow.start_run(run_name=f"notebook-{stage}-{executed_notebook.stem}"):
        mlflow.log_param("stage", stage)
        mlflow.log_artifact(str(executed_notebook))
        if pip_freeze and pip_freeze.exists():
            mlflow.log_artifact(str(pip_freeze))
        # could also log model files, metrics written by the notebook into a known path, etc.

if __name__ == "__main__":
    main()
```

Notas:

* `run_notebook.py` asume que `papermill` está instalado en el venv. Si no lo está, `create_venv.py` debe incluirlo.
* `mlflow_helper.py` usa la API `mlflow` para crear un run y subir artifacts; debe ejecutarse con el `python` del venv para usar la misma instalación `mlflow`.

---

# 8 — Plantilla MLproject (opcional) para MLflow Projects

Archivo `MLproject` en repo raíz:

```yaml
name: mlops-pipeline
conda_env: null
# usamos venv no conda, pero MLproject puede ejecutar comando
entry_points:
  train:
    parameters:
      spec_path: {type: str, default: "env_specs/stage_train.yaml"}
    command: "python scripts/run_notebook.py {spec_path}"
  data_prep:
    parameters:
      spec_path: {type: str, default: "env_specs/stage_data_prep.yaml"}
    command: "python scripts/run_notebook.py {spec_path}"
```

Con esto, MLflow puede lanzar `mlflow run . -e train -P spec_path=...`.

---

# 9 — Jenkinsfile (Declarative, Windows agent)

Ejemplo `Jenkinsfile` (coloca en repo):

```groovy
pipeline {
  agent { label 'windows' } // asegúrate de tener un node Windows con ese label
  options {
    timestamps()
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Create venvs') {
      steps {
        bat 'scripts\\create_venv.bat env_specs\\stage_data_prep.yaml'
        bat 'scripts\\create_venv.bat env_specs\\stage_feature_eng.yaml'
        bat 'scripts\\create_venv.bat env_specs\\stage_train.yaml'
        bat 'scripts\\create_venv.bat env_specs\\stage_eval.yaml'
      }
    }
    stage('Run pipeline (MLflow orchestrado)') {
      steps {
        // Ejecuta etapas en secuencia; puedes paralelizar si es seguro
        bat 'scripts\\run_stage.bat env_specs\\stage_data_prep.yaml'
        bat 'scripts\\run_stage.bat env_specs\\stage_feature_eng.yaml'
        bat 'scripts\\run_stage.bat env_specs\\stage_train.yaml'
        bat 'scripts\\run_stage.bat env_specs\\stage_eval.yaml'
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: '**/*_executed_*.ipynb', allowEmptyArchive: true
      junit allowEmptyResults: true, testResults: '**/test-reports/*.xml'
    }
  }
}
```

Notas:

* Jenkins debe ejecutar con credenciales que tengan permisos para crear kernels ipykernel (instalación `--user`), o registra en sistema si prefieres `--prefix`.
* Asegúrate que `git` esté en PATH en el agente para que `git rev-parse HEAD` funcione.

---

# 10 — MLflow tracking server en Windows (mínimo, para pruebas)

Ejecuta en la máquina que ejerce de tracking server (puede ser la misma del Jenkins agent, o otra accesible):

```cmd
set MLFLOW_HOME=C:\mlflow_server
mkdir %MLFLOW_HOME%
cd %MLFLOW_HOME%
REM create a sqlite file and folder for artifacts
python -m pip install mlflow
mkdir artifacts
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root %MLFLOW_HOME%/artifacts --host 0.0.0.0 --port 5000
```

Sugerencia: configurar este comando como un servicio de Windows (por ejemplo NSSM) para que siempre esté levantado.

---

# 11 — Notebooks: snippet recomendado al inicio (para auditar)

En cada notebook, en la primera celda (ejecutable), usa algo así (Python):

```python
# header_audit.py (snippet to paste in first cell)
import mlflow, os, sys, json, subprocess, time
from pathlib import Path

def capture_env_info():
    info = {}
    info['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    info['python_executable'] = sys.executable
    info['python_version'] = sys.version
    try:
        info['git_commit'] = subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
    except Exception:
        info['git_commit'] = 'no-git'
    try:
        info['notebook_path'] = __file__
    except:
        info['notebook_path'] = None
    return info

env_info = capture_env_info()
print(env_info)
# Start MLflow run if not already started by wrapper
try:
    mlflow.active_run()
except Exception:
    pass
# Save env_info as artifact later via mlflow.log_dict if desired
```

(Se puede ejecutar desde la wrapper; la idea es que cada notebook documente env y git.)

---

# 12 — Manejo de incompatibilidades de versiones Python

* **Estrategia**: instala en la máquina los Pythons requeridos (inversión única). Cada YAML apunta a su `python_exe`. Esto evita necesitar `pyenv` o contenedores.
* **Alternativa ligera**: usar `venv` + `pip` con `--constraint` files o wheels precompiladas si hay paquetes con compilación (por ejemplo `tsfresh` o `dask`). Para paquetes con dependencias nativas, procura tener Microsoft Build Tools si hace falta.
* Documenta en README qué Python versions están soportadas y proporciona links / instaladores de Python embebidos (ej. instaladores embebidos de python.org).

---

# 13 — Buenas prácticas de auditoría (implementarlas en el repo)

* En cada run, guardar como artifacts:

  * notebook ejecutado (`*_executed_*.ipynb`)
  * `pip-freeze.txt` del venv
  * `git_commit` y `git_diff` (si hay cambios no committeados)
  * logs y stdout/stderr (capturados por Jenkins)
  * métricas y modelos (pickle, joblib, ONNX)
* Forzar que notebooks usen MLflow para loggear métricas y parámetros en celdas clave.
* Mantener una convención estricta de nombres y una carpeta `artifacts/<run_id>/...` si quieres redundancia local además de MLflow.

---

# 14 — Consideraciones operativas / riesgos y mitigaciones

* Riesgo: dependencias que requieren compilación (p. ej. `tsfresh`) fallan en Windows. Mitigación: usar ruedas precompiladas (`pip wheel`) o MS Build Tools, o usar versiones de paquete conocidas buenas. Documenta en cada spec `notes` con instrucciones.
* Riesgo: múltiples Pythons requieren instalación administradora. Documentar y proveer scripts de instalación o indicar instaladores.
* Riesgo: Jenkins agent que corre múltiples venvs puede consumir disco. Mantener limpieza periódica.
* Riesgo: ipykernel `--user` instala en perfil del usuario que ejecuta Jenkins; si Jenkins corre bajo servicio distinto, registrar kernels en un path accesible o configurar Jupyter para usar kernels desde cada venv (jupyter lab/spawn de kernels se basará en `~/.local/...`). Alternativa: no registrar kernel y usar `python -m papermill` para ejecución automática; registro es solo para prototipado interactivo por el data scientist.

---

# 15 — Checklist de implementación (acciones concretas)

1. Instalar en la máquina los intérpretes Python que vayan a usarse.
2. Asegurar un Python "gestor" con `pyyaml` para correr `create_venv.py`.
3. Pegar los scripts `create_venv.py`, `create_venv.bat`, `run_notebook.py`, `run_stage.bat`, `mlflow_helper.py`.
4. Crear archivos `env_specs/*.yaml` para cada etapa con `python_exe` apuntando al Python deseado.
5. Instalar MLflow y ejecutar `mlflow server` como servicio.
6. Configurar Jenkins Windows agent y pipeline con el `Jenkinsfile` de ejemplo.
7. Versionar notebooks y ejecutar una run completa; revisar MLflow UI en `http://<mlflow-host>:5000`.
8. Ajustar `packages` en YAML si alguna instalación falla (usar ruedas o pin versions).

---

# 16 — Extras creativos y prácticos (ideas fuera de lo obvio)

* Mantén un directorio `wheels_cache/` con ruedas `.whl` aprobadas para instalaciones offline; `create_venv.py` puede usar `pip install --no-index --find-links=../wheels_cache -r requirements.txt`.
* Añade una etapa en Jenkins que calcule un “environment fingerprint” (hash de `pip-freeze.txt` + git sha) y lo compare con runs anteriores para detectar drift.
* Implementa una pequeña UI interna (Flask) que muestre diagramas de pipeline y enlace a runs de MLflow, útil para stakeholders no técnicos.
* Usa `papermill` para testing: tener notebooks “smoke tests” que se ejecutan en cada PR con datasets pequeños.

---

# 17 — Archivos listos para copiar (resumen rápido)

* `env_specs/*.yaml` (uno por etapa) — ejemplo incluido.
* `scripts/create_venv.bat` + `scripts/create_venv.py` — para crear venvs y registrar kernels.
* `scripts/run_stage.bat` + `scripts/run_notebook.py` + `scripts/mlflow_helper.py` — para ejecutar notebooks y subir artifacts a MLflow.
* `Jenkinsfile` — pipeline de ejemplo.
* `MLproject` — opcional para invocación con `mlflow run`.
