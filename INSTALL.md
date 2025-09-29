# Guía de instalación paso a paso

**MLOps en Windows con GoCD + MLflow + Conda + papermill**

---

## 1. Requisitos previos

Antes de empezar, asegurate de tener:

* **Windows 10/11** actualizado.
* Permisos de administrador (para instalar programas).
* Conexión a internet.
* **Git** instalado: [descargar aquí](https://git-scm.com/download/win).

---

## 2. Instalar Conda

1. Descargar e instalar **Miniconda** o **Anaconda** para Windows:

   * Miniconda: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
2. Agregar Conda al PATH si no se agregó automáticamente.
3. Abrir nueva terminal PowerShell y verificar:

   ```powershell
   conda --version
   ```

---

## 3. Instalar Jupyter (base)

```powershell
conda install -y notebook jupyterlab
```

---

## 4. Clonar este repositorio

```powershell
git clone https://github.com/georgsmeinung/mlops-pipeline
cd mlops-pipeline
```

---

## 5. Instalar MLflow (opcional pipeline completo)

```powershell
conda install -y pip
pip install mlflow==1.29.0
```

Configurar backend sencillo con SQLite:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow/mlflow.db --default-artifact-root ./mlruns
```

La UI estará disponible en `http://127.0.0.1:5000`.

---

## 6. Instalar GoCD (opcional pipeline completo)

1. Descargar **GoCD Server** y **GoCD Agent (Windows)** desde: [https://www.gocd.org/download/](https://www.gocd.org/download/).
2. Instalar **GoCD Server** (puede ser la misma máquina que el agente).
3. Instalar **GoCD Agent** en la misma máquina o en estaciones de los data scientists.

   * Durante la instalación, apuntar el agente al servidor (`localhost` si es la misma máquina).

---

## 7. Configurar pipeline en GoCD (opcional)

1. Ingresar a `http://localhost:8153`.

2. Crear pipeline `mlops_pipeline`.

3. Definir stages:

   * `setup_env_ingest`
   * `run_ingest`
   * `setup_env_features`
   * `run_features`
   * etc.

4. En cada job:

   * `setup_env_*`:

     ```powershell
     python scripts/create_conda_env.py --spec specs/ingest.yaml --env-root C:\ml_envs
     ```
   * `run_*`:

     ```powershell
     python scripts/run_notebook.py --conda-env C:\ml_envs\ml_ingest_py38 --notebook notebooks/ingest.ipynb --output out/ingest_out.ipynb --params-file params/ingest_params.yaml
     ```

---

## 8. Validar el setup

1. Ejecutar pipeline desde GoCD.
2. Verificar:

   * Se creó el entorno Conda en `C:\ml_envs\ml_ingest_py38`.
   * Kernel registrado en Jupyter:

     ```powershell
     jupyter kernelspec list
     ```
   * Notebook ejecutado y guardado en `out/`.
   * MLflow registra run con parámetros, métricas y artefactos.

---

## 9. Uso interactivo en Jupyter

1. Abrir Jupyter Lab:

   ```powershell
   jupyter lab
   ```
2. Seleccionar kernel `Ingest (py3.8)` (o el definido en el YAML).
3. Prototipar libremente; luego el mismo código se puede ejecutar automáticamente vía GoCD + papermill.

---

## 10. Checklist rápido

* [ ] Conda instalado y accesible (`conda --version`)
* [ ] Jupyter instalado
* [ ] MLflow instalado y corriendo en `localhost:5000`
* [ ] GoCD server y agent instalados y activos
* [ ] Repo clonado con `specs/`, `notebooks/`, `scripts/`
* [ ] Pipeline creado en GoCD con `create_conda_env.py` y `run_notebook.py`
* [ ] Primer run exitoso con notebook ejecutado y registrado en MLflow
