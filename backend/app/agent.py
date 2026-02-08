"""
AI Agent configuration for Todo Chatbot.
Per specs/001-ai-chatbot/plan.md - Phase 5: AI Agent Construction
Phase V extensions: advanced task management tools, event emission.

Uses OpenAI SDK with Gemini API via base_url configuration.
Implements tool-calling pattern for task management operations.
"""
import json
import time
import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import get_settings
from app import mcp_tools
from app.events.producer import publish_event
from app.events.schemas import create_ai_tool_event
from app.events.topics import AI_EVENTS

logger = logging.getLogger(__name__)


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
MODEL = "gemini-2.5-flash-lite"


# ============================================================================
# System Prompt (T048: Updated for all 13 tools)
# ============================================================================

SYSTEM_PROMPT = """You are TodoBot, a friendly and helpful AI assistant for managing todo tasks. You communicate naturally in both English and Roman Urdu based on how the user writes to you.

## CAPABILITIES
You can help users with these 13 task operations (use the provided tools):

### Core Task Management
- **add_task**: Create new tasks (supports priority, tags, due_date, reminder_time)
- **list_tasks**: View tasks with optional filtering (all/pending/completed)
- **toggle_task_completion**: Mark tasks as complete or reopen them
- **delete_task**: Remove tasks (requires confirmation - call with confirmed=false first, then confirmed=true after user confirms)
- **search_tasks**: Find tasks by keyword in title, description, or tags
- **get_my_user_info**: Show user's account information

### Advanced Task Features
- **set_due_date**: Set or update a task's due date
- **set_priority**: Set task priority (low, medium, high, urgent)
- **add_tags**: Add tags to a task for organization
- **schedule_reminder**: Schedule a reminder notification for a task
- **create_recurring**: Set up recurring task rules (daily, weekly, monthly, yearly, custom)

### Filtering & Sorting
- **filter_tasks**: Filter tasks by status, priority, tags, or due date range
- **sort_tasks**: Sort tasks by created_at, due_date, priority, or title

## CRITICAL RULES

1. **Use Tools for ALL Operations**: You MUST use tools for any task operation. NEVER make up task data, IDs, or assume what tasks exist. If unsure what tasks exist, use list_tasks first.

2. **Task IDs**: When users refer to tasks by name/description, you should:
   - First use list_tasks to see available tasks
   - Match the user's description to actual task IDs
   - Use the correct task_id in subsequent operations

3. **Delete Confirmation Flow**: When deleting a task:
   - First call delete_task with confirmed=false to get the confirmation prompt
   - Show the user the task title they're about to delete
   - Ask for confirmation: "Are you sure you want to delete '[task title]'?"
   - Only call delete_task with confirmed=true if user confirms with "yes", "haan", "confirm", etc.
   - If user says "no", "nahi", "cancel", etc., do NOT proceed with deletion

4. **User Isolation**: You can ONLY access the current user's tasks. Never attempt to access other users' data.

5. **Language Matching**: Respond in the same language style the user uses:
   - English -> English
   - Roman Urdu -> Roman Urdu
   - Mixed -> You can mix naturally

6. **Advanced Features Usage**:
   - When creating tasks, offer to set priority, tags, or due date if the user mentions them
   - Use filter_tasks when users ask to see tasks by priority, tags, or date range
   - Use sort_tasks when users ask to see tasks ordered by a specific field
   - Use set_priority when users want to change a task's importance
   - Use add_tags when users want to categorize tasks
   - Use schedule_reminder when users want to be reminded about a task
   - Use create_recurring for tasks that repeat on a schedule

7. **Multi-turn Context**: Remember previous messages in the conversation. If the user refers to a task discussed earlier, use that context rather than asking again.

## RESPONSE STYLE

- Be conversational, warm, and helpful
- Confirm actions you've taken with specific details
- When listing tasks, format them clearly:
  - Use checkmarks for completed tasks and squares for pending tasks
  - Include task ID for reference
  - Show priority, tags, and due date when present
- Offer helpful suggestions when appropriate
- Keep responses concise but informative
- Never expose technical errors - translate to friendly messages

## EXAMPLES

User: "add high priority task buy groceries with tag shopping due tomorrow"
-> Call add_task with title="buy groceries", priority="high", tags=["shopping"], due_date="YYYY-MM-DD"
-> Respond with task details including priority and due date

User: "show me all urgent tasks"
-> Call filter_tasks with priority="urgent"
-> Respond with filtered task list

User: "sort my tasks by priority"
-> Call sort_tasks with sort_by="priority", sort_order="desc"
-> Respond with sorted task list

User: "remind me about task 5 tomorrow at 9am"
-> Call schedule_reminder with task_id=5, trigger_at="YYYY-MM-DDT09:00:00Z"
-> Confirm the reminder was scheduled

User: "make task 3 repeat every week"
-> Call create_recurring with task_id=3, frequency="weekly"
-> Confirm the recurring rule was set

User: "delete groceries task"
-> Call list_tasks to find the task
-> Call delete_task with confirmed=false to get task info
-> Ask: "Are you sure you want to delete 'buy groceries'?"
-> Wait for confirmation before calling delete_task with confirmed=true

## ERROR HANDLING

- If a task isn't found: "I couldn't find a task with that name/ID. Would you like to see your current tasks?"
- If no tasks exist: "You don't have any tasks yet. Would you like to add one?"
- If operation fails: "Something went wrong. Please try again."
"""


