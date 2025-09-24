"""
Uso: 
python scripts/create_venv.py --spec specs/ingest.yaml --venv-root ./ml_venvs
"""
import argparse, subprocess, sys, yaml, os, shutil

def run(cmd, env=None):
    print(">", cmd)
    proc = subprocess.run(cmd, shell=True, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout.decode(errors='ignore'))

def check_and_install_python_version(py_ver):
    """Check if Python version is installed with pyenv, install if not"""
    try:
        # Check if the version is already installed
        proc = subprocess.run(f'pyenv versions --bare', shell=True, capture_output=True, text=True)
        installed_versions = proc.stdout.strip().split('\n')
        
        if py_ver in installed_versions:
            print(f"Python {py_ver} is already installed")
            return
        
        print(f"Python {py_ver} not found. Installing...")
        run(f'pyenv install {py_ver}')
        print(f"Python {py_ver} installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error checking/installing Python version: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--venv-root", required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(open(args.spec))
    venv_name = spec["venv_name"]
    py_ver = spec["python_version"]
    venv_path = os.path.join(args.venv_root, venv_name)

    # 1) Check if Python version is installed, install if not
    check_and_install_python_version(py_ver)
    
    # 2) Create venv using pyenv
    # Use pyenv to switch to the specified Python version and create venv
    create_cmd = f'pyenv exec python -m venv "{venv_path}"'
    
    # Set the local Python version for this operation
    run(f'pyenv local {py_ver}')
    run(create_cmd)

    # 3) Upgrade pip and install wheel
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
