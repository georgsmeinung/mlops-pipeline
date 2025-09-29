"""
Script para listar y borrar entornos Conda, y desregistrar su kernel Jupyter.

USO:
    python manage_conda_envs.py --list
    python manage_conda_envs.py --delete <env_name>

Opciones:
    --list          Lista todos los entornos Conda disponibles.
    --delete        Borra el entorno especificado por nombre y su kernel Jupyter.
"""

import argparse, subprocess, os

def run(cmd, env=None):
    """Ejecuta un comando en shell y muestra salida."""
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def list_envs():
    """Lista todos los entornos Conda."""
    run("conda env list")

def remove_kernel(kernel_name):
    """Desregistra el kernel de Jupyter asociado al entorno."""
    try:
        run(f"jupyter kernelspec remove {kernel_name} -f")
        print(f"Kernel '{kernel_name}' eliminado.")
    except subprocess.CalledProcessError:
        print(f"No se encontró kernel '{kernel_name}' para eliminar.")

def delete_env(env_name):
    """Borra un entorno Conda por nombre y desregistra el kernel."""
    # 1) Borrar el entorno
    try:
        run(f"conda env remove -n {env_name} --yes")
    except subprocess.CalledProcessError:
        print(f"No se pudo eliminar el entorno '{env_name}' por nombre, intentando por path...")
        try:
            run(f"conda env remove -p {env_name} --yes")
        except subprocess.CalledProcessError:
            print(f"No se pudo eliminar el entorno '{env_name}' ni por nombre ni por path.")
            return

    # 2) Borrar kernel Jupyter
    remove_kernel(env_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="Listar entornos Conda")
    parser.add_argument("--delete", type=str, help="Nombre o path del entorno a borrar")
    args = parser.parse_args()

    if args.list:
        list_envs()
    elif args.delete:
        delete_env(args.delete)
    else:
        print("Error: Debe usar --list o --delete <env_name_or_path>")

if __name__ == "__main__":
    main()
