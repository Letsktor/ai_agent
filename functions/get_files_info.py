import os
def get_files_info(working_directory, directory=None):
    full_path=os.path.join(working_directory,directory)
    abs_path=os.path.abspath(full_path)
    if not os.path.isdir(abs_path):
        return f'Error: "{directory}" is not a directory'
    if not abs_path.startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    try:
        li=[]
        for files in os.listdir(full_path):
            li.append(f"- {files}: file_size={os.path.getsize(full_path+f'/{files}')}, is_dir={os.path.isdir(full_path+f'/{files}')}")
        return "\n".join(li)
    except Exception as e:
        return f"Error: {e}"