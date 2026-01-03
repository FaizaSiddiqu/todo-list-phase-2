# Phase III: AI-Powered Todo Chatbot - Task Breakdown

**Version**: 1.0  
**Date**: January 3, 2026  
**Based on**: specs/003-chatbot/plan.md  
**Status**: Ready for Implementation

---

## Task Overview

| Task ID | Title | Estimated Time | Dependencies | Status |
|---------|-------|----------------|--------------|--------|
| T-001 | Database Schema Migration | 30 mins | None | 🔵 Ready |
| T-002 | Database Models Implementation | 30 mins | T-001 | 🔵 Ready |
| T-003 | MCP Tool: add_task | 30 mins | T-002 | 🔵 Ready |
| T-004 | MCP Tool: list_tasks | 30 mins | T-002 | 🔵 Ready |
| T-005 | MCP Tool: complete_task | 30 mins | T-002 | 🔵 Ready |
| T-006 | MCP Tool: delete_task | 30 mins | T-002 | 🔵 Ready |
| T-007 | MCP Tool: update_task | 30 mins | T-002 | 🔵 Ready |
| T-008 | OpenAI Agent Configuration | 45 mins | T-003-T-007 | 🔵 Ready |
| T-009 | Chat Endpoint Implementation | 1 hour | T-008 | 🔵 Ready |
| T-010 | Frontend Chat Page | 45 mins | T-009 | 🔵 Ready |
| T-011 | Environment Configuration | 15 mins | None | 🔵 Ready |
| T-012 | Testing & Validation | 1 hour | T-001-T-010 | 🔵 Ready |
| T-013 | Documentation Update | 30 mins | T-012 | 🔵 Ready |

**Total Estimated Time**: 7-8 hours

---

## Task Details

### T-001: Database Schema Migration

**Objective**: Create database migration to add conversation and message tables

**Preconditions**:
- Phase II database is operational
- Neon PostgreSQL connection configured

**Implementation Steps**:

1. Create migration file: `backend/migrations/003_add_chat_tables.sql`

```sql
-- Create conversation table
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for conversation
CREATE INDEX idx_conversation_user_id ON conversation(user_id);

-- Create message table
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for message
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_user_id ON message(user_id);
CREATE INDEX idx_message_created_at ON message(created_at);
```

2. Run migration script against Neon database
3. Verify tables created successfully
4. Test foreign key constraints

**Expected Outputs**:
- ✅ `conversation` table exists
- ✅ `message` table exists
- ✅ All indexes created
- ✅ Foreign keys enforced
- ✅ Check constraints working

**Validation**:
```sql
-- Verify tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('conversation', 'message');

-- Verify indexes
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('conversation', 'message');
```

**Rollback Plan**:
```sql
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS conversation CASCADE;
```

---

### T-002: Database Models Implementation

**Objective**: Add Conversation and Message SQLModel models to backend

**Preconditions**:
- T-001 completed (database tables exist)
- SQLModel imported in models.py

**Files to Modify**:
- `backend/app/models.py`

**Implementation**:

Add to `backend/app/models.py`:

```python
class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation {self.id} for user {self.user_id}>"


class Message(SQLModel, table=True):
    """Message model for chat history."""
    
    __tablename__ = "message"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(...)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"<Message {self.id} by {self.role}>"
```

**Expected Outputs**:
- ✅ Models defined with proper fields
- ✅ Foreign keys configured
- ✅ Indexes defined
- ✅ Type hints correct
- ✅ No import errors

**Validation**:
```python
# Test in Python REPL
from app.models import Conversation, Message
from sqlmodel import Session, select
from app.database import engine

# Create test conversation
with Session(engine) as session:
    conv = Conversation(user_id="test_user")
    session.add(conv)
    session.commit()
    assert conv.id is not None
```

---

### T-003: MCP Tool: add_task

**Objective**: Implement add_task MCP tool

**Preconditions**:
- T-002 completed (models available)
- MCP SDK installed (`pip install mcp`)

**Files to Create**:
- `backend/app/mcp_server/__init__.py`
- `backend/app/mcp_server/tools.py`

**Implementation**:

Create `backend/app/mcp_server/tools.py`:

