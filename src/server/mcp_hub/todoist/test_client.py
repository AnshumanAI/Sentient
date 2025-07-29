# src/server/mcp_hub/todoist/test_client.py
import json
from qwen_agent.agents import Assistant

# --- Configuration ---
llm_cfg = {
    'model': 'qwen3:4b',
    'model_server': 'http://localhost:11434/v1/',
    'api_key': 'EMPTY',
}

# Todoist MCP Server Configuration
mcp_server_url = "http://127.0.0.1:9021/sse"

# IMPORTANT: Replace with a valid User ID from your MongoDB that has Todoist credentials
USER_ID = "google-oauth2|115437244827618197332"

# --- Agent Setup ---
tools = [{
    "mcpServers": {
        "todoist_server": {
            "url": mcp_server_url,
            "headers": {"X-User-ID": USER_ID},
        }
    }
}]

print("Initializing Qwen agent for Todoist...")
agent = Assistant(
    llm=llm_cfg,
    function_list=tools,
    name="TodoistAgent",
    description="An agent that can manage Todoist tasks.",
    system_message="You are a helpful Todoist assistant. Use the available tools to manage projects and tasks."
)

# --- Interactive Chat Loop ---
def run_agent_interaction():
    print("\n--- Todoist Agent Ready ---")
    print("You can now manage your Todoist tasks.")
    print("Type 'quit' or 'exit' to end the session.")
    print("\nExample commands:")
    print("  - list my projects")
    print("  - what are my tasks for today?")
    print("  - add a task 'Buy milk' to my Inbox project")
    print("  - complete the task with ID '...'")
    print("-" * 25)

    messages = []
    while True:
        try:
            print("\nYou: ", end="")
            user_input = input()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋  Goodbye!")
                break

            messages.append({'role': 'user', 'content': user_input})
            print("\nAgent: ", end="", flush=True)
            
            last_assistant_text = ""
            final_response_from_run = None
            for response in agent.run(messages=messages):
                if isinstance(response, list) and response and response[-1].get("role") == "assistant":
                    current_text = response[-1].get("content", "")
                    if isinstance(current_text, str):
                        delta = current_text[len(last_assistant_text):]
                        print(delta, end="", flush=True)
                        last_assistant_text = current_text
                final_response_from_run = response

            print()
            if final_response_from_run:
                messages = final_response_from_run
            else:
                print("I could not process that request.")
                messages.pop()

        except KeyboardInterrupt:
            print("\n👋  Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    run_agent_interaction()

