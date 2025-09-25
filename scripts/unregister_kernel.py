"""
Script para desregistrar kernels de Jupyter.

Uso: 
python scripts/unregister_kernel.py --kernel-name my_kernel
python scripts/unregister_kernel.py --list-kernels
python scripts/unregister_kernel.py --remove-all
python scripts/unregister_kernel.py --spec specs/optimization.yaml
"""
import argparse
import subprocess
import sys
import json
import yaml
import os
from pathlib import Path

def run(cmd, env=None, capture_output=False):
    """Execute a command and optionally capture output"""
    print(">", cmd)
    if capture_output:
        proc = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"Error: {proc.stderr}")
            return None
        return proc.stdout.strip()
    else:
        proc = subprocess.run(cmd, shell=True, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(proc.stdout.decode(errors='ignore'))

def list_kernels():
    """List all available Jupyter kernels"""
    try:
        output = run("jupyter kernelspec list --json", capture_output=True)
        if output:
            kernels_data = json.loads(output)
            kernels = kernels_data.get('kernelspecs', {})
            
            if not kernels:
                print("No kernels found.")
                return []
            
            print("Available kernels:")
            kernel_names = []
            for name, info in kernels.items():
                print(f"  - {name}: {info.get('spec', {}).get('display_name', 'N/A')}")
                print(f"    Location: {info.get('resource_dir', 'N/A')}")
                kernel_names.append(name)
            
            return kernel_names
        else:
            print("Failed to list kernels")
            return []
    except json.JSONDecodeError as e:
        print(f"Error parsing kernel list: {e}")
        return []
    except Exception as e:
        print(f"Error listing kernels: {e}")
        return []

def unregister_kernel(kernel_name):
    """Unregister a specific kernel by name"""
    try:
        # Check if kernel exists first
        kernels = list_kernels()
        if kernel_name not in kernels:
            print(f"Kernel '{kernel_name}' not found.")
            return False
        
        print(f"Unregistering kernel: {kernel_name}")
        run(f'jupyter kernelspec uninstall "{kernel_name}" -f')
        print(f"Successfully unregistered kernel: {kernel_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error unregistering kernel '{kernel_name}': {e}")
        return False

def remove_all_kernels():
    """Remove all registered kernels except the default python3 kernel"""
    kernels = list_kernels()
    
    if not kernels:
        print("No kernels to remove.")
        return
    
    # Filter out the default python3 kernel to avoid removing system kernel
    kernels_to_remove = [k for k in kernels if k != 'python3']
    
    if not kernels_to_remove:
        print("Only system kernel found. Nothing to remove.")
        return
    
    print(f"Found {len(kernels_to_remove)} kernel(s) to remove:")
    for kernel in kernels_to_remove:
        print(f"  - {kernel}")
    
    confirmation = input("Are you sure you want to remove all these kernels? (y/N): ")
    if confirmation.lower() in ['y', 'yes']:
        for kernel in kernels_to_remove:
            unregister_kernel(kernel)
    else:
        print("Operation cancelled.")

def unregister_from_spec(spec_file):
    """Unregister kernel based on specification file"""
    try:
        with open(spec_file, 'r') as f:
            spec = yaml.safe_load(f)
        
        kernel_name = spec.get("venv_name")
        if not kernel_name:
            print(f"No 'venv_name' found in spec file: {spec_file}")
            return False
        
        print(f"Unregistering kernel from spec: {kernel_name}")
        return unregister_kernel(kernel_name)
        
    except FileNotFoundError:
        print(f"Spec file not found: {spec_file}")
        return False
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Unregister Jupyter kernels")
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument("--kernel-name", 
                      help="Name of the kernel to unregister")
    group.add_argument("--list-kernels", action="store_true",
                      help="List all available kernels")
    group.add_argument("--remove-all", action="store_true",
                      help="Remove all kernels (except system python3)")
    group.add_argument("--spec",
                      help="Unregister kernel based on spec file (uses venv_name)")
    
    args = parser.parse_args()
    
    if args.list_kernels:
        list_kernels()
    elif args.kernel_name:
        unregister_kernel(args.kernel_name)
    elif args.remove_all:
        remove_all_kernels()
    elif args.spec:
        unregister_from_spec(args.spec)

if __name__ == "__main__":
    main()