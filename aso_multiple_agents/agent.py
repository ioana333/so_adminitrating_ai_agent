# https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart
import os
import asyncio
import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


ollama_model = LiteLlm(
    model="ollama/qwen3:8b",
    base_url="http://localhost:11434",
    stream=True,
)


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


# --- 1. Define Worker Agents ---
# These are specialists that only know how to do one thing.

time_agent = Agent(
    name="time_agent",
    model=ollama_model,
    description="Use this agent ONLY if the user asks for the 'time' in a specific 'city'.",
    instruction="""
        **Your Job:** You are a simple Time Bot. You have ONE tool called `get_current_time`.
        
        **Your Process:**
        1.  You will be given a user's request for the time (e.g., "what time is it in london?").
        2.  You MUST immediately call your `get_current_time` tool with the city you extracted.
        3.  The tool will give you an output (e.g., `{"status": "success", "report": "The current time in London is..."}`).
        4.  Your FINAL and ONLY response is to report the 'report' (on success) or 'error_message' (on failure).
        
        **Example 1: Success**
        User Request: "time in new york"
        Your Action: [Tool Call: `get_current_time(city="new york")`]
        Tool Output: `{"status": "success", "report": "The current time in New York is 2025-10-17 03:30:00"}`
        Your Final Answer: "The current time in New York is 2025-10-17 03:30:00"

        **Example 2: Failure**
        User Request: "what time is it in paris"
        Your Action: [Tool Call: `get_current_time(city="paris")`]
        Tool Output: `{"status": "error", "error_message": "Sorry, I don't have timezone information for 'paris'."}`
        Your Final Answer: "Sorry, I don't have timezone information for 'paris'."
    """,
    tools=[get_current_time],
)

directory_agent = Agent(
    name="directory_agent",
    model=ollama_model,
    description="Use this agent ONLY if the user asks to 'list files' or 'list directories'.",
    instruction="""
        **Your Job:** You are a simple File Bot. You have ONE tool called `list_files`.
        
        **Your Process:**
        1.  You will be given a user's request for files (e.g., "list files", "show files in /tmp").
        2.  You MUST immediately call your `list_files` tool.
        3.  **IMPORTANT:** If the user did NOT give a path, you MUST call the tool with `path="."`.
        4.  The tool will give you an output (e.g., `{"status": "success", "contents": ["file.txt"]}`).
        5.  Your FINAL and ONLY response is to report the 'contents' (on success) or 'error_message' (on failure).

        **Example 1: Success (Default Path)**
        User Request: "list my files"
        Your Action: [Tool Call: `list_files(path=".")`]
        Tool Output: `{"status": "success", "path": ".", "contents": ["agent.py", "README.md"]}`
        Your Final Answer: "Here are the contents of '.': agent.py, README.md"

        **Example 2: Success (Specific Path)**
        User Request: "what is in /var/log"
        Your Action: [Tool Call: `list_files(path="/var/log")`]
        Tool Output: `{"status": "success", "path": "/var/log", "contents": ["syslog", "auth.log"]}`
        Your Final Answer: "Here are the contents of '/var/log': syslog, auth.log"
        
        **Example 3: Failure**
        User Request: "list files in /root"
        Your Action: [Tool Call: `list_files(path="/root")`]
        Tool Output: `{"status": "error", "path": "/root", "error_message": "Permission denied to access: '/root'"}`
        Your Final Answer: "Permission denied to access: '/root'"
    """,
    tools=[list_files], 
)


# --- 2. Define the Root (Coordinator) Agent ---
# This agent is the "manager". It decides which specialist to call,
# or it handles the "easy" task (jokes) itself.

root_agent = Agent(
    name="root_agent",
    model=ollama_model,
    description="A coordinator agent that tells jokes and routes tasks to specialist agents.",
    instruction="""
        You are a manager agent. You have **two specialist agents** you can delegate tasks to: `time_agent` and `directory_agent`.
        You also have **one internal skill**: telling jokes.

        You MUST follow these rules and examples:

        **1. Joke Requests:**
        -   **If the user asks for a joke** or "something funny," your job is to **generate a joke yourself**.
        -   **DO NOT** transfer to an agent.
        -   **DO NOT** look for a tool.
        -   You must generate the joke text as your Final Answer.

        **2. Time Requests:**
        -   **If the user asks for the time,** your job is to transfer control to the `time_agent`.
        -   Your Final Answer should be ONLY the transfer.

        **3. File Requests:**
        -   **If the user asks to list files,** your job is to transfer control to the `directory_agent`.
        -   Your Final Answer should be ONLY the transfer.

        **4. Other Requests:**
        -   **If the user asks for ANYTHING ELSE** (like 'weather', 'hello', 'how are you'), you MUST refuse.
        -   Your Final Answer must be: "I'm sorry, I can only help with telling time, listing files, and telling jokes."

        ---
        **EXAMPLES OF YOUR JOB**
        ---

        **Example: Joke Request (Your Internal Skill)**
        User: "tell me a joke"
        Your Action: (Do NOT use any tool or agent. Generate a response directly.)
        Your Final Answer: "Why did the scarecrow win an award? Because he was outstanding in his field!"

        **Example: Time Request (Delegation)**
        User: "what time is it in tokyo?"
        Your Action: (Recognize this is a time question for the specialist)
        Your Final Answer: [Transfer to `time_agent`]

        **Example: File Request (Delegation)**
        User: "list files in /tmp"
        Your Action: (Recognize this is a file question for the specialist)
        Your Final Answer: [Transfer to `directory_agent`]
        
        **Example: Invalid Request (Refusal)**
        User: "hello"
        Your Action: (Recognize this is not a joke, time, or file question)
        Your Final Answer: "I'm sorry, I can only help with telling time, listing files, and telling jokes."
    """,
    sub_agents=[time_agent, directory_agent],
    tools=[] # This agent has no tools of its own
)

async def main():
    
    import uuid
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService, Session
    from google.genai import types 
    """
    Main function to set up the ADK Runner and chat with the agent.
    """
    
    app_name = "aso_agent_chat"  # This can be any string

    # This service stores conversation history.
    session_service = InMemorySessionService()
    
    # The Runner orchestrates the entire agent execution.
    runner = Runner(
        session_service=session_service,
        agent=root_agent,
        app_name=app_name
    )
    
    # Arbitrary IDs for the user and session
    user_id = f"user_{uuid.uuid4()}"
    session_id = f"session_{uuid.uuid4()}"

    print(f"Creating new session: {session_id}")
    await session_service.create_session(
        app_name=app_name,
        session_id=session_id,
        user_id=user_id
        # You could also pass initial agent state here if needed
    )
    
    print(f"--- Agent Chat Started (Session: {session_id}) ---")
    print("Type 'exit' to quit.")

    print("Ask a question (e.g., 'What time is it in Tokyo?', 'list files', 'tell me a joke').")
    
    while True:
        try:
            user_input_text = input("You: ")
            if user_input_text.lower() == 'exit':
                break
            
            # Format the user's input into the ADK's message format
            user_message = types.Content(
                role="user",
                parts=[types.Part(text=user_input_text)]
            )
            
            final_response_text = "Agent did not provide a final response."
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                # The agent loop produces many events (tool calls, etc.)
                # We are looking for the final text response to the user.
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                        break  # Got the final answer, stop processing events
            
            print(f"Assistant: {final_response_text}")

        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")