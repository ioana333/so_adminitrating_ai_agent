import os
import random
import datetime
from zoneinfo import ZoneInfo

def list_directory(path: str) -> dict:
    """
    Lists all files inside a specified file system path.

    Use this tool ONLY when the user asks to 'list files', 'show files', 
    'list files', or 'what's in this folder'.

    Args:
        path (str): The absolute or relative path of the directory 
                    you want to list. 
                    This argument is REQUIRED.
                    If the user does not specify a path, YOU MUST pass "."
                    (a string with a single period) as the path.

    Returns:
        dict: A dictionary with:
              - 'status': 'success' or 'error'
              - 'path': The path that was listed
              - 'contents': (on success) A list of strings
              - 'error_message': (on error) A string explaining what went wrong
    """
    print(f"list_files called for path: {path}")  # Debug log
    try:

        if not os.path.exists(path):
            return {"status": "error",
                    "path": path,
                    "error_message": f"Path not found: '{path}'"}

        if not os.path.isdir(path):
            return {"status": "error",
                    "path": path,
                    "error_message": f"Path is not a directory: '{path}'"}

        contents = os.listdir(path)
        
        if not contents:
             return {"status": "success",
                    "path": path,
                    "contents": ["(This directory is empty)"]}
        
        return {"status": "success",
                "path": path,
                "contents": contents}

    except PermissionError:
        return {"status": "error",
                "path": path,
                "error_message": f"Permission denied to access: '{path}'"}
    except Exception as e:
        return {"status": "error",
                "path": path,
                "error_message": f"An unexpected error occurred: {str(e)}"}

def get_file_content(path: str) -> dict:
    """
    Returns the text content of a file.
    
    Use this tool when the user asks what a file contains or wants to
    see what is written inside a file.    
    
    Args:
        path (str): The absolute or relative path of the file 
                    you want to read. 
                    This argument is REQUIRED.
                    If the user does not specify a path, YOU MUST pass "."
                    (a string with a single period) as the path.

    Returns:
        dict: A dictionary with:
              - 'status': 'success' or 'error'
              - 'path': The path that was listed
              - 'contents': (on success) A list of strings
              - 'error_message': (on error) A string explaining what went wrong
    """
    print(f"get_file_content called for path: {path}")  # Debug log
    try:

        if not os.path.exists(path):
            return {"status": "error",
                    "path": path,
                    "error_message": f"Path not found: '{path}'"}

        if not os.path.isfile(path):
            return {"status": "error",
                    "path": path,
                    "error_message": f"Path is not a directory: '{path}'"}

        with open(path, "r") as f:
            contents = f.read()

        if not contents:
            return {"status": "success",
                    "path": path,
                    "contents": ["(This directory is empty)"]}

        return {"status": "success",
                "path": path,
                "contents": contents}

    except PermissionError:
        return {"status": "error",
                "path": path,
                "error_message": f"Permission denied to access: '{path}'"}
    except Exception as e:
        return {"status": "error",
                "path": path,
                "error_message": f"An unexpected error occurred: {str(e)}"}

def get_system_info() -> dict:
    """
    Returns the basic information about the operating system.

    Use this tool when the user asks about the operating system, the OS, its version,
    the architecture, CPU, RAM or the machine name    

    Returns:
        dict: A dictionary with:
              - 'status': 'success' or 'error'
              - 'path': The path that was listed
              - 'contents': (on success) A dictionary of strings
              - 'error_message': (on error) A string explaining what went wrong
    """
    print(f"get_system_info: ")  # Debug log
    try:

        contents = {
            "OS": platform.system(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node()
        }

        if not contents:
            return {"status": "success",
                    "contents": ["(Could not get system information)"]}

        return {"status": "success",
                "contents": contents}

    except Exception as e:
        return {"status": "error",
                "error_message": f"An unexpected error occurred: {str(e)}"}


if __name__ == "__main__":
    mcp_app = app.http_app(path='/mcp', transport="http")
    uvicorn.run(mcp_app, host="127.0.0.1", port=9000)