```python
"""MCP tools for task operations."""
from mcp.server import MCPServer
from mcp.types import Tool, ToolParameter
from sqlmodel import Session, select
from ..models import Task
from ..database import engine
from datetime import datetime

# Initialize MCP server
mcp_server = MCPServer("todo-mcp-server")


@mcp_server.tool(
    name="add_task",
    description="Create a new todo task for the user",
    parameters=[
        ToolParameter(
            name="user_id",
            type="string",
            description="User identifier",
            required=True
        ),
        ToolParameter(
            name="title",
            type="string",
            description="Task title (1-200 characters)",
            required=True
        ),
        ToolParameter(
            name="description",
            type="string",
            description="Task description (optional, max 1000 characters)",
            required=False
        ),
    ]
)
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Add a new task for the user."""
    # Validate inputs
    if not title or not title.strip():
        return {
            "error": "Title is required and cannot be empty",
            "status": "validation_error"
        }
    
    if len(title) > 200:
        return {
            "error": "Title must be 200 characters or less",
            "status": "validation_error"
        }
    
    if description and len(description) > 1000:
        return {
            "error": "Description must be 1000 characters or less",
            "status": "validation_error"
        }
    
    # Create task
    try:
        with Session(engine) as session:
            task = Task(
                user_id=user_id,
                title=title.strip(),
                description=description.strip() if description else None,
                completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
    except Exception as e:
        return {
            "error": f"Failed to create task: {str(e)}",
            "status": "error"
        }
```

**Expected Outputs**:
- ✅ Tool registered with MCP server
- ✅ Parameters defined correctly
- ✅ Input validation working
- ✅ Task created in database
- ✅ Returns structured response

**Validation**:
```python
# Test tool directly
result = await add_task(
    user_id="test_user",
    title="Test Task",
    description="This is a test"
)
assert result["status"] == "created"
assert result["task_id"] is not None
```

---

### T-004: MCP Tool: list_tasks

**Objective**: Implement list_tasks MCP tool

**Preconditions**:
- T-003 completed (MCP server initialized)

**Implementation**:

Add to `backend/app/mcp_server/tools.py`:

```python
@mcp_server.tool(
    name="list_tasks",
    description="Retrieve user's tasks with optional status filter",
    parameters=[
        ToolParameter(
            name="user_id",
            type="string",
            description="User identifier",
            required=True
        ),
        ToolParameter(
            name="status",
            type="string",
            description="Filter by status: 'all', 'pending', or 'completed'",
            required=False
        ),
    ]
)
async def list_tasks(user_id: str, status: str = "all") -> dict:
    """List tasks for the user with optional status filter."""
    # Validate status
    if status not in ["all", "pending", "completed"]:
        return {
            "error": "Status must be 'all', 'pending', or 'completed'",
            "status": "validation_error"
        }
    
    try:
        with Session(engine) as session:
            # Build query
            query = select(Task).where(Task.user_id == user_id)
            
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)
            
            # Execute query
            tasks = session.exec(query.order_by(Task.created_at.desc())).all()
            
            return {
                "status": "success",
                "count": len(tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ]
            }
    except Exception as e:
        return {
            "error": f"Failed to list tasks: {str(e)}",
            "status": "error"
        }
```

**Expected Outputs**:
- ✅ Returns all tasks when status="all"
- ✅ Filters by completed status
- ✅ Filters by pending status
- ✅ Returns count and task array
- ✅ Handles empty results

**Validation**:
```python
# Test with no tasks
result = await list_tasks(user_id="new_user", status="all")
assert result["count"] == 0

# Test with tasks
await add_task(user_id="test_user", title="Task 1")
result = await list_tasks(user_id="test_user", status="pending")
assert result["count"] >= 1
```

---

### T-005: MCP Tool: complete_task

**Objective**: Implement complete_task MCP tool

**Preconditions**:
- T-003 completed (MCP server initialized)

**Implementation**:

Add to `backend/app/mcp_server/tools.py`:

```python
@mcp_server.tool(
    name="complete_task",
    description="Toggle task completion status",
    parameters=[
        ToolParameter(
            name="user_id",
            type="string",
            description="User identifier",
            required=True
        ),
        ToolParameter(
            name="task_id",
            type="integer",
            description="Task ID to complete",
            required=True
        ),
    ]
)
async def complete_task(user_id: str, task_id: int) -> dict:
    """Toggle task completion status."""
    try:
        with Session(engine) as session:
            # Fetch task
            task = session.get(Task, task_id)
            
            if not task:
                return {
                    "error": f"Task {task_id} not found",
                    "status": "not_found"
                }
            
            # Verify ownership
            if task.user_id != user_id:
                return {
                    "error": "Unauthorized: task belongs to another user",
                    "status": "unauthorized"
                }
            
            # Toggle completion
            task.completed = not task.completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "completed" if task.completed else "pending",
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
    except Exception as e:
        return {
            "error": f"Failed to complete task: {str(e)}",
            "status": "error"
        }
```

