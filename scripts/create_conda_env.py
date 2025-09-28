"""
Script para crear entornos con Conda a partir de especificaciones YAML 
y registrar kernels para Jupyter.

Uso: 
python scripts/create_conda_env.py --spec specs/test.yaml --env-root ./ml_envs
"""
import argparse, subprocess, sys, yaml, os
from pathlib import Path

def run(cmd, env=None):
    print(">", cmd)
    proc = subprocess.run(cmd, shell=True, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout.decode(errors='ignore'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--env-root", required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(open(args.spec))
    env_name = spec["venv_name"]   # lo dejo igual para no romper specs
    py_ver = spec["python_version"]
    env_path = Path(args.env_root) / env_name

    # 1) Crear entorno con conda
    #   -p especifica el path exacto (en lugar de manejar entornos por nombre global)
    run(f'conda create -y -p "{env_path}" python={py_ver}')

    # 2) Instalar paquetes con conda (si están listados)
    conda_packages = spec.get("conda_packages", [])
    if conda_packages:
        run(f'conda install -y -p "{env_path}" ' + " ".join(conda_packages))

    # 3) Instalar paquetes con pip (fallback)
    pip_packages = spec.get("pip_packages", [])
    if pip_packages:
        pip_exec = env_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
        cmd = [str(pip_exec), "install", "-vvv"] + pip_packages
        subprocess.run(cmd, check=True)

    # 4) Registrar kernel en Jupyter
    python_exec = env_path / ("Scripts" if os.name == "nt" else "bin") / "python"
    kernel_name = env_name
    display_name = spec.get("kernel_display_name", kernel_name)

    run(f'"{python_exec}" -m pip install ipykernel')
    run(f'"{python_exec}" -m ipykernel install --user --name "{kernel_name}" --display-name "{display_name}"')

    # 5) Guardar freeze para auditoría
    freeze_file = f"{env_path}_freeze.txt"
    run(f'"{python_exec}" -m pip freeze > "{freeze_file}"')

    print("Conda env ready:", env_path)

if __name__ == "__main__":
    main()
