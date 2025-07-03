import os
import subprocess
def run_python_file(working_directory, file_path):
    full_path=os.path.join(working_directory,file_path)
    abs_path=os.path.abspath(full_path)
    if not abs_path.startswith(os.path.abspath(working_directory)):
        return  f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if file_path not in os.listdir(os.path.abspath(working_directory)):
        return f'Error: File "{file_path}" not found.'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        finished=subprocess.run(args=["python3",file_path],timeout=30,capture_output=True,cwd=os.path.abspath(working_directory),text=True)
        if not finished.returncode==0:
            return f"Process exited with code {finished.returncode}"
        if finished.stdout==None and finished.stderr==None:
            return "No output produced."
        print(finished.stdout)
        return f'STDOUT: {finished.stdout}\n STDERR:{finished.stderr}'
    except Exception as e:
        f"Error: executing Python file: {e}"