# ============================================================================
# Tool Definitions (OpenAI Function Format)
# T045-T047: All 13 tools with proper JSON schemas
# ============================================================================

TOOLS = [
    # --- Core Tools (updated schemas) ---
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new todo task for the user. Use when user wants to add, create, or make a new task. Supports priority, tags, due_date, and reminder_time.",
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
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Task priority level (default: medium)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags for categorization"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format"
                    },
                    "reminder_time": {
                        "type": "string",
                        "description": "Reminder time in ISO 8601 format (e.g., 2025-01-20T09:00:00Z)"
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
            "description": "Permanently delete a task. Requires confirmation: first call with confirmed=false to get task info, then call with confirmed=true after user confirms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    },
                    "confirmed": {
                        "type": "boolean",
                        "description": "Set to true to confirm deletion. First call should be false to get confirmation prompt."
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
            "description": "Search tasks by keyword in title, description, or tags. Use when user wants to find, search, or look for specific tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search term to match in task title, description, or tags"
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
    },
    # --- New Phase V Tools ---
    {
        "type": "function",
        "function": {
            "name": "set_due_date",
            "description": "Set or update the due date for a task. Use when user wants to set a deadline or due date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format"
                    }
                },
                "required": ["task_id", "due_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_reminder",
            "description": "Schedule a reminder notification for a task. Use when user wants to be reminded about a task at a specific time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task"
                    },
                    "trigger_at": {
                        "type": "string",
                        "description": "When to trigger the reminder in ISO 8601 format (e.g., 2025-01-20T09:00:00Z)"
                    }
                },
                "required": ["task_id", "trigger_at"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_recurring",
            "description": "Set up a recurring rule for a task. Use when user wants a task to repeat on a schedule (daily, weekly, monthly, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task"
                    },
                    "frequency": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly", "yearly", "custom"],
                        "description": "How often the task recurs"
                    },
                    "interval": {
                        "type": "integer",
                        "description": "Interval multiplier (e.g., 2 for every 2 weeks). Default: 1"
                    },
                    "day_of_week": {
                        "type": "integer",
                        "description": "Day of week for weekly recurrence (0=Monday, 6=Sunday)"
                    },
                    "day_of_month": {
                        "type": "integer",
                        "description": "Day of month for monthly recurrence (1-31)"
                    },
                    "cron_expression": {
                        "type": "string",
                        "description": "Custom cron expression (for frequency=custom)"
                    }
                },
                "required": ["task_id", "frequency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_priority",
            "description": "Set or change the priority level of a task. Use when user wants to mark a task as urgent, high priority, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level to set"
                    }
                },
                "required": ["task_id", "priority"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_tags",
            "description": "Add tags to a task for organization. Tags are deduplicated automatically. Use when user wants to categorize or label tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tag strings to add"
                    }
                },
                "required": ["task_id", "tags"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_tasks",
            "description": "Filter tasks by multiple criteria: status, priority, tags, due date range. Use when user wants to see specific subsets of tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "Filter by completion status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Filter by priority level"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (tasks matching any of these tags)"
                    },
                    "due_date_from": {
                        "type": "string",
                        "description": "Start of due date range (YYYY-MM-DD)"
                    },
                    "due_date_to": {
                        "type": "string",
                        "description": "End of due date range (YYYY-MM-DD)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sort_tasks",
            "description": "Sort and return all tasks by a specified field. Use when user wants to see tasks ordered by priority, due date, title, or creation date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "enum": ["created_at", "due_date", "priority", "title"],
                        "description": "Field to sort by"
                    },
                    "sort_order": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort direction (default: desc)"
                    }
                },
                "required": ["sort_by"]
            }
        }
    }
]


# ============================================================================
# Tool Dispatcher
# ============================================================================

# Map tool names to actual MCP tool functions (T045-T047: all 13 tools)
TOOL_FUNCTIONS = {
    # Core tools
    "add_task": mcp_tools.add_task,
    "list_tasks": mcp_tools.list_tasks,
    "toggle_task_completion": mcp_tools.toggle_task_completion,
    "delete_task": mcp_tools.delete_task,
    "search_tasks": mcp_tools.search_tasks,
    "get_my_user_info": mcp_tools.get_my_user_info,
    # Phase V: Advanced tools
    "set_due_date": mcp_tools.set_due_date,
    "schedule_reminder": mcp_tools.schedule_reminder,
    "create_recurring": mcp_tools.create_recurring,
    "set_priority": mcp_tools.set_priority,
    "add_tags": mcp_tools.add_tags,
    "filter_tasks": mcp_tools.filter_tasks,
    "sort_tasks": mcp_tools.sort_tasks,
}


async def execute_tool(user_id: str, tool_call) -> Dict[str, Any]:
    """
    Execute a tool call with user_id injection for security.
    Emits an ai_tool_called event after execution (fire-and-forget).

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

    # T049: Measure execution time and emit event
    start = time.time()

    # Execute the tool
    try:
        result = await tool_func(**arguments)

        # Calculate duration
        duration_ms = int((time.time() - start) * 1000)

        # Extract entity_id from arguments if present
        entity_id = str(arguments.get("task_id", "none"))

        # Fire-and-forget event emission
        try:
            event_data = create_ai_tool_event(
                entity_id=entity_id,
                user_id=user_id,
                tool_name=function_name,
                arguments={k: v for k, v in arguments.items() if k != "user_id"},
                result_status=result.get("status", "unknown"),
                duration_ms=duration_ms
            )
            asyncio.create_task(publish_event(AI_EVENTS, event_data))
        except Exception as event_err:
            logger.debug(f"Event emission failed (non-blocking): {event_err}")

        return result
    except Exception as e:
        # Calculate duration even on failure
        duration_ms = int((time.time() - start) * 1000)

        # Fire-and-forget error event
        try:
            event_data = create_ai_tool_event(
                entity_id=str(arguments.get("task_id", "none")),
                user_id=user_id,
                tool_name=function_name,
                arguments={k: v for k, v in arguments.items() if k != "user_id"},
                result_status="error",
                duration_ms=duration_ms
            )
            asyncio.create_task(publish_event(AI_EVENTS, event_data))
        except Exception as event_err:
            logger.debug(f"Event emission failed (non-blocking): {event_err}")

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
            print(f"[AGENT ERROR] {e}")  # Debug logging
            if "rate" in error_str or "quota" in error_str or "resource" in error_str:
                return "I'm getting a lot of requests right now. Please try again in a moment."
            elif "api_key" in error_str or "authentication" in error_str or "invalid" in error_str:
                return "I'm having trouble connecting. Please check API key configuration."
            else:
                return f"Something went wrong: {str(e)[:100]}"

    # Max iterations reached (shouldn't happen normally)
    return "I got a bit confused there. Could you try again?"
