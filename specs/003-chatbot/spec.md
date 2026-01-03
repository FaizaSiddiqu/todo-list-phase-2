# Phase III: AI-Powered Todo Chatbot - Specification

**Version**: 1.0  
**Date**: January 3, 2026  
**Phase**: III - AI Chatbot  
**Status**: Active

---

## 1. Overview

### 1.1 Purpose
Transform the existing Todo Full-Stack Web Application (Phase II) into an AI-powered chatbot system that allows users to manage their tasks through natural language conversations while maintaining all existing REST API functionality.

### 1.2 Scope
- Add conversational AI interface using OpenAI Agents SDK
- Implement MCP (Model Context Protocol) server with 5 task management tools
- Create stateless chat endpoint with conversation persistence
- Integrate OpenAI ChatKit for frontend chat interface
- Maintain backward compatibility with Phase II REST API

### 1.3 Key Principles
- **Stateless Architecture**: Server holds no conversation state; all state persists in database
- **Tool-Based Interaction**: AI agent uses MCP tools to perform task operations
- **Zero Breaking Changes**: Phase II functionality remains fully operational
- **Natural Language First**: Users can manage tasks conversationally

---

## 2. User Stories

### 2.1 Basic Level - Conversational Task Management

**US-001: Add Task via Chat**
- **As a** user
- **I want to** tell the chatbot to add a task using natural language
- **So that** I can quickly create tasks without using forms

**Acceptance Criteria:**
- User can say "Add a task to buy groceries"
- Agent creates task with title "Buy groceries"
- Agent confirms creation with task ID
- User can optionally include description in request

**US-002: List Tasks via Chat**
- **As a** user
- **I want to** ask the chatbot to show my tasks
- **So that** I can see what needs to be done

**Acceptance Criteria:**
- User can say "Show me all my tasks" or "What's pending?"
- Agent retrieves and displays tasks with appropriate filter
- Agent presents tasks in readable format
- User can request filtering by status (all/pending/completed)

**US-003: Complete Task via Chat**
- **As a** user
- **I want to** tell the chatbot to mark tasks complete
- **So that** I can update task status conversationally

**Acceptance Criteria:**
- User can say "Mark task 3 as complete"
- Agent toggles task completion status
- Agent confirms the action
- User can reference task by ID or title

**US-004: Delete Task via Chat**
- **As a** user
- **I want to** tell the chatbot to delete tasks
- **So that** I can remove tasks I no longer need

**Acceptance Criteria:**
- User can say "Delete task 2" or "Remove the meeting task"
- Agent confirms deletion intent if ambiguous
- Agent deletes task and confirms
- Agent handles task not found gracefully

**US-005: Update Task via Chat**
- **As a** user
- **I want to** tell the chatbot to modify task details
- **So that** I can update tasks without using forms

**Acceptance Criteria:**
- User can say "Change task 1 to 'Call mom tonight'"
- Agent updates task title or description
- Agent confirms the update
- User can update either field independently

### 2.2 Conversation Management

**US-006: Persistent Conversations**
- **As a** user
- **I want to** continue previous conversations
- **So that** the chatbot has context of our discussion

**Acceptance Criteria:**
- Each conversation has unique ID
- Conversation history persists to database
- Server restarts don't lose conversation state
- User can resume conversations across sessions

**US-007: Multi-Turn Interactions**
- **As a** user
- **I want to** have back-and-forth conversations
- **So that** I can clarify requests and get help

**Acceptance Criteria:**
- Agent remembers context within conversation
- Agent can ask clarifying questions
- Agent handles follow-up requests
- Agent maintains conversation flow

---

## 3. Functional Requirements

### 3.1 Database Models

#### 3.1.1 Conversation Model
```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Requirements:**
- Auto-incrementing primary key
- Foreign key to users table
- Timestamps for tracking
- Index on user_id for efficient queries

#### 3.1.2 Message Model
```python
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(...)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Requirements:**
- Links to conversation and user
- Role distinguishes user vs assistant messages
- Content stores message text
- Chronological ordering by created_at

### 3.2 MCP Server Tools

The MCP server must expose exactly 5 tools for the AI agent to use:

#### Tool 1: add_task
**Purpose**: Create a new task  
**Parameters**:
- `user_id` (string, required): User identifier
- `title` (string, required): Task title (1-200 chars)
- `description` (string, optional): Task description (max 1000 chars)

**Returns**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

**Error Handling**:
- Invalid user_id → 404 error
- Empty title → validation error
- Title too long → validation error

