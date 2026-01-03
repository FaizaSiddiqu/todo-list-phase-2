# Backend Guidelines - FastAPI + AI Agent + MCP

> **Context**: Python FastAPI backend with OpenAI Agents SDK and MCP Server

---

## Quick Reference

**Read First**: @../AGENTS.md and @../.specify/memory/constitution.md

**Current Phase**: III - AI Chatbot  
**Framework**: FastAPI  
**Python**: 3.13+  
**AI**: OpenAI Agents SDK  
**Tools**: Custom MCP Tools

---

## Stack

- **Framework**: FastAPI 0.128.0+
- **ORM**: SQLModel 0.0.31+
- **Database**: PostgreSQL (Neon Serverless)
- **AI**: OpenAI Agents SDK (gpt-4o-mini)
- **MCP**: Custom tools (Official MCP SDK patterns)
- **Auth**: JWT with python-jose + bcrypt

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # JWT authentication utilities
│   ├── agents/
│   │   └── todo_agent.py    # OpenAI Agents SDK integration
│   ├── mcp_server/
│   │   └── tools.py         # MCP tools (5 task operations)
│   └── routes/
│       ├── auth.py          # Authentication endpoints
│       ├── tasks.py         # Task CRUD endpoints
│       └── chat.py          # Chat endpoint (Phase III)
├── requirements.txt
└── .env
```

---

## Code Patterns

### 1. Type Hints (MANDATORY)

```python
# All functions must have complete type hints
from typing import Optional
from sqlmodel import Session

def create_task(
    title: str,
    description: Optional[str],
    user_id: str,
    session: Session
) -> Task:
    """Create a new task for a user."""
    task = Task(
        title=title,
        description=description,
        user_id=user_id
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### 2. Async/Await for Database

```python
# Use async for all route handlers
from fastapi import Depends
from sqlmodel import Session, select

@router.get("/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> list[Task]:
    """Get all tasks for authenticated user."""
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    ).all()
    return tasks
```

### 3. User Data Isolation (CRITICAL)

```python
# ALWAYS filter by user_id - NO EXCEPTIONS
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """Get a specific task."""
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id  # ALWAYS include this
        )
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task
```

### 4. Error Handling

```python
from fastapi import HTTPException, status

# Use appropriate HTTP status codes
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """Create a new task."""
    if not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    # Create task...
    return task
```

---

## Database Models (SQLModel)

### Pattern
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Relationships
```python
# User can have many tasks
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    # ...

# Task belongs to user
class Task(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    # ...
```

---

## Authentication

### JWT Pattern
```python
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

---

## OpenAI Agents SDK (Phase III)

### Agent Setup
```python
from openai import OpenAI
from openai.agents import Agent, Runner

client = OpenAI(api_key=settings.openai_api_key)

agent = Agent(
    name="todo_assistant",
    model="gpt-4o-mini",
    instructions="You are a helpful todo assistant...",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

runner = Runner(agent=agent, client=client)
```

### Running Agent
```python
async def run_agent(user_message: str, conversation_id: int, user_id: str) -> str:
    """Run agent with conversation history."""
    # 1. Fetch conversation history from database
    messages = get_conversation_messages(conversation_id)
    
    # 2. Add user message
    messages.append({"role": "user", "content": user_message})
    
    # 3. Run agent
    response = runner.run(messages=messages)
    
    # 4. Store messages in database
    store_message(conversation_id, "user", user_message)
    store_message(conversation_id, "assistant", response.content)
    
    return response.content
```

---

## MCP Tools (Phase III)

### Tool Pattern
```python
from typing import Dict, Any

def add_task(user_id: str, title: str, description: str = None) -> Dict[str, Any]:
    """MCP Tool: Add a new task.
    
    Args:
        user_id: User ID from conversation context
        title: Task title (required)
        description: Task description (optional)
    
    Returns:
        Dict with task_id, status, and title
    """
    session = get_db_session()
    
    task = Task(
        user_id=user_id,
        title=title,
        description=description
    )
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }
```

### Tool Registration
```python
# Register tools with OpenAI Agents SDK
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        }
    },
    # ... other tools
]
```

---

## API Routes

### Pattern
```python
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all tasks for authenticated user."""
    # Implementation...

@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new task."""
    # Implementation...
```

---

## Environment Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    openai_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Running the Backend

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Testing

```python
# Use pytest with async support
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/tasks",
        json={"title": "Test task", "description": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test task"
```

---

## Common Issues

### Database Connection
```python
# Check .env has correct DATABASE_URL
DATABASE_URL=postgresql://user:pass@host/dbname
```

### OpenAI API
```python
# Check .env has valid OPENAI_API_KEY
OPENAI_API_KEY=sk-...
```

### JWT Issues
```python
# Ensure JWT_SECRET is set and consistent
JWT_SECRET=your-secret-key-here
```

---

## Critical Rules

1. **Type hints on all functions** - No exceptions
2. **Filter by user_id** - Always, on every query
3. **Async/await for routes** - Use async def
4. **Validate inputs** - Before database operations
5. **Error handling** - Use HTTPException with proper status codes
6. **Stateless server** - No session storage, state in DB
7. **MCP tools are stateless** - They query/modify DB directly

---

## Next Steps (Phase IV)

- Containerize with Docker
- Create Dockerfile
- Add health check endpoints
- Prepare for Kubernetes deployment

---

**Version**: 1.0.0  
**Phase**: III - AI Chatbot  
**Last Updated**: January 3, 2026