**Expected Outputs**:
- ✅ Toggles completion status
- ✅ Returns 404 for non-existent task
- ✅ Returns 403 for unauthorized access
- ✅ Updates timestamp
- ✅ Returns updated task state

**Validation**:
```python
# Create and complete task
task = await add_task(user_id="test_user", title="Test")
result = await complete_task(user_id="test_user", task_id=task["task_id"])
assert result["completed"] == True

# Toggle back
result = await complete_task(user_id="test_user", task_id=task["task_id"])
assert result["completed"] == False
```

---

### T-006: MCP Tool: delete_task

**Objective**: Implement delete_task MCP tool

**Preconditions**:
- T-003 completed (MCP server initialized)

**Implementation**:

Add to `backend/app/mcp_server/tools.py`:

```python
@mcp_server.tool(
    name="delete_task",
    description="Remove a task from the list",
    parameters=[
        ToolParameter(
            name="user_id",
            type="string",
            description="User identifier",
            required=True
        ),
        ToolParameter(
            name="task_id",
            type="integer",
            description="Task ID to delete",
            required=True
        ),
    ]
)
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task."""
    try:
        with Session(engine) as session:
            # Fetch task
            task = session.get(Task, task_id)
            
            if not task:
                return {
                    "error": f"Task {task_id} not found",
                    "status": "not_found"
                }
            
            # Verify ownership
            if task.user_id != user_id:
                return {
                    "error": "Unauthorized: task belongs to another user",
                    "status": "unauthorized"
                }
            
            # Store info before deletion
            task_info = {
                "task_id": task.id,
                "title": task.title
            }
            
            # Delete task
            session.delete(task)
            session.commit()
            
            return {
                **task_info,
                "status": "deleted"
            }
    except Exception as e:
        return {
            "error": f"Failed to delete task: {str(e)}",
            "status": "error"
        }
```

**Expected Outputs**:
- ✅ Deletes task from database
- ✅ Returns 404 for non-existent task
- ✅ Returns 403 for unauthorized access
- ✅ Returns deleted task info
- ✅ Task no longer queryable

**Validation**:
```python
# Create and delete task
task = await add_task(user_id="test_user", title="To Delete")
result = await delete_task(user_id="test_user", task_id=task["task_id"])
assert result["status"] == "deleted"

# Verify deletion
list_result = await list_tasks(user_id="test_user")
assert task["task_id"] not in [t["id"] for t in list_result["tasks"]]
```

---

### T-007: MCP Tool: update_task

**Objective**: Implement update_task MCP tool

**Preconditions**:
- T-003 completed (MCP server initialized)

**Implementation**:

Add to `backend/app/mcp_server/tools.py`:

```python
@mcp_server.tool(
    name="update_task",
    description="Modify task title or description",
    parameters=[
        ToolParameter(
            name="user_id",
            type="string",
            description="User identifier",
            required=True
        ),
        ToolParameter(
            name="task_id",
            type="integer",
            description="Task ID to update",
            required=True
        ),
        ToolParameter(
            name="title",
            type="string",
            description="New task title (optional)",
            required=False
        ),
        ToolParameter(
            name="description",
            type="string",
            description="New task description (optional)",
            required=False
        ),
    ]
)
async def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None
) -> dict:
    """Update task details."""
    # Validate at least one field provided
    if title is None and description is None:
        return {
            "error": "At least one field (title or description) must be provided",
            "status": "validation_error"
        }
    
    # Validate title length
    if title and len(title) > 200:
        return {
            "error": "Title must be 200 characters or less",
            "status": "validation_error"
        }
    
    # Validate description length
    if description and len(description) > 1000:
        return {
            "error": "Description must be 1000 characters or less",
            "status": "validation_error"
        }
    
    try:
        with Session(engine) as session:
            # Fetch task
            task = session.get(Task, task_id)
            
            if not task:
                return {
                    "error": f"Task {task_id} not found",
                    "status": "not_found"
                }
            
            # Verify ownership
            if task.user_id != user_id:
                return {
                    "error": "Unauthorized: task belongs to another user",
                    "status": "unauthorized"
                }
            
            # Update fields
            if title is not None:
                task.title = title.strip()
            if description is not None:
                task.description = description.strip() if description else None
            
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
                "description": task.description,
                "updated_at": task.updated_at.isoformat()
            }
    except Exception as e:
        return {
            "error": f"Failed to update task: {str(e)}",
            "status": "error"
        }
```

