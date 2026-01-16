"""
AI Agent configuration for Todo Chatbot.
Per specs/001-ai-chatbot/plan.md - Phase 5: AI Agent Construction

Uses OpenAI SDK with Gemini API via base_url configuration.
Implements tool-calling pattern for task management operations.
"""
import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import get_settings
from app import mcp_tools


# ============================================================================
# OpenAI Client Configuration (with Gemini API)
# ============================================================================

def get_openai_client() -> OpenAI:
    """
    Create OpenAI client configured to use Gemini API.

    Uses the OpenAI SDK's compatibility layer with Gemini's endpoint.
    """
    settings = get_settings()
    return OpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )


# Model to use for chat completions
MODEL = "gemini-2.0-flash-exp"


# ============================================================================
# System Prompt
# ============================================================================

SYSTEM_PROMPT = """You are TodoBot, a friendly and helpful AI assistant for managing todo tasks. You communicate naturally in both English and Roman Urdu based on how the user writes to you.

## CAPABILITIES
You can help users with these task operations (use the provided tools):
- **add_task**: Create new tasks
- **list_tasks**: View tasks with optional filtering (all/pending/completed)
- **toggle_task_completion**: Mark tasks as complete or reopen them
- **delete_task**: Remove tasks (ALWAYS ask for confirmation first!)
- **search_tasks**: Find tasks by keyword
- **get_my_user_info**: Show user's account information

## CRITICAL RULES

1. **Use Tools for ALL Operations**: You MUST use tools for any task operation. NEVER make up task data, IDs, or assume what tasks exist. If unsure what tasks exist, use list_tasks first.

2. **Task IDs**: When users refer to tasks by name/description, you should:
   - First use list_tasks to see available tasks
   - Match the user's description to actual task IDs
   - Use the correct task_id in subsequent operations

3. **Delete Confirmation**: Before calling delete_task, you MUST:
   - Show the user the task title they're about to delete
   - Ask "Are you sure you want to delete '[task title]'?"
   - Only proceed if user confirms with "yes", "haan", "confirm", etc.
   - If user says "no", "nahi", "cancel", etc., do NOT delete

4. **User Isolation**: You can ONLY access the current user's tasks. Never attempt to access other users' data.

5. **Language Matching**: Respond in the same language style the user uses:
   - English → English
   - Roman Urdu → Roman Urdu
   - Mixed → You can mix naturally

## RESPONSE STYLE

- Be conversational, warm, and helpful
- Confirm actions you've taken with specific details
- When listing tasks, format them clearly:
  - ✅ for completed tasks
  - ⬜ for pending tasks
  - Include task ID for reference
- Offer helpful suggestions when appropriate
- Keep responses concise but informative
- Never expose technical errors - translate to friendly messages

## EXAMPLES

User: "add task buy groceries"
→ Call add_task with title="buy groceries"
→ Respond: "Done! I've added 'buy groceries' to your list."

User: "meri tasks dikhao"
→ Call list_tasks
→ Respond with formatted task list in Roman Urdu

User: "delete groceries task"
→ Call list_tasks to find the task
→ Ask: "Kya aap 'buy groceries' delete karna chahte hain?"
→ Wait for confirmation before calling delete_task

User: "who am I?"
→ Call get_my_user_info
→ Respond with user's email and name

## ERROR HANDLING

- If a task isn't found: "I couldn't find a task with that name/ID. Would you like to see your current tasks?"
- If no tasks exist: "You don't have any tasks yet. Would you like to add one?"
- If operation fails: "Something went wrong. Please try again."
"""


# ============================================================================
# Tool Definitions (OpenAI Function Format)
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new todo task for the user. Use when user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description (max 1000 characters)"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user. Use when user wants to see, show, view, or check their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by task status. Use 'pending' for incomplete tasks, 'completed' for done tasks, 'all' for everything."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_task_completion",
            "description": "Toggle a task's completion status. Use when user wants to complete, finish, mark done, check off, or reopen/uncheck a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to toggle"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task. IMPORTANT: Always confirm with the user before calling this function by showing them the task title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by keyword in title or description. Use when user wants to find, search, or look for specific tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search term to match in task title or description"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by task status"
                    }
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_user_info",
            "description": "Get the user's account information (email, name). Use when user asks about their identity, email, account, or 'who am I'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ============================================================================
# Tool Dispatcher
# ============================================================================

# Map tool names to actual MCP tool functions
TOOL_FUNCTIONS = {
    "add_task": mcp_tools.add_task,
    "list_tasks": mcp_tools.list_tasks,
    "toggle_task_completion": mcp_tools.toggle_task_completion,
    "delete_task": mcp_tools.delete_task,
    "search_tasks": mcp_tools.search_tasks,
    "get_my_user_info": mcp_tools.get_my_user_info,
}


async def execute_tool(user_id: str, tool_call) -> Dict[str, Any]:
    """
    Execute a tool call with user_id injection for security.

    Args:
        user_id: The authenticated user's ID (from JWT)
        tool_call: The tool call object from OpenAI API

    Returns:
        Tool result dictionary
    """
    function_name = tool_call.function.name

    # Parse arguments
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        arguments = {}

    # Get the tool function
    tool_func = TOOL_FUNCTIONS.get(function_name)
    if not tool_func:
        return {
            "status": "error",
            "message": f"Unknown tool: {function_name}",
            "data": None
        }

    # Inject user_id (security: never trust user-provided user_id)
    arguments["user_id"] = user_id

    # Execute the tool
    try:
        result = await tool_func(**arguments)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}",
            "data": None
        }


# ============================================================================
# Agent Runner
# ============================================================================

async def run_agent(
    user_id: str,
    user_message: str,
    conversation_history: List[Dict[str, Any]] = None
) -> str:
    """
    Run the TodoOrchestratorAgent with the given user message.

    Implements the tool execution loop:
    1. Send message to AI with tools
    2. If AI calls tools, execute them and continue
    3. Repeat until AI returns final text response

    Args:
        user_id: The authenticated user's ID (from JWT)
        user_message: The user's chat message
        conversation_history: Previous messages in the conversation

    Returns:
        The assistant's final text response
    """
    client = get_openai_client()

    # Build messages array
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Maximum iterations to prevent infinite loops
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            # Call the AI
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
            )

            assistant_message = response.choices[0].message

            # Check if AI wants to call tools
            if assistant_message.tool_calls:
                # Add assistant's message (with tool calls) to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    result = await execute_tool(user_id, tool_call)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

                # Continue the loop to get AI's response to tool results
                continue

            # No tool calls - this is the final response
            return assistant_message.content or "I'm not sure how to help with that. Could you rephrase?"

        except Exception as e:
            # Handle API errors gracefully
            error_str = str(e).lower()
            if "rate" in error_str or "quota" in error_str:
                return "I'm getting a lot of requests right now. Please try again in a moment."
            elif "api_key" in error_str or "authentication" in error_str:
                return "I'm having trouble connecting. Please try again later."
            else:
                return "Something went wrong. Please try again."

    # Max iterations reached (shouldn't happen normally)
    return "I got a bit confused there. Could you try again?"