#### Tool 2: list_tasks
**Purpose**: Retrieve tasks from user's list  
**Parameters**:
- `user_id` (string, required): User identifier
- `status` (string, optional): Filter by "all", "pending", "completed" (default: "all")

**Returns**:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-03T10:00:00Z"
  }
]
```

**Error Handling**:
- Invalid user_id → 404 error
- Invalid status value → validation error

#### Tool 3: complete_task
**Purpose**: Toggle task completion status  
**Parameters**:
- `user_id` (string, required): User identifier
- `task_id` (integer, required): Task identifier

**Returns**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom",
  "completed": true
}
```

**Error Handling**:
- Task not found → 404 error
- Task belongs to different user → 403 error

#### Tool 4: delete_task
**Purpose**: Remove a task  
**Parameters**:
- `user_id` (string, required): User identifier
- `task_id` (integer, required): Task identifier

**Returns**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

**Error Handling**:
- Task not found → 404 error
- Task belongs to different user → 403 error

#### Tool 5: update_task
**Purpose**: Modify task title or description  
**Parameters**:
- `user_id` (string, required): User identifier
- `task_id` (integer, required): Task identifier
- `title` (string, optional): New title
- `description` (string, optional): New description

**Returns**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits",
  "description": "Updated description"
}
```

**Error Handling**:
- Task not found → 404 error
- No fields to update → validation error
- Task belongs to different user → 403 error

### 3.3 Chat Endpoint

#### Endpoint: POST /api/{user_id}/chat

**Request Body**:
```json
{
  "conversation_id": 123,  // optional, creates new if not provided
  "message": "Add a task to buy groceries"
}
```

**Response**:
```json
{
  "conversation_id": 123,
  "response": "✅ I've added the task 'Buy groceries' to your list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"user_id": "user123", "title": "Buy groceries"},
      "result": {"task_id": 5, "status": "created"}
    }
  ]
}
```

**Processing Flow**:
1. Validate user authentication via JWT
2. Create or retrieve conversation by ID
3. Store user message in database
4. Load conversation history (last 10 messages)
5. Build message array for OpenAI Agent
6. Run agent with MCP tools available
7. Store assistant response in database
8. Return response with tool call details

**Requirements**:
- Stateless server (no in-memory conversation state)
- All conversation state persists to database
- Support for conversation resume after server restart
- Proper error handling and user feedback

### 3.4 OpenAI Agent Configuration

**Agent Name**: TodoAssistant

**Instructions**:
```
You are a helpful assistant that manages todo tasks for users.
You can help users:
- Add new tasks
- View their task list
- Mark tasks as complete
- Delete tasks
- Update task details

Always confirm actions clearly. When tasks are created, updated, or deleted,
provide specific feedback including the task ID and title.

When users ask ambiguous questions, ask for clarification rather than guessing.
For example, if they say "delete the meeting" and there are multiple meetings,
ask which one they mean.

Be friendly, concise, and action-oriented.
```

**Available Tools**:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task

**Model**: gpt-4o or gpt-4o-mini (configurable)

**Temperature**: 0.7 (balanced creativity and consistency)

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Chat response time < 3 seconds (excluding OpenAI API latency)
- Database queries optimized with proper indexes
- Conversation history limited to last 10 messages per request
- MCP tool calls must complete in < 500ms each

### 4.2 Scalability
- Stateless server design allows horizontal scaling
- Database connection pooling
- No in-memory state (conversation, session, cache)
- Each request is independent and reproducible

### 4.3 Security
- All chat endpoints require JWT authentication
- User data isolation (filter by user_id)
- Input validation on all MCP tools
- Rate limiting on chat endpoint (10 requests/minute per user)
- SQL injection prevention via SQLModel ORM

### 4.4 Reliability
- Graceful error handling for OpenAI API failures
- Retry logic for transient failures
- Conversation state persists across server restarts
- Tool errors don't crash the agent

### 4.5 Usability
- Natural language understanding for common phrases
- Clear confirmation messages for all actions
- Helpful error messages
- Support for ambiguous requests with clarification

---

## 5. Integration Requirements

### 5.1 Frontend Integration
- OpenAI ChatKit component
- Domain allowlist configuration required
- Environment variable: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
- Chat interface accessible from dashboard
- Shows conversation history
- Real-time message updates

### 5.2 Backend Integration
- New route module: `routes/chat.py`
- MCP server module: `mcp_server/`
- OpenAI Agents SDK integration
- Database migrations for new tables
- Environment variables:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL` (default: gpt-4o-mini)

### 5.3 Database Integration
- Add Conversation and Message tables
- Foreign key constraints to User and Task tables
- Indexes on user_id and conversation_id
- Migration script for schema updates

---

## 6. Natural Language Command Examples

### 6.1 Task Creation
- "Add a task to buy groceries"
- "Create a new task: Call mom tonight"
- "I need to remember to pay bills"
- "Remind me to schedule dentist appointment"

### 6.2 Task Listing
- "Show me all my tasks"
- "What's on my todo list?"
- "List pending tasks"
- "What have I completed?"
- "Show me everything"

### 6.3 Task Completion
- "Mark task 3 as complete"
- "I finished buying groceries"
- "Complete the meeting task"
- "Mark all shopping tasks as done"

### 6.4 Task Deletion
- "Delete task 2"
- "Remove the meeting task"
- "Cancel the dentist appointment"
- "Get rid of old tasks"

### 6.5 Task Updates
- "Change task 1 to 'Call mom tonight'"
- "Update the grocery task to include fruits"
- "Rename task 5"
- "Edit the description of task 3"

### 6.6 Clarifications
- "Which meeting do you mean - the dentist or the team sync?"
- "I found 3 tasks with 'call' in the title. Which one?"
- "Could you provide the task ID or more details?"

---

## 7. Success Criteria

### 7.1 Functional Completeness
- ✅ All 5 MCP tools implemented and tested
- ✅ Chat endpoint returns responses in < 5 seconds
- ✅ Conversation history persists correctly
- ✅ Agent uses tools appropriately for requests
- ✅ ChatKit UI displays conversations

### 7.2 Quality Metrics
- ✅ Natural language understanding accuracy > 90%
- ✅ Zero breaking changes to Phase II API
- ✅ All Phase II tests still pass
- ✅ Chat endpoint test coverage > 80%
- ✅ MCP tools test coverage 100%

### 7.3 User Experience
- ✅ Clear, friendly responses
- ✅ Action confirmations include details
- ✅ Error messages are helpful
- ✅ Conversation context maintained
- ✅ UI is intuitive and responsive

---

## 8. Out of Scope

The following are explicitly NOT included in Phase III:

- ❌ Voice input/output
- ❌ Multi-language support (English only)
- ❌ Advanced NLP features (sentiment analysis, etc.)
- ❌ Real-time collaboration
- ❌ Push notifications
- ❌ Mobile app
- ❌ Advanced task features (recurring, tags, priorities)
- ❌ Event-driven architecture (Kafka/Dapr)
- ❌ Kubernetes deployment

These are reserved for Phases IV and V.

---

## 9. Dependencies

### 9.1 External Services
- OpenAI API (gpt-4o or gpt-4o-mini)
- Neon PostgreSQL (existing)
- Better Auth (existing)

### 9.2 Libraries
- `openai-agents-sdk` (Python)
- `mcp` (Official MCP SDK)
- `openai-chatkit` (React/Next.js)
- `httpx` (async HTTP client)
- `sqlmodel` (existing)

### 9.3 Environment Variables
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
```

---

## 10. Acceptance Testing

### 10.1 Test Scenarios

**Scenario 1: First Time User**
1. User logs in
2. User opens chat interface
3. User says "Add a task to buy milk"
4. System creates task and confirms
5. User says "Show my tasks"
6. System displays the newly created task

**Scenario 2: Conversation Continuation**
1. User has existing conversation
2. User resumes conversation
3. User sees previous messages
4. User sends new message
5. Agent maintains context

**Scenario 3: Server Restart**
1. User has active conversation
2. Server restarts
3. User sends new message
4. Conversation continues seamlessly
5. No state is lost

**Scenario 4: Error Handling**
1. User requests to delete non-existent task
2. Agent responds with helpful error message
3. User requests to update task with ambiguous reference
4. Agent asks for clarification
5. User provides clarification
6. Agent completes action

### 10.2 Tool Testing

Each MCP tool must pass:
- ✅ Valid input returns expected output
- ✅ Invalid user_id returns 404
- ✅ Unauthorized access returns 403
- ✅ Validation errors return clear messages
- ✅ Edge cases handled (empty strings, very long input, etc.)

---

## 11. References

- OpenAI Agents SDK Documentation
- Model Context Protocol (MCP) Specification
- OpenAI ChatKit Documentation
- Phase II Specification (002-web-app/spec.md)
- Hackathon Guide (HACKATHON_GUIDE.md)

---

**Specification Status**: ✅ Complete and Ready for Planning Phase

**Next Steps**:
1. Create architectural plan (plan.md)
2. Break down into tasks (tasks.md)
3. Implement using Claude Code
4. Test and validate