**Expected Outputs**:
- ✅ Updates title when provided
- ✅ Updates description when provided
- ✅ Updates both fields together
- ✅ Returns 404 for non-existent task
- ✅ Returns 403 for unauthorized access
- ✅ Validates field lengths

**Validation**:
```python
# Create and update task
task = await add_task(user_id="test_user", title="Original")
result = await update_task(
    user_id="test_user",
    task_id=task["task_id"],
    title="Updated Title"
)
assert result["title"] == "Updated Title"
```

---

### T-008: OpenAI Agent Configuration

**Objective**: Set up OpenAI Agents SDK and create TodoAssistant agent

**Preconditions**:
- T-003 to T-007 completed (all MCP tools implemented)
- OpenAI API key configured
- `openai` and `openai-agents-sdk` installed

**Files to Create**:
- `backend/app/agents/__init__.py`
- `backend/app/agents/todo_agent.py`

**Implementation**:

Create `backend/app/agents/todo_agent.py`:

```python
"""OpenAI Agent configuration for TodoAssistant."""
import os
from openai import OpenAI
from openai.agents import Agent

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
3. If users ask ambiguous questions, ask for clarification
4. Be friendly, concise, and action-oriented
5. Use natural language responses, not JSON
6. Format task lists in a readable way with numbers or bullets
7. Use emojis sparingly (✅ for success, ❌ for errors)

Example responses:
- "✅ I've added 'Buy groceries' to your list (Task #5)"
- "You have 3 pending tasks:\n1. Buy groceries\n2. Call mom\n3. Pay bills"
- "✅ Marked 'Call mom' as complete!"
- "❌ I couldn't find that task. Could you provide the task ID?"

Remember: You're conversational and helpful, not robotic!
"""

# Create TodoAssistant agent
todo_agent = Agent(
    name="TodoAssistant",
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    instructions=AGENT_INSTRUCTIONS,
    tools=[
        # MCP tools will be registered from mcp_server.tools
        "add_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "update_task"
    ],
    temperature=0.7  # Balanced creativity and consistency
)


async def run_agent(user_id: str, messages: list) -> dict:
    """
    Run the TodoAssistant agent with conversation history.
    
    Args:
        user_id: User identifier (injected into tool calls)
        messages: List of message dicts with 'role' and 'content'
    
    Returns:
        dict with 'response' and 'tool_calls'
    
    Example:
        messages = [
            {"role": "user", "content": "Add a task to buy milk"},
            {"role": "assistant", "content": "✅ Added task..."},
            {"role": "user", "content": "Show my tasks"}
        ]
        result = await run_agent("user123", messages)
        # Returns: {"response": "...", "tool_calls": [...]}
    """
    # Inject user_id into agent context
    # This will be automatically passed to all tool calls
    agent_context = {"user_id": user_id}
    
    try:
        # Run agent with conversation history
        result = await todo_agent.run(
            messages=messages,
            context=agent_context
        )
        
        return {
            "response": result.content,
            "tool_calls": [
                {
                    "tool": call.tool_name,
                    "parameters": call.parameters,
                    "result": call.result
                }
                for call in result.tool_calls
            ] if hasattr(result, 'tool_calls') else []
        }
    except Exception as e:
        # Handle agent errors gracefully
        return {
            "response": f"❌ I encountered an error: {str(e)}. Please try again.",
            "tool_calls": [],
            "error": str(e)
        }
```

**Expected Outputs**:
- ✅ Agent initialized with correct model
- ✅ Instructions loaded
- ✅ Tools registered
- ✅ `run_agent` function works
- ✅ user_id injected into context
- ✅ Error handling implemented

**Validation**:
```python
# Test agent with simple conversation
messages = [{"role": "user", "content": "Hello"}]
result = await run_agent("test_user", messages)
assert "response" in result
assert isinstance(result["tool_calls"], list)
```

