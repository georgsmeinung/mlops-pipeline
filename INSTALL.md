# Guía de instalación paso a paso

**MLOps en Windows con GoCD + MLflow + venvs + papermill**

---

## 1. Requisitos previos

Antes de empezar, asegurate de tener:

* **Windows 10/11** actualizado.
* Permisos de administrador (para instalar programas).
* Conexión a internet (para descargar librerías y Python).
* **Git** instalado: [descargar aquí](https://git-scm.com/download/win).

---

## 2. Instalar múltiples versiones de Python

La solución requiere distintas versiones de Python para cada etapa.
Opciones. Usar **pyenv-win** (más flexible, instala versiones bajo demanda)

1. Instalar con PowerShell:

   ```powershell
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
   ```
2. Reiniciar la terminal.
3. Instalar versiones necesarias:

   ```powershell
   pyenv install 3.8.10
   pyenv install 3.9.13
   pyenv install 3.10.11
   ```

---

## 3. Instalar Jupyter

En el Python base del sistema:

```powershell
pip install notebook jupyterlab
```

---

## 4. Clonar este repositorio

```powershell
git clone https://github.com/georgsmeinung/mlops-pipeline
cd mlops-pipeline
```

---

## 5. Instalar MLflow

En el Python base:

```powershell
pip install mlflow==1.29.0
```

Configurar un backend sencillo con SQLite:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```

Esto abre la UI en `http://127.0.0.1:5000`.

---

## 6. Instalar GoCD

1. Descargar **GoCD Server** y **GoCD Agent (Windows)** desde: [https://www.gocd.org/download/](https://www.gocd.org/download/).
2. Instalar **GoCD Server** en una máquina Windows (puede ser la misma del equipo).

   * Servicio corre en `http://localhost:8153`.
3. Instalar **GoCD Agent** en la misma máquina o en máquinas de los data scientists.

   * Durante la instalación, apuntar el agente al servidor (`localhost` si es la misma máquina).

---

## 7. Crear estructura de carpetas

Si no está creada ya en el repo:

```powershell
mkdir specs notebooks params scripts gocd
```

---

## 8. Configurar GoCD pipeline

1. Ingresar a la UI de GoCD (`http://localhost:8153`).
2. Crear un pipeline llamado `mlops_pipeline`.
3. Definir stages por etapa:

   * **Stage 1**: `setup_env_ingest`
   * **Stage 2**: `run_ingest`
   * etc.
4. En cada job:

   * `setup_env_*`:

     ```powershell
     python scripts/create_venv.py --spec specs/ingest.yaml --venv-root C:\ml_venvs
     ```
   * `run_*`:

     ```powershell
     python scripts/run_notebook.py --venv C:\ml_venvs\ml_ingest_py38 --notebook notebooks/ingest.ipynb --output out/ingest_out.ipynb --params-file params/ingest_params.yaml
     ```

---

## 9. Validar el setup

1. Ejecutar el pipeline desde la UI de GoCD.
2. Verificar:

   * Se creó el venv en `C:\ml_venvs\`.
   * El kernel aparece en Jupyter (`jupyter kernelspec list`).
   * El notebook fue ejecutado y guardado en `out/`.
   * En MLflow aparece un run con parámetros, métricas y artefactos.

---

## 10. Uso interactivo en Jupyter

1. Abrir Jupyter Lab:

   ```powershell
   jupyter lab
   ```
2. En un notebook nuevo, seleccionar kernel `Ingest (py3.8)` (o el que se haya definido en el YAML).
3. Prototipar libremente; luego el mismo código se puede ejecutar automatizado vía GoCD + papermill.

---

## 11. Checklist rápido (resumen)

* [ ] Python (múltiples versiones) instalado y accesible (`py -3.8`, `py -3.9`)
* [ ] Jupyter instalado
* [ ] MLflow instalado y corriendo en `localhost:5000`
* [ ] GoCD server y agent instalados y activos
* [ ] Repo clonado con carpetas `specs`, `notebooks`, `scripts`
* [ ] Pipeline creado en GoCD con `create_venv.py` y `run_notebook.py`
* [ ] Primer run exitoso con notebook ejecutado y registrado en MLflow

