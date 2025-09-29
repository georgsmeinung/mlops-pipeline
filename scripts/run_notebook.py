"""
Este script permite ejecutar un notebook de Jupyter usando un entorno Conda específico,
gracias a la herramienta `papermill`, que admite parametrización y salida controlada.

USO:
    python run_notebook.py \
        --conda-env ./ml_venvs/ml_ingest_py38 \
        --notebook notebooks/ingest.ipynb \
        --output out/ingest_out.ipynb \
        [--params-file specs/params.yaml]

Parámetros:
    --conda-env   Ruta al entorno Conda (ej: ./ml_venvs/ml_ingest_py38) o nombre de entorno.
    --notebook    Notebook de entrada que se quiere ejecutar.
    --output      Archivo de salida con el notebook ya ejecutado.
    --params-file (opcional) Archivo YAML con parámetros a inyectar en el notebook.

Notas:
  - Usa `conda run` para asegurar que el notebook se ejecute en el entorno Conda elegido.
  - Antes de la ejecución se setea la variable de entorno MLFLOW_TRACKING_URI.
  - Requiere que `papermill` esté instalado dentro del entorno Conda.
"""

import argparse, subprocess, os

def run(cmd, env=None):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conda-env", required=True, help="Nombre o ruta del entorno conda")
    parser.add_argument("--notebook", required=True, help="Notebook de entrada")
    parser.add_argument("--output", required=True, help="Notebook de salida")
    parser.add_argument("--params-file", required=False, help="Archivo YAML con parámetros opcionales")
    args = parser.parse_args()

    # Construir comando usando conda run
    papermill_cmd = [
        "conda", "run", "-p", args.conda_env,  # usar ruta al entorno
        "python", "-m", "papermill",
        args.notebook,
        args.output
    ]

    if args.params_file:
        papermill_cmd.extend(["-f", args.params_file])

    # Setear tracking URI opcional
    env = os.environ.copy()
    env["MLFLOW_TRACKING_URI"] = "http://localhost:5000"

    run(" ".join(papermill_cmd), env=env)

if __name__ == "__main__":
    main()
