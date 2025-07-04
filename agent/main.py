
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

sys.path.insert(0, "..")
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = function_call_part.args
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    di = {"get_file_content": get_file_content, "get_files_info": get_files_info,
              "run_python_file": run_python_file, "write_file": write_file}
    if function_name not in di:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "error": f"Unknown function: {function_name}"},
                )
            ],
        )
    else:
        function_result = di[function_call_part.name](
            working_directory="../calculator", **function_args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )


def main():
    load_dotenv()
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    user_prompt = sys.argv[1]
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )
    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Prints the contents of a file.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The name of the file which we want to know the contents of.",
                ),
            },
        ),
    )
    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Runs a python file",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The name of the file which we want to execute.",
                ),
            },
        ),
    )
    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes content into a file",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The name of the file which we want to write.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content which will be written into the file.",
                ),
            },
        ),
    )
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file
        ]
    )
    config = types.GenerateContentConfig(
        system_instruction=system_prompt, tools=[available_functions])
    iters = 0
    while True:
        iters+=1
        if iters > 20:
            print(f"Maximum iterations ({20}) reached.")
            sys.exit(1)
        try:
            function_responses=[]
            if len(sys.argv) == 2:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-001", contents=messages, config=config,)

                if response.function_calls:
                    for function_call_part in response.function_calls:
                        if not call_function(function_call_part).parts[0].function_response.response:
                            raise Exception("EROORRRR")
                else:
                    print(response.text)
            elif len(sys.argv) == 3 and sys.argv[2] == "--verbose":
                response = client.models.generate_content(
                    model="gemini-2.0-flash-001", contents=messages, config=config,)
                if response.candidates:
                    for candidate in response.candidates:
                        functin_call_content=candidate.content
                        messages.append(functin_call_content)
                if response.function_calls:
                    for function_call_part in response.function_calls:
                        function_call_result = call_function(
                            function_call_part,verbose=True)
                        if not function_call_result.parts[0].function_response.response:
                            raise Exception("EROORRRR")
                        else:
                            print(
                                f"-> {function_call_result.parts[0].function_response.response}")
                            function_responses.append(function_call_result.parts[0])
                else:
                    print(response.text)
                    print(f"User prompt: {user_prompt}")
                    print(
                        f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                    print(
                        f"Response tokens: {response.usage_metadata.candidates_token_count}")
                messages.append(types.Content(role="tool",parts=function_responses))
            else:
                raise Exception("Prompt wasn't provided!")
                exit(1)
        except Exception as e:
            print(f"Error while generating content: {e}")
        


if __name__ == "__main__":
    main()
