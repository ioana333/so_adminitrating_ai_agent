import os
import random
import datetime
from zoneinfo import ZoneInfo


def list_files(path: str) -> dict:
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


def tell_joke() -> dict:
    """
    Tells a random, short, family-friendly joke.

    Use this tool ONLY when the user explicitly asks for a 'joke' 
    or asks you to 'tell me something funny'.
    This tool takes NO arguments.

    Returns:
        dict: A dictionary with:
              - 'status': 'success'
              - 'joke': A string containing the joke.
    """
    print("tell_joke called")  # Debug log
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call a factory that makes good products? A satisfactory.",
        "Why couldn't the bicycle stand up by itself? It was two-tired."
    ]
    
    joke = random.choice(jokes)
    return {"status": "success", "joke": joke}


def get_current_time(city: str) -> dict:
    """
    Returns the current time in a specified city.

    Use this tool ONLY when the user asks for the 'time' in a specific 'city'.
    You MUST extract the 'city' name from the user's request.

    Args:
        city (str): The name of the city (e.g., "New York", "London"). 
                    This function only supports "New York" as an example.

    Returns:
        dict: A dictionary with:
              - 'status': 'success' or 'error'
              - 'report': (on success) A string with the current date and time.
              - 'error_message': (on error) A string explaining the failure.
    """
    print(f"get_current_time called for: {city}")  # Debug log
    
    # Simple mapping just for an example.
    tz_identifier = ""
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    elif city.lower() in ["london", "dublin", "lisbon"]:
         tz_identifier = "Europe/London"
    elif city.lower() in ["paris", "berlin", "rome"]:
         tz_identifier = "Europe/Paris"
    elif city.lower() in ["tokyo"]:
         tz_identifier = "Asia/Tokyo"
    else:
        return {"status": "error",
                "error_message": f"Sorry, I don't have timezone information for '{city}'."}

    try:
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        return {"status": "success",
                "report": f"""The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}"""}
    except Exception as e:
        return {"status": "error",
                "error_message": f"Error getting time for {city}: {str(e)}"}