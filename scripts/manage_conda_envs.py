"""
Script para listar y borrar entornos Conda, y desregistrar su kernel Jupyter.

USO:
    Listar entornos:
        python scripts/manage_conda_envs.py --list

    Borrar un entorno:
        python scripts/manage_conda_envs.py --delete <env_name> [--env-root ./ml_envs]

Parámetros:
    --list          Lista todos los entornos Conda disponibles.
    --delete        Borra el entorno especificado por nombre.
    --env-root      Carpeta raíz donde se crean los entornos (opcional, útil si no están en default conda envs).
"""

import argparse, subprocess, os
from pathlib import Path

def run(cmd, env=None):
    """Ejecuta un comando shell y muestra la salida."""
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def list_envs():
    """Lista todos los entornos Conda."""
    run("conda env list")

def remove_kernel(kernel_name):
    """Desregistra el kernel Jupyter asociado al entorno."""
    try:
        run(f"jupyter kernelspec remove {kernel_name} -f")
        print(f"Kernel '{kernel_name}' eliminado.")
    except subprocess.CalledProcessError:
        print(f"No se encontró kernel '{kernel_name}' para eliminar.")

def delete_env(env_name, env_root=None):
    """Borra un entorno Conda por nombre y desregistra el kernel."""
    env = os.environ.copy()
    success = False

    # 1) Intentar borrar por nombre (default conda envs)
    try:
        run(f"conda env remove -n {env_name} --yes", env=env)
        success = True
    except subprocess.CalledProcessError:
        print(f"No se pudo eliminar el entorno '{env_name}' por nombre en la ubicación default de conda.")

    # 2) Intentar borrar por path absoluto si se pasa env_root
    if not success and env_root:
        env_path = Path(env_root).resolve() / env_name
        if env_path.exists():
            try:
                run(f'conda env remove -p "{env_path}" --yes', env=env)
                success = True
            except subprocess.CalledProcessError:
                print(f"No se pudo eliminar el entorno en path '{env_path}'.")
        else:
            print(f"No existe entorno en path '{env_path}'")

    if success:
        # 3) Borrar kernel Jupyter
        remove_kernel(env_name)
        print(f"Entorno '{env_name}' eliminado correctamente.")
    else:
        print(f"No se pudo eliminar el entorno '{env_name}' ni por nombre ni por path.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="Listar entornos Conda")
    parser.add_argument("--delete", type=str, help="Nombre del entorno a borrar")
    parser.add_argument("--env-root", type=str, help="Carpeta raíz de entornos si no están en default conda envs")
    args = parser.parse_args()

    if args.list:
        list_envs()
    elif args.delete:
        delete_env(args.delete, env_root=args.env_root)
    else:
        print("Error: Debe usar --list o --delete <env_name> [--env-root]")

if __name__ == "__main__":
    main()
