"""
create_venv.py --spec specs/ingest.yaml --venv-root C:\ml_venvs
"""
import argparse, subprocess, sys, yaml, os, shutil

def run(cmd, env=None):
    print(">", cmd)
    proc = subprocess.run(cmd, shell=True, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout.decode(errors='ignore'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--venv-root", required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(open(args.spec))
    venv_name = spec["venv_name"]
    py_ver = spec["python_version"]
    venv_path = os.path.join(args.venv_root, venv_name)

    # 1) Create venv using Python launcher (py -3.8 -m venv)
    # On Windows, 'py -3.8' will call the installed Python 3.8. Requires Python versions installed.
    create_cmd = f'py -{py_ver} -m venv "{venv_path}"'
    run(create_cmd)

    # 2) Upgrade pip and install wheel
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
