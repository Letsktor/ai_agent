import os
MAX_CHARS = 10000
def get_file_content(working_directory, file_path):
    full_path=os.path.join(working_directory,file_path)
    abs_path=os.path.abspath(full_path)
    if not abs_path.startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    try:
        with open(abs_path, "r") as f:
            file=f.read()         
            if len(file)>MAX_CHARS:
                file_content_string = file[:MAX_CHARS]
                return file_content_string+f'[...File "{file_path}" truncated at 10000 characters]'
            else:
                file_content_string = file
                return file_content_string
    except Exception as e:
        return f"Error: {e}"
    