"""OpenAI Agent configuration for TodoAssistant.

This module configures the OpenAI agent that handles natural language
conversations for task management. The agent uses MCP tools to perform
operations on behalf of the user.
"""
import os
from typing import List, Dict, Any
import json

from ..mcp_server.tools import mcp_tools


# Agent instructions
AGENT_INSTRUCTIONS = """
You are TodoAssistant, a helpful AI that manages todo tasks for users.

You can help users:
- Add new tasks (use add_task tool)
- View their task list (use list_tasks tool)
- Mark tasks as complete (use complete_task tool)
- Delete tasks (use delete_task tool)
- Update task details (use update_task tool)

Guidelines:
1. Always confirm actions clearly with task ID and title
2. When tasks are created, updated, or deleted, provide specific feedback
3. If users ask ambiguous questions, ask for clarification rather than guessing
4. Be friendly, concise, and action-oriented
5. Use natural language responses, not JSON
6. Format task lists in a readable way with numbers or bullets
7. Use emojis sparingly (✅ for success, ❌ for errors, 📝 for lists)

Example responses:
- "✅ I've added 'Buy groceries' to your list (Task #5)"
- "You have 3 pending tasks:\\n1. Buy groceries\\n2. Call mom\\n3. Pay bills"
- "✅ Marked 'Call mom' as complete!"
- "❌ I couldn't find that task. Could you provide the task ID?"

When listing tasks:
- Format them clearly with numbers
- Show title and completion status
- Mention task IDs for easy reference
- Summarize the count at the end

Remember: You're conversational and helpful, not robotic!
"""


async def run_agent(user_id: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Run the TodoAssistant agent with conversation history.
    
    This function processes user messages using OpenAI's API and
    MCP tools to perform task operations.
    
    Args:
        user_id: User identifier (passed to all tool calls)
        messages: List of message dicts with 'role' and 'content'
            Example: [{"role": "user", "content": "Add a task"}]
    
    Returns:
        dict with 'response' and 'tool_calls'
        Example: {
            "response": "✅ I've added the task...",
            "tool_calls": [{"tool": "add_task", "result": {...}}]
        }
    """
    try:
        # Import OpenAI here to avoid import errors if not installed
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Build system message with instructions
        system_message = {"role": "system", "content": AGENT_INSTRUCTIONS}
        all_messages = [system_message] + messages
        
        # Define available tools in OpenAI function calling format
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new todo task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (1-200 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional, max 1000 characters)"
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
                    "description": "Retrieve user's tasks with optional status filter",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by status: 'all', 'pending', or 'completed'"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Toggle task completion status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Task ID to complete"
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
                    "description": "Remove a task from the list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Task ID to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Modify task title or description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Task ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]
        
        # Call OpenAI API with function calling
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=all_messages,
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        tool_calls_made = []
        
        # Handle tool calls if any
        if message.tool_calls:
            # Add assistant message to conversation
            all_messages.append(message)
            
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Inject user_id into function call
                function_args["user_id"] = user_id
                
                # Execute the tool
                if function_name == "add_task":
                    result = await mcp_tools.add_task(**function_args)
                elif function_name == "list_tasks":
                    result = await mcp_tools.list_tasks(**function_args)
                elif function_name == "complete_task":
                    result = await mcp_tools.complete_task(**function_args)
                elif function_name == "delete_task":
                    result = await mcp_tools.delete_task(**function_args)
                elif function_name == "update_task":
                    result = await mcp_tools.update_task(**function_args)
                else:
                    result = {"error": f"Unknown tool: {function_name}"}
                
                # Add tool call result to tracking
                tool_calls_made.append({
                    "tool": function_name,
                    "parameters": function_args,
                    "result": result
                })
                
                # Add tool result to conversation
                all_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result)
                })
            
            # Get final response after tool execution
            final_response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=all_messages
            )
            
            final_message = final_response.choices[0].message.content
        else:
            # No tool calls, use direct response
            final_message = message.content
        
        return {
            "response": final_message,
            "tool_calls": tool_calls_made
        }
        
    except Exception as e:
        # Handle errors gracefully
        return {
            "response": f"❌ I encountered an error: {str(e)}. Please try again or contact support.",
            "tool_calls": [],
            "error": str(e)
        }
