"""
Script para crear entornos Conda en una carpeta específica usando -n (nombre),
instalar paquetes con pip y registrar kernel de Jupyter.

Uso:
python scripts/create_conda_env.py --spec specs/test.yaml --env-root ./ml_envs

Parámetros del YAML:
venv_name: nombre del entorno
python_version: versión de Python
packages: lista de paquetes pip a instalar
kernel_display_name: nombre a mostrar en Jupyter
"""

import argparse, subprocess, os, yaml
from pathlib import Path

def run(cmd, env=None):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--env-root", required=True, help="Carpeta donde se crearán los entornos")
    args = parser.parse_args()

    spec = yaml.safe_load(open(args.spec))
    env_name = spec["venv_name"]
    py_ver = spec["python_version"]
    packages = spec.get("packages", [])
    display_name = spec.get("kernel_display_name", env_name)

    # 1) Crear entorno con nombre, pero con folder raíz personalizado
    env_root = Path(args.env_root).resolve()
    env_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["CONDA_ENVS_PATH"] = str(env_root)

    run(f'conda create -y -n "{env_name}" python={py_ver}', env=env)

    # 2) Instalar paquetes con pip dentro del entorno
    if packages:
        run(f'conda run -n "{env_name}" pip install -vvv ' + " ".join(packages), env=env)

    # 3) Instalar ipykernel y registrar kernel en Jupyter
    run(f'conda run -n "{env_name}" pip install ipykernel', env=env)
    run(f'conda run -n "{env_name}" python -m ipykernel install --user --name "{env_name}" --display-name "{display_name}"', env=env)

    # 4) Guardar pip freeze para auditoría
    freeze_file = Path(f"{env_root}/{env_name}_freeze.txt")
    run(f'conda run -n "{env_name}" pip freeze > "{freeze_file}"', env=env)

    print("Conda env ready:", env_root / env_name)

if __name__ == "__main__":
    main()
