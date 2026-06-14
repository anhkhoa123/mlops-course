import sys
import subprocess

def check_git():
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    print("Git:", result.stdout.strip())

def check_python():
    print("Python:", sys.version)
    print("Duong dan:", sys.executable)

if __name__ == "__main__":
    check_git()
    check_python()
