# Claude Code Instructions

> **Read this first**: This file provides context for Claude Code to work effectively with this Spec-Driven Development project.

---

## Quick Start

This project follows **Spec-Driven Development (SDD)**. Before making any changes:

1. **Read the agent instructions**: @AGENTS.md
2. **Understand the principles**: @.specify/memory/constitution.md
3. **Check current phase specs**: @specs/003-chatbot/

---

## Project Overview

**Project**: Todo Full-Stack Web Application with AI Chatbot  
**Current Phase**: Phase III - AI Chatbot  
**Methodology**: Spec-Driven Development (SDD)

### Completed Phases
- ✅ Phase I: Console App (Python)
- ✅ Phase II: Web Application (Next.js + FastAPI)
- ✅ Phase III: AI Chatbot (OpenAI + MCP)

### Architecture
```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ Database (PostgreSQL)
                           ↓
                    OpenAI Agents SDK
                           ↓
                      MCP Tools
```

---

## How to Work with This Project

### 1. Understanding the Structure

```
todo-fullstack/
├── AGENTS.md              # Read this for SDD workflow
├── CLAUDE.md              # This file
├── .specify/              # Project constitution
├── specs/                 # All specifications
│   ├── 002-web-app/      # Phase II specs
│   └── 003-chatbot/      # Phase III specs (current)
├── backend/               # FastAPI + AI Agent + MCP
├── frontend/              # Next.js + ChatKit
└── docker-compose.yml
```

### 2. Before Making Changes

**Always check:**
1. Is this feature in the spec? → @specs/003-chatbot/spec.md
2. Is the architecture planned? → @specs/003-chatbot/plan.md
3. Is there a task for this? → @specs/003-chatbot/tasks.md
4. Does it follow principles? → @.specify/memory/constitution.md

**If something is missing**: Ask the developer to update the spec first.

### 3. Referencing Files

Use these references in your responses:
- Constitution: @.specify/memory/constitution.md
- Phase II Spec: @specs/002-web-app/spec.md
- Phase III Spec: @specs/003-chatbot/spec.md
- Backend Code: @backend/app/
- Frontend Code: @frontend/src/

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **AI**: OpenAI Agents SDK (gpt-4o-mini)
- **Tools**: Custom MCP Tools (Official MCP SDK)
- **Auth**: JWT with bcrypt

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Chat UI**: OpenAI ChatKit (not implemented yet)
- **Auth**: JWT tokens from backend

---

## Common Tasks

### Adding a New Feature

```markdown
1. Ask developer: "Is this feature specified?"
2. If not: "Please create/update specs/003-chatbot/spec.md"
3. Review: @specs/003-chatbot/plan.md for architecture
4. Check: @specs/003-chatbot/tasks.md for breakdown
5. Implement following the plan
6. Reference task IDs in commit messages
```

### Modifying Existing Code

```markdown
1. Read the relevant spec section
2. Check if change affects architecture
3. If yes: Request plan update
4. Implement following existing patterns
5. Update tests
```

### Debugging Issues

```markdown
1. Check: @backend/app/ for backend issues
2. Check: @frontend/src/ for frontend issues
3. Review: Database models in @backend/app/models.py
4. Check: API schemas in @backend/app/schemas.py
5. Verify: JWT auth in @backend/app/auth.py
```

---

## Code Standards

### Backend (Python)
```python
# All functions must have type hints
def create_task(title: str, user_id: str) -> Task:
    """Create a new task for a user."""
    pass

# Use async/await for database operations
async def get_tasks(user_id: str, session: Session) -> list[Task]:
    """Get all tasks for a user."""
    pass

# User data isolation is CRITICAL
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)  # Always filter by user_id
).all()
```

### Frontend (TypeScript)
```typescript
// Use functional components with hooks
export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  
  // Type all variables
  const handleComplete = (taskId: number): void => {
    // ...
  };
}

// Use the API client
import { api } from '@/lib/api';
const tasks = await api.getTasks();
```

---

## Critical Rules

### Security
1. **ALWAYS filter queries by `user_id`** - No exceptions
2. **Validate JWT tokens** on all protected endpoints
3. **Hash passwords** with bcrypt (never store plain text)
4. **Sanitize inputs** before database operations

