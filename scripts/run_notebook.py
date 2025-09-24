"""
run_notebook.py --venv C:\ml_venvs\ml_ingest_py38 --notebook notebooks/ingest.ipynb --output out/ingest_out.ipynb
"""
import argparse, subprocess, os, sys, yaml

def run(cmd, env=None):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", required=True)
    parser.add_argument("--notebook", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--params-file", required=False)
    args = parser.parse_args()

    python_exec = os.path.join(args.venv, "Scripts", "python.exe")
    papermill = f'"{python_exec}" -m papermill "{args.notebook}" "{args.output}"'
    if args.params_file:
        papermill += f' -f "{args.params_file}"'

    # Optional: set MLflow tracking URI (env var) before running
    # os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-server:5000"
    run(papermill)

if __name__ == "__main__":
    main()
