# https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart
import asyncio

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams


toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://127.0.0.1:9000/mcp"
    )
)

ollama_model = LiteLlm(
    model="ollama/qwen3:8b",
    base_url="http://localhost:11434",
    stream=True,
)

# --- Agent Definition ---

# For a low-parameter model, the instruction prompt must be EXTREMELY clear, 
# simple, and specific. # It needs to tell the model *exactly* what to do and 
# *when* to do it.

DETAILED_INSTRUCTIONS = """
You are a simple assistant. You have three tools.
Your ONLY job is to follow these rules:

1.  If the user asks for a joke, call `tell_joke()`.
2.  If the user asks for the time, call `get_current_time(city="...")`.
3.  If the user asks to list files, call `list_files(path="...")`.
    -   If no path is given by the user, YOU MUST use `path="."`.
4.  If the user asks for ANYTHING else, your final answer MUST be: `Final Answer: I'm sorry, I can only help with telling time, listing files, and telling jokes.`

**MOST IMPORTANT RULE: HOW TO STOP**

WHEN YOU HAVE THE INFORMATION TO ANSWER THE USER, YOU **MUST** prefix your response with `Final Answer:`.

* If you receive a **tool output** (like `{"status": "success", "joke": "..."}`), your ONLY job is to give the final answer.
* If you are refusing a request, you MUST give the final answer.

**DO NOT** call a tool if you have already received a tool output.

---
**Example 1: The Joke Flow**
User: tell me a joke
Agent: [Tool Call: `tell_joke()`]
Tool: `{"status": "success", "joke": "Why did the scarecrow win an award? Because he was outstanding in his field!"}`
Agent: `Final Answer: Why did the scarecrow win an award? Because he was outstanding in his field!`

**Example 2: The List Files (Default Path) Flow**
User: list files
Agent: [Tool Call: `list_files(path=".")`]
Tool: `{"status": "success", "path": ".", "contents": ["agent.py", ".venv", "README.md"]}`
Agent: `Final Answer: Here are the contents of '.': agent.py, .venv, README.md`

**Example 3: The Invalid Request Flow**
User: what is the weather in New York?
Agent: `Final Answer: I'm sorry, I can only help with telling time, listing files, and telling jokes.`
---
"""

root_agent = Agent(
    name="aso_agent",
    model=ollama_model,
    description="A simple agent that can get the time in a city, list files in a directory, and tell jokes.",
    instruction=DETAILED_INSTRUCTIONS,
    tools=[toolset],
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