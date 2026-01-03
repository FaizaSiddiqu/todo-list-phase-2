# Phase III: AI-Powered Todo Chatbot - Technical Plan

**Version**: 1.0  
**Date**: January 3, 2026  
**Based on**: specs/003-chatbot/spec.md  
**Status**: Active

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Dashboard    │  │ Task List    │  │  Chat Interface      │  │
│  │ (REST API)   │  │ (REST API)   │  │  (ChatKit + MCP)     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                  │                      │              │
│         └──────────────────┼──────────────────────┘              │
│                            │ JWT Token                           │
└────────────────────────────┼─────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              REST API (Phase II)                          │  │
│  │              Still works unchanged                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              NEW: Chat Endpoint                           │  │
│  │              POST /api/{user_id}/chat                     │  │
│  │              ┌─────────────────────────────────────┐      │  │
│  │              │  1. Validate JWT & user_id          │      │  │
│  │              │  2. Create/retrieve conversation    │      │  │
│  │              │  3. Store user message              │      │  │
│  │              │  4. Load conversation history       │      │  │
│  │              │  5. Build message array             │      │  │
│  │              │  6. Run OpenAI Agent with tools     │      │  │
│  │              │  7. Store assistant response        │      │  │
│  │              │  8. Return response + tool calls    │      │  │
│  │              └─────────────────────────────────────┘      │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              OpenAI Agents SDK Integration                │  │
│  │              Agent: TodoAssistant                         │  │
│  │              Model: gpt-4o-mini                           │  │
│  │              Tools: [5 MCP tools]                         │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MCP Server (5 Tools)                         │  │
│  │              ┌────────────────────────────────┐           │  │
│  │              │ 1. add_task                    │           │  │
│  │              │ 2. list_tasks                  │           │  │
│  │              │ 3. complete_task               │           │  │
│  │              │ 4. delete_task                 │           │  │
│  │              │ 5. update_task                 │           │  │
│  │              └────────────────────────────────┘           │  │
│  │              Each tool validates user_id and              │  │
│  │              performs database operations                 │  │
│  └────────────────────────┬─────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            ↓
                  ┌──────────────────┐
                  │   Neon Database  │
                  │   (PostgreSQL)   │
                  │  ┌────────────┐  │
                  │  │ users      │  │
                  │  │ tasks      │  │
                  │  │ conversation│  │ ← NEW
                  │  │ message    │  │ ← NEW
                  │  └────────────┘  │
                  └──────────────────┘
```

### 1.2 Key Architectural Decisions

**Decision 1: Stateless Server**
- **Rationale**: Enables horizontal scaling, resilience, and cloud-native deployment
- **Implementation**: All conversation state persists to database
- **Trade-offs**: Slightly higher database load, but gains in scalability

**Decision 2: MCP Tools Wrap Existing Logic**
- **Rationale**: Reuse Phase II business logic, maintain single source of truth
- **Implementation**: MCP tools call existing database operations
- **Trade-offs**: Additional abstraction layer, but ensures consistency

**Decision 3: Conversation History Limitation**
- **Rationale**: Control token usage and response latency
- **Implementation**: Load only last 10 messages per chat request
- **Trade-offs**: Loses very old context, but keeps API fast

**Decision 4: Single Chat Endpoint**
- **Rationale**: Simplify API surface, let agent route internally
- **Implementation**: One endpoint handles all conversational intents
- **Trade-offs**: More complex agent logic, but cleaner API

---

## 2. Component Design

### 2.1 Database Layer

#### New Tables Schema

```sql
-- Conversations table
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);

-- Messages table
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_user_id ON message(user_id);
CREATE INDEX idx_message_created_at ON message(created_at);
```

#### SQLModel Models

**File**: `backend/app/models.py` (extend existing)

```python
class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Message model for chat history."""
    
    __tablename__ = "message"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(...)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Database Operations**:
- Create conversation: `INSERT INTO conversation ...`
- Retrieve conversation: `SELECT * FROM conversation WHERE id = ? AND user_id = ?`
- Store message: `INSERT INTO message ...`
- Load history: `SELECT * FROM message WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 10`
- Update conversation timestamp: `UPDATE conversation SET updated_at = NOW() WHERE id = ?`

### 2.2 MCP Server Layer

**File**: `backend/app/mcp_server/__init__.py`

#### Tool Definitions

```python
from mcp.server import MCPServer
from mcp.types import Tool, ToolParameter

mcp_server = MCPServer("todo-mcp-server")

# Tool 1: Add Task
@mcp_server.tool(
    name="add_task",
    description="Create a new todo task",
    parameters=[
        ToolParameter(name="user_id", type="string", required=True),
        ToolParameter(name="title", type="string", required=True),
        ToolParameter(name="description", type="string", required=False),
    ]
)
async def add_task(user_id: str, title: str, description: str = None):
    """Add a new task for the user."""
    # Validate inputs
    if not title or len(title) > 200:
        return {"error": "Title is required and must be ≤200 characters"}
    
    # Create task in database
    task = Task(
        user_id=user_id,
        title=title,
        description=description
    )
    
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }

# Tool 2: List Tasks
@mcp_server.tool(
    name="list_tasks",
    description="Retrieve user's tasks",
    parameters=[
        ToolParameter(name="user_id", type="string", required=True),
        ToolParameter(name="status", type="string", required=False),
    ]
)
async def list_tasks(user_id: str, status: str = "all"):
    """List tasks for the user with optional status filter."""
    with Session(engine) as session:
        query = select(Task).where(Task.user_id == user_id)
        
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        
        tasks = session.exec(query).all()
    
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat()
        }
        for task in tasks
    ]

# Tool 3: Complete Task
@mcp_server.tool(
    name="complete_task",
    description="Mark a task as complete",
    parameters=[
        ToolParameter(name="user_id", type="string", required=True),
        ToolParameter(name="task_id", type="integer", required=True),
    ]
)
async def complete_task(user_id: str, task_id: int):
    """Toggle task completion status."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task:
            return {"error": "Task not found"}
        
        if task.user_id != user_id:
            return {"error": "Unauthorized access"}
        
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "completed" if task.completed else "pending",
        "title": task.title,
        "completed": task.completed
    }

# Tool 4: Delete Task
@mcp_server.tool(
    name="delete_task",
    description="Remove a task",
    parameters=[
        ToolParameter(name="user_id", type="string", required=True),
        ToolParameter(name="task_id", type="integer", required=True),
    ]
)
async def delete_task(user_id: str, task_id: int):
    """Delete a task."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task:
            return {"error": "Task not found"}
        
        if task.user_id != user_id:
            return {"error": "Unauthorized access"}
        
        title = task.title
        session.delete(task)
        session.commit()
    
    return {
        "task_id": task_id,
        "status": "deleted",
        "title": title
    }

# Tool 5: Update Task
@mcp_server.tool(
    name="update_task",
    description="Modify task title or description",
    parameters=[
        ToolParameter(name="user_id", type="string", required=True),
        ToolParameter(name="task_id", type="integer", required=True),
        ToolParameter(name="title", type="string", required=False),
        ToolParameter(name="description", type="string", required=False),
    ]
)
async def update_task(user_id: str, task_id: int, title: str = None, description: str = None):
    """Update task details."""
    if not title and not description:
        return {"error": "At least one field (title or description) must be provided"}
    
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task:
            return {"error": "Task not found"}
        
        if task.user_id != user_id:
            return {"error": "Unauthorized access"}
        
        if title:
            task.title = title
        if description is not None:  # Allow empty string
            task.description = description
        
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "updated",
        "title": task.title,
        "description": task.description
    }
```

**Key Design Principles**:
- Each tool validates user_id and task ownership
- Tools return consistent response format
- Error responses include helpful messages
- Database operations use context managers
- All timestamps use UTC

### 2.3 Agent Layer

**File**: `backend/app/agents/todo_agent.py`

```python
from openai import OpenAI
from openai.agents import Agent

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create TodoAssistant agent
todo_agent = Agent(
    name="TodoAssistant",
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    instructions="""
You are a helpful assistant that manages todo tasks for users.

You can help users:
- Add new tasks (use add_task tool)
- View their task list (use list_tasks tool)
- Mark tasks as complete (use complete_task tool)
- Delete tasks (use delete_task tool)
- Update task details (use update_task tool)

Guidelines:
1. Always confirm actions clearly with task ID and title
2. When tasks are created/updated/deleted, provide specific feedback
3. If users ask ambiguous questions, ask for clarification
4. Be friendly, concise, and action-oriented
5. Use natural language responses, not JSON
6. Format task lists in a readable way

Example responses:
- "✅ I've added 'Buy groceries' to your list (Task #5)"
- "You have 3 pending tasks: 1. Buy groceries, 2. Call mom, 3. Pay bills"
- "✅ Marked 'Call mom' as complete!"
- "❌ I couldn't find that task. Could you provide the task ID?"
""",
    tools=[
        # MCP tools will be registered here
        "add_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "update_task"
    ]
)

async def run_agent(user_id: str, messages: list) -> dict:
    """
    Run the TodoAssistant agent with conversation history.
    
    Args:
        user_id: User identifier for tool calls
        messages: List of message dicts with 'role' and 'content'
    
    Returns:
        dict with 'response' and 'tool_calls'
    """
    # Inject user_id into agent context
    # This will be passed to all tool calls automatically
    agent_context = {"user_id": user_id}
    
    # Run agent with conversation history
    result = await todo_agent.run(
        messages=messages,
        context=agent_context
    )
    
    return {
        "response": result.content,
        "tool_calls": result.tool_calls
    }
```

**Agent Behavior**:
- Analyzes user intent from natural language
- Selects appropriate tool(s) to use
- Handles multi-turn conversations
- Asks clarifying questions when needed
- Provides friendly confirmations

### 2.4 Chat Endpoint Layer

**File**: `backend/app/routes/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime

from ..database import get_session
from ..models import Conversation, Message
from ..auth import get_current_user
from ..agents.todo_agent import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request schema."""
    conversation_id: Optional[int] = None
    message: str


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
    4. Load conversation history
    5. Run AI agent
    6. Store assistant response
    7. Return response
    """
    
    # 1. Validate user owns this conversation
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversation"
        )
    
    # 2. Create or retrieve conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
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

**Endpoint Features**:
- JWT authentication required
- User data isolation enforced
- Stateless (all state in DB)
- Proper error handling
- Transaction management

### 2.5 Frontend Layer

**File**: `frontend/src/app/chat/page.tsx`

```typescript
"use client";

import { ChatKit } from "openai-chatkit";
import { useAuth } from "@/lib/auth-context";

export default function ChatPage() {
  const { user } = useAuth();

  if (!user) {
    return <div>Please log in to use the chatbot.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Todo Chatbot</h1>
      
      <ChatKit
        apiUrl={`/api/${user.id}/chat`}
        headers={{
          Authorization: `Bearer ${user.token}`,
        }}
        placeholder="Ask me to manage your tasks..."
        className="h-[600px]"
      />
    </div>
  );
}
```

**Frontend Features**:
- OpenAI ChatKit integration
- Automatic message history
- Real-time responses
- Secure API calls with JWT

---

## 3. Data Flow

### 3.1 Chat Request Flow

```
1. User types message in ChatKit UI
   ↓
2. Frontend sends POST /api/{user_id}/chat with message & conversation_id
   ↓
3. Backend validates JWT token
   ↓
4. Backend creates/retrieves Conversation record
   ↓
5. Backend stores user Message in database
   ↓
6. Backend loads last 10 messages from database
   ↓
7. Backend calls OpenAI Agent with message history
   ↓
8. Agent analyzes intent and selects MCP tool(s)
   ↓
9. MCP tool executes database operation
   ↓
10. Tool returns result to agent
   ↓
11. Agent generates natural language response
   ↓
12. Backend stores assistant Message in database
   ↓
13. Backend returns response to frontend
   ↓
14. ChatKit displays assistant response
```

### 3.2 MCP Tool Execution Flow

```
1. Agent decides to call tool (e.g., add_task)
   ↓
2. Agent provides parameters: {user_id, title, description}
   ↓
3. MCP tool validates inputs
   ↓
4. Tool creates database session
   ↓
5. Tool performs database operation (INSERT, SELECT, UPDATE, DELETE)
   ↓
6. Tool commits transaction
   ↓
7. Tool returns structured result
   ↓
8. Agent incorporates result into response
```

---

## 4. Technology Stack

### 4.1 Backend Dependencies

**New Dependencies** (add to `requirements.txt`):
```
openai>=1.0.0
openai-agents-sdk>=0.1.0
mcp>=1.0.0
httpx>=0.25.0
```

**Existing Dependencies** (already installed):
```
fastapi
sqlmodel
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

### 4.2 Frontend Dependencies

**New Dependencies** (add to `package.json`):
```json
{
  "dependencies": {
    "openai-chatkit": "^1.0.0"
  }
}
```

**Existing Dependencies** (already installed):
```
next
react
tailwindcss
```

### 4.3 Environment Variables

**Backend** (`backend/.env`):
```
# Existing
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...

# New
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**Frontend** (`frontend/.env.local`):
```
# Existing
NEXT_PUBLIC_API_URL=http://localhost:8000

# New
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
```

---

## 5. Security Considerations

### 5.1 Authentication & Authorization
- All chat endpoints require valid JWT token
- User can only access their own conversations
- MCP tools validate user_id on every call
- Task operations filtered by user_id

### 5.2 Input Validation
- Message content max length: 2000 characters
- Title max length: 200 characters
- Description max length: 1000 characters
- SQL injection prevention via SQLModel ORM
- XSS prevention via proper escaping

### 5.3 Rate Limiting
- 10 chat requests per minute per user
- Implement using FastAPI-Limiter
- Prevent OpenAI API abuse
- Protect database from overload

### 5.4 Error Handling
- No sensitive data in error messages
- Proper HTTP status codes
- Graceful degradation on OpenAI API failures
- Database transaction rollback on errors

---

## 6. Performance Optimization

### 6.1 Database
- Index on conversation.user_id
- Index on message.conversation_id
- Index on message.created_at
- Limit conversation history to 10 messages
- Connection pooling

### 6.2 API
- Async/await throughout
- Database query optimization
- Response compression
- Caching (future enhancement)

### 6.3 Agent
- Use gpt-4o-mini (faster, cheaper)
- Temperature 0.7 (balanced)
- Max tokens limit
- Timeout handling

---

## 7. Testing Strategy

### 7.1 Unit Tests
- MCP tools: Test each tool independently
- Database models: Test CRUD operations
- Agent: Test with mock tools
- Chat endpoint: Test with mock agent

### 7.2 Integration Tests
- End-to-end chat flow
- Conversation persistence
- Tool execution
- Error scenarios

### 7.3 Manual Testing
- Natural language understanding
- Multi-turn conversations
- Ambiguous requests
- Edge cases

---

## 8. Deployment Considerations

### 8.1 Phase II Compatibility
- Zero breaking changes to existing API
- Existing routes continue to work
- Database migrations are additive
- Frontend dashboard unchanged

### 8.2 Database Migration
- Create conversation and message tables
- Add indexes
- No data migration needed (new feature)
- Rollback plan: DROP tables

### 8.3 Environment Setup
- OpenAI API key required
- Domain allowlist configuration for ChatKit
- Environment variables validated on startup
- Health check endpoint updated

---

## 9. Success Metrics

### 9.1 Functional Metrics
- ✅ All 5 MCP tools working
- ✅ Chat endpoint response time < 5s
- ✅ Conversation persistence working
- ✅ Zero Phase II regression

### 9.2 Quality Metrics
- ✅ Test coverage > 80%
- ✅ Natural language accuracy > 90%
- ✅ Error rate < 5%
- ✅ Zero security vulnerabilities

### 9.3 Performance Metrics
- ✅ MCP tool execution < 500ms
- ✅ Database queries < 100ms
- ✅ Agent response < 3s
- ✅ Concurrent users: 50+

---

## 10. Risks & Mitigation

### Risk 1: OpenAI API Latency
- **Impact**: Slow chat responses
- **Mitigation**: Use gpt-4o-mini, set timeout, show loading state

### Risk 2: OpenAI API Cost
- **Impact**: High API bills
- **Mitigation**: Rate limiting, token limits, use mini model

### Risk 3: Natural Language Ambiguity
- **Impact**: Wrong tool selection
- **Mitigation**: Clear agent instructions, clarification prompts

### Risk 4: Database Load
- **Impact**: Slow queries
- **Mitigation**: Indexes, connection pooling, query optimization

### Risk 5: Security Vulnerabilities
- **Impact**: Unauthorized access
- **Mitigation**: JWT validation, user_id filtering, input validation

---

## 11. Future Enhancements (Out of Scope)

- Voice input/output
- Multi-language support
- Real-time collaboration
- Push notifications
- Advanced NLP features
- Custom agent training
- Analytics dashboard
- Conversation export

---

## 12. Implementation Phases

### Phase 1: Database & Models (1-2 hours)
- Add Conversation and Message models
- Create database migration
- Test models

### Phase 2: MCP Server (2-3 hours)
- Implement 5 tools
- Add validation and error handling
- Unit test each tool

### Phase 3: Agent Integration (1-2 hours)
- Set up OpenAI Agents SDK
- Create TodoAssistant agent
- Test with mock conversations

### Phase 4: Chat Endpoint (2-3 hours)
- Implement POST /api/{user_id}/chat
- Add authentication
- Test end-to-end flow

### Phase 5: Frontend (1-2 hours)
- Integrate ChatKit
- Create chat page
- Test UI

### Phase 6: Testing & Documentation (2-3 hours)
- Write tests
- Update README
- Create demo video

**Total Estimated Time**: 9-15 hours

---

## 13. File Structure Changes

```
todo-fullstack/
├── backend/
│   ├── app/
│   │   ├── models.py              # ✨ Add Conversation, Message
│   │   ├── main.py                # Update to include chat router
│   │   ├── agents/                # ✨ New
│   │   │   ├── __init__.py
│   │   │   └── todo_agent.py      # Agent configuration
│   │   ├── mcp_server/            # ✨ New
│   │   │   ├── __init__.py
│   │   │   └── tools.py           # 5 MCP tools
│   │   └── routes/
│   │       ├── auth.py            # Existing
│   │       ├── tasks.py           # Existing
│   │       └── chat.py            # ✨ New
│   └── requirements.txt           # Add new dependencies
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/         # Existing
│   │   │   ├── login/             # Existing
│   │   │   └── chat/              # ✨ New
│   │   │       └── page.tsx       # ChatKit integration
│   │   └── components/
│   │       ├── TaskList.tsx       # Existing
│   │       └── ChatInterface.tsx  # ✨ Optional wrapper
│   └── package.json               # Add openai-chatkit
└── specs/
    └── 003-chatbot/
        ├── spec.md                # ✅ Complete
        ├── plan.md                # ✅ Complete
        └── tasks.md               # Next step
```

---

## 14. Dependencies Between Components

```
Frontend (ChatKit)
    ↓ depends on
Chat Endpoint
    ↓ depends on
OpenAI Agent
    ↓ depends on
MCP Tools
    ↓ depends on
Database Models
    ↓ depends on
Database Schema
```

**Implementation Order**:
1. Database schema & models
2. MCP tools
3. Agent configuration
4. Chat endpoint
5. Frontend integration

---

## 15. Validation Checklist

Before considering Phase III complete:

- [ ] All 5 MCP tools implemented and tested
- [ ] Chat endpoint returns responses
- [ ] Conversation persists to database
- [ ] ChatKit UI displays conversations
- [ ] JWT authentication working
- [ ] User data isolation enforced
- [ ] Natural language commands work
- [ ] Error handling robust
- [ ] Phase II tests still pass
- [ ] Documentation updated
- [ ] Demo video created

---

**Plan Status**: ✅ Complete and Ready for Task Breakdown

**Next Steps**:
1. Break down into atomic tasks (tasks.md)
2. Implement using Claude Code
3. Test thoroughly
4. Deploy and demonstrate