---

### T-009: Chat Endpoint Implementation

**Objective**: Create POST /api/{user_id}/chat endpoint

**Preconditions**:
- T-008 completed (agent configured)
- T-002 completed (models available)

**Files to Create**:
- `backend/app/routes/chat.py`

**Files to Modify**:
- `backend/app/main.py` (include router)

**Implementation**:

Create `backend/app/routes/chat.py`:

```python
"""Chat endpoint for conversational task management."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime

from ..database import get_session
from ..models import Conversation, Message
from ..auth import get_current_user
from ..agents.todo_agent import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request schema."""
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID (optional)")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class ChatResponse(BaseModel):
    """Chat response schema."""
    conversation_id: int
    response: str
    tool_calls: list


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Chat endpoint for conversational task management.
    
    Flow:
    1. Validate user authentication
    2. Create or retrieve conversation
    3. Store user message
    4. Load conversation history (last 10 messages)
    5. Run AI agent
    6. Store assistant response
    7. Return response
    
    Args:
        user_id: User identifier from path
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user: Authenticated user from JWT
    
    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    
    Raises:
        403: User doesn't own the conversation
        404: Conversation not found
        500: Agent error
    """
    
    # 1. Validate user authentication
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversation"
        )
    
    # 2. Create or retrieve conversation
    if request.conversation_id:
        # Retrieve existing conversation
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # 3. Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()
    
    # 4. Load conversation history (last 10 messages)
    history_query = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .limit(10)
    )
    history = session.exec(history_query).all()
    
    # Build message array for agent
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]
    
    # 5. Run AI agent
    try:
        agent_result = await run_agent(user_id, messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
        )
    
    # 6. Store assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=agent_result["response"]
    )
    session.add(assistant_message)
    session.commit()
    
    # 7. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_result["response"],
        tool_calls=agent_result.get("tool_calls", [])
    )
```

Update `backend/app/main.py`:

```python
# Add import
from .routes.chat import router as chat_router

# Include router
app.include_router(chat_router)
```

**Expected Outputs**:
- ✅ Endpoint accepts POST requests
- ✅ JWT authentication required
- ✅ Conversation created/retrieved correctly
- ✅ Messages stored in database
- ✅ Agent runs successfully
- ✅ Response returned to client
- ✅ Error handling works

**Validation**:
```bash
# Test endpoint with curl
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy milk"}'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "✅ I've added 'Buy milk' to your list (Task #1)",
#   "tool_calls": [{"tool": "add_task", ...}]
# }
```

---

### T-010: Frontend Chat Page

**Objective**: Create chat interface using OpenAI ChatKit

**Preconditions**:
- T-009 completed (chat endpoint working)
- `openai-chatkit` installed

**Files to Create**:
- `frontend/src/app/chat/page.tsx`

**Files to Modify**:
- `frontend/src/app/dashboard/page.tsx` (add link to chat)
- `frontend/package.json` (add dependency)

**Implementation**:

1. Install ChatKit:
```bash
cd frontend
npm install openai-chatkit
```

2. Create `frontend/src/app/chat/page.tsx`:

```typescript
"use client";

import { ChatKit } from "openai-chatkit";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const { user } = useAuth();
  const router = useRouter();

  if (!user) {
    router.push("/login");
    return null;
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Todo Chatbot
        </h1>
        <p className="text-gray-600">
          Manage your tasks using natural language. Try saying "Add a task to buy milk" or "Show my tasks".
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg p-4">
        <ChatKit
          apiUrl={`/api/${user.id}/chat`}
          headers={{
            Authorization: `Bearer ${user.token}`,
          }}
          placeholder="Ask me to manage your tasks..."
          className="h-[600px] w-full"
          welcomeMessage="👋 Hi! I'm your todo assistant. I can help you add, view, complete, delete, and update tasks. What would you like to do?"
        />
      </div>
      
      <div className="mt-4 text-sm text-gray-500">
        <p className="mb-2">💡 Example commands:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Add a task to buy groceries</li>
          <li>Show me all my tasks</li>
          <li>Mark task 3 as complete</li>
          <li>Delete the meeting task</li>
          <li>Update task 1 to "Call mom tonight"</li>
        </ul>
      </div>
    </div>
  );
}
```

