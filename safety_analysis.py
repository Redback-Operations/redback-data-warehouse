import subprocess
import json
import os

def run_safety(path):
    """Runs Safety check on the dependencies and returns the results as JSON."""
    try:
        requirements_file = os.path.join(path, 'requirements.txt')
        if not os.path.exists(requirements_file):
            print(f"Requirements file does not exist: {requirements_file}")
            return None

        result = subprocess.run(['safety', 'check', '--json', '--file', requirements_file], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Safety: {e.stderr}")
        print(f"Standard output: {e.stdout}")
        return None

if __name__ == "__main__":
    TARGET_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'myproject', 'sample_code')
    if os.path.exists(TARGET_PATH):
        safety_results = run_safety(TARGET_PATH)
        if safety_results:
            print(json.dumps(safety_results, indent=2))
    else:
        print(f"Target path does not exist: {TARGET_PATH}")