### Architecture
1. **Backend is stateless** - No session storage
2. **Database is source of truth** - All state persists there
3. **MCP tools are stateless** - They query/modify DB directly
4. **Agent conversations persist** - Store in database

### Development
1. **No code without spec** - If spec is missing, ask for it
2. **Follow the plan** - Don't invent architecture
3. **Type everything** - Python type hints + TypeScript strict mode
4. **Test changes** - Verify functionality works

---

## Running the Application

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

### Both (Docker)
```bash
docker-compose up
```

---

## Phase-Specific Context

### Phase II (Web App) - Completed
- ✅ Authentication with JWT
- ✅ User signup/login
- ✅ Task CRUD operations
- ✅ Responsive UI
- ✅ User data isolation

### Phase III (AI Chatbot) - Current
- ✅ OpenAI Agents SDK integration
- ✅ MCP Server with 5 tools
- ✅ Stateless chat endpoint
- ✅ Conversation persistence
- ⚠️ ChatKit UI (custom implementation, not official OpenAI ChatKit)

### Known Issues
- Better Auth not used (custom JWT implementation instead)
- API endpoints use `/api/tasks` instead of `/api/{user_id}/tasks`
- OpenAI ChatKit UI not implemented (custom chat interface used)

---

## File Organization

### Backend
```
backend/app/
├── main.py              # FastAPI app, routers
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT authentication
├── config.py            # Environment configuration
├── database.py          # Database connection
├── agents/
│   └── todo_agent.py    # OpenAI Agents SDK integration
├── mcp_server/
│   └── tools.py         # MCP tools for task operations
└── routes/
    ├── auth.py          # Auth endpoints
    ├── tasks.py         # Task endpoints
    └── chat.py          # Chat endpoint (Phase III)
```

### Frontend
```
frontend/src/
├── app/
│   ├── layout.tsx       # Root layout with auth
│   ├── page.tsx         # Landing/home page
│   ├── login/           # Login page
│   ├── signup/          # Signup page
│   ├── dashboard/       # Task management UI
│   └── chat/            # Chat interface (Phase III)
├── components/
│   ├── TaskList.tsx     # Task list display
│   ├── TaskForm.tsx     # Task creation form
│   └── TaskItem.tsx     # Individual task component
└── lib/
    ├── api.ts           # API client with JWT
    └── auth-context.tsx # Auth context provider
```

---

## Git Workflow

### Commit Message Format
```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scopes: backend, frontend, specs, mcp, agent, auth, ui

Examples:
feat(mcp): Add update_task tool
fix(auth): Correct JWT expiration handling
docs(specs): Update Phase III specification
```

### SDD Workflow Commits
```
1. docs: Add specification (WHAT)
2. docs: Generate technical plan (HOW)
3. docs: Break into tasks (BREAKDOWN)
4. feat: Implement feature (CODE)
```

---

## Troubleshooting

### Backend Issues
- Check database connection: `backend/.env` has correct `DATABASE_URL`
- Check migrations: Run database setup scripts
- Check imports: All imports use absolute paths from `app.`

### Frontend Issues
- Check API URL: `NEXT_PUBLIC_API_URL` in `.env.local`
- Check auth: JWT token in localStorage
- Check types: Run `npm run build` to catch TypeScript errors

### AI Agent Issues
- Check OpenAI key: `OPENAI_API_KEY` in `backend/.env`
- Check MCP tools: Import in `agents/todo_agent.py`
- Check database access: MCP tools need database session

---

## Next Steps (Phase IV - Kubernetes)

When starting Phase IV:
1. Create `specs/004-kubernetes/` directory
2. Write spec for containerization and deployment
3. Plan architecture for Minikube/K8s
4. Use Docker AI (Gordon) for container assistance
5. Use kubectl-ai and kagent for K8s operations

---

## Questions?

If you need clarification:
1. Check @AGENTS.md for workflow
2. Check @.specify/memory/constitution.md for principles
3. Check @specs/003-chatbot/ for current phase details
4. Ask the developer to update specs if needed

---

**Remember**: This is a Spec-Driven project. Always reference specifications before implementing changes. When in doubt, ask for the spec to be updated first.

---

**Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Current Phase**: III - AI Chatbot