3. Add link in `frontend/src/app/dashboard/page.tsx`:

```typescript
// Add to dashboard navigation
<Link href="/chat">
  <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
    💬 Chat with AI
  </button>
</Link>
```

**Expected Outputs**:
- ✅ Chat page accessible at /chat
- ✅ ChatKit component renders
- ✅ Messages send to backend
- ✅ Responses display in chat
- ✅ Conversation persists
- ✅ UI is responsive

**Validation**:
1. Navigate to http://localhost:3000/chat
2. Type "Add a task to buy milk"
3. Verify task created in backend
4. Type "Show my tasks"
5. Verify task list displayed

---

### T-011: Environment Configuration

**Objective**: Set up environment variables for Phase III

**Preconditions**:
- OpenAI API key obtained
- OpenAI domain allowlist configured

**Files to Modify**:
- `backend/.env`
- `frontend/.env.local`
- `backend/requirements.txt`
- `frontend/package.json`

**Implementation**:

1. Update `backend/.env`:
```env
# Existing
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...

# Phase III - Add these
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

2. Update `frontend/.env.local`:
```env
# Existing
NEXT_PUBLIC_API_URL=http://localhost:8000

# Phase III - Add this (after domain allowlist setup)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

3. Update `backend/requirements.txt`:
```txt
# Existing dependencies
fastapi
sqlmodel
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-multipart
uvicorn

# Phase III - Add these
openai>=1.0.0
openai-agents-sdk>=0.1.0
mcp>=1.0.0
httpx>=0.25.0
```

4. Update `frontend/package.json`:
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "openai-chatkit": "^1.0.0"
  }
}
```

5. Install dependencies:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

**Expected Outputs**:
- ✅ All environment variables set
- ✅ Dependencies installed
- ✅ No import errors
- ✅ OpenAI API key valid
- ✅ ChatKit domain configured

**Validation**:
```python
# Test OpenAI connection
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assert client.models.list() is not None
```

---

### T-012: Testing & Validation

**Objective**: Test all Phase III functionality end-to-end

**Preconditions**:
- All tasks T-001 to T-011 completed

**Test Scenarios**:

**1. Database Models Test**
```python
def test_conversation_creation():
    with Session(engine) as session:
        conv = Conversation(user_id="test_user")
        session.add(conv)
        session.commit()
        assert conv.id is not None

def test_message_creation():
    # ... similar test
```

**2. MCP Tools Test**
```python
async def test_add_task():
    result = await add_task(
        user_id="test_user",
        title="Test Task",
        description="Test Description"
    )
    assert result["status"] == "created"
    assert result["task_id"] is not None

async def test_list_tasks():
    # ... test listing

async def test_complete_task():
    # ... test completion

async def test_delete_task():
    # ... test deletion

async def test_update_task():
    # ... test update
```

**3. Chat Endpoint Test**
```python
def test_chat_endpoint(client, auth_headers):
    response = client.post(
        "/api/test_user/chat",
        headers=auth_headers,
        json={"message": "Add a task to buy milk"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
```

**4. Frontend Integration Test**
- Manual test: Navigate to /chat
- Send message: "Add a task to test integration"
- Verify task created in backend
- Verify response displayed in UI

**Expected Outputs**:
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ End-to-end flow works
- ✅ Error handling works
- ✅ Phase II tests still pass

**Validation Command**:
```bash
# Run tests
cd backend
pytest

# Expected output:
# ====================== test session starts ======================
# collected 15 items
#
# tests/test_models.py::test_conversation_creation PASSED
# tests/test_models.py::test_message_creation PASSED
# tests/test_mcp_tools.py::test_add_task PASSED
# ...
# ======================= 15 passed in 5.23s =======================
```

---

### T-013: Documentation Update

**Objective**: Update project documentation for Phase III

**Preconditions**:
- T-012 completed (all testing done)

**Files to Create/Update**:
- `todo-fullstack/README.md` (update)
- `specs/003-chatbot/README.md` (create)

**Implementation**:

1. Update `todo-fullstack/README.md`:

```markdown
# Todo Full-Stack Application

## Phases Completed

- ✅ **Phase I**: Console App (Python)
- ✅ **Phase II**: Web Application (Next.js + FastAPI)
- ✅ **Phase III**: AI Chatbot (OpenAI Agents + MCP) ← NEW

## Phase III: AI Chatbot Features

- 🤖 Natural language task management
- 💬 Conversational interface using OpenAI ChatKit
- 🛠️ 5 MCP tools for task operations
- 📝 Persistent conversation history
- 🔒 Secure JWT authentication
- 🚀 Stateless architecture

## Quick Start (Phase III)

### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set environment variables:
```bash
cp .env.example .env
# Add OPENAI_API_KEY=sk-...
```

3. Run database migrations:
```bash
python -m app.migrations.003_add_chat_tables
```

4. Start server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set environment variables:
```bash
cp .env.example .env.local
# Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

3. Start development server:
```bash
npm run dev
```

### Using the Chatbot

1. Navigate to http://localhost:3000/chat
2. Log in with your credentials
3. Start chatting! Try:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 3 as complete"
   - "Delete the meeting task"

## Architecture

See [specs/003-chatbot/spec.md](specs/003-chatbot/spec.md) for detailed architecture and design decisions.

## MCP Tools

- `add_task`: Create new tasks
- `list_tasks`: View tasks with filters
- `complete_task`: Toggle completion status
- `delete_task`: Remove tasks
- `update_task`: Modify task details

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend (manual testing recommended for ChatKit)
cd frontend
npm run dev
# Navigate to /chat and test interactions
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, OpenAI ChatKit |
| Backend | FastAPI, OpenAI Agents SDK |
| Tools | Official MCP SDK |
| Database | Neon PostgreSQL |
| Auth | Better Auth (JWT) |

## License

MIT
```

2. Create `specs/003-chatbot/README.md`:

```markdown
# Phase III: AI Chatbot - Implementation Summary

## Overview

This phase adds conversational AI capabilities to the todo application using OpenAI Agents SDK and Model Context Protocol (MCP).

## Files Created

- `backend/app/models.py` - Added Conversation and Message models
- `backend/app/mcp_server/tools.py` - 5 MCP tools
- `backend/app/agents/todo_agent.py` - OpenAI agent configuration
- `backend/app/routes/chat.py` - Chat endpoint
- `frontend/src/app/chat/page.tsx` - ChatKit UI

## Database Schema

```sql
-- New tables
CREATE TABLE conversation (...)
CREATE TABLE message (...)
```

## API Endpoints

- `POST /api/{user_id}/chat` - Send message, get AI response

## MCP Tools

1. add_task
2. list_tasks
3. complete_task
4. delete_task
5. update_task

## Testing

All tests pass. See [tasks.md](tasks.md) for test scenarios.

## Deployment

No changes to Phase II deployment. Just add environment variables for OpenAI API key.

## Next Steps

Phase IV: Kubernetes Deployment (local Minikube)
```

**Expected Outputs**:
- ✅ README.md updated with Phase III info
- ✅ Setup instructions clear
- ✅ Environment variables documented
- ✅ Architecture diagrams included
- ✅ Example commands provided

**Validation**:
- New developer can follow README and run the application
- All environment variables documented
- Setup steps are clear and complete

---

## Implementation Order Summary

**Priority 1: Foundation** (Complete First)
1. T-001: Database Schema
2. T-002: Database Models
3. T-011: Environment Configuration

**Priority 2: MCP Tools** (Can be parallelized)
4. T-003: add_task
5. T-004: list_tasks
6. T-005: complete_task
7. T-006: delete_task
8. T-007: update_task

**Priority 3: Integration** (Sequential)
9. T-008: Agent Configuration
10. T-009: Chat Endpoint
11. T-010: Frontend Chat Page

**Priority 4: Quality** (Final Step)
12. T-012: Testing & Validation
13. T-013: Documentation

---

## Testing Checklist

After completing all tasks, verify:

- [ ] Database tables created
- [ ] All 5 MCP tools work independently
- [ ] Agent responds to natural language
- [ ] Chat endpoint returns responses
- [ ] Conversation persists across requests
- [ ] ChatKit UI displays correctly
- [ ] JWT authentication enforced
- [ ] User data isolated by user_id
- [ ] Error handling works
- [ ] Phase II functionality unaffected
- [ ] Documentation updated
- [ ] Demo video created

---

**Tasks Status**: ✅ Complete and Ready for Implementation

**Next Step**: Begin implementation with T-001 (Database Schema Migration)

**Estimated Completion Time**: 7-8 hours for solo developer, 4-5 hours with pair programming

