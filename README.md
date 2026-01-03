# Todo Full-Stack Web Application with AI Chatbot

> **Hackathon II: Evolution of Todo**  
> **Phase**: II & III - Web Application + AI Chatbot  
> **Built with**: Spec-Driven Development (SDD) methodology

A production-ready, multi-user web application with AI-powered conversational task management, built entirely through **Spec-Driven Development**.

## Phases Completed

- Phase I: Console App (Python)
- Phase II: Web Application (Next.js + FastAPI)
- Phase III: AI Chatbot (OpenAI + MCP)

## Phase III: AI Chatbot Features

### Natural Language Task Management
- Conversational interface for all task operations
- Understand natural language commands
- Context-aware multi-turn conversations
- Persistent conversation history

### MCP Tools (5 Task Operations)
- **add_task**: Create new tasks via chat
- **list_tasks**: View tasks with natural filters
- **complete_task**: Toggle completion status
- **delete_task**: Remove tasks by ID or description
- **update_task**: Modify task details

### Security & Architecture
- Stateless server design (horizontally scalable)
- JWT authentication for all endpoints
- User data isolation per conversation
- Conversation state persists in database

### Example Commands
```
"Add a task to buy groceries"
"Show me all my tasks"
"What's pending?"
"Mark task 3 as complete"
"Delete the meeting task"
"Update task 1 to 'Call mom tonight'"
```

---

## Spec-Driven Development Process

This project was built using the **Spec-Driven Development (SDD)** methodology:

```
Phase III Process:
1. Specification (specs/003-chatbot/spec.md) - Requirements & user stories
2. Technical Plan (specs/003-chatbot/plan.md) - Architecture & components
3. Task Breakdown (specs/003-chatbot/tasks.md) - Implementation tasks
4. Implementation - Code following the plan
```

## Project Structure

```
todo-fullstack/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # JWT authentication
│   │   ├── agents/          # AI Agent
│   │   │   └── todo_agent.py
│   │   ├── mcp_server/      # MCP Tools
│   │   │   └── tools.py
│   │   └── routes/
│   │       ├── auth.py      # Auth endpoints
│   │       ├── tasks.py     # Task CRUD
│   │       └── chat.py      # Chat endpoint
│   └── requirements.txt
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # Pages
│   │   ├── components/      # React components
│   │   └── lib/             # API client & auth
│   └── package.json
├── specs/
│   ├── 002-web-app/         # Phase II specs
│   └── 003-chatbot/         # Phase III specs
├── AGENTS.md                # AI agent instructions
├── CLAUDE.md                # Claude Code guide
└── .specify/
    └── memory/
        └── constitution.md   # Project principles
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS | Modern React framework with SSR |
| **Backend** | FastAPI, Python 3.13+ | High-performance async API |
| **AI Agent** | OpenAI API (gpt-4o-mini) | Natural language understanding |
| **Tools** | Custom MCP Tools | Task operation functions |
| **Database** | PostgreSQL (Neon Serverless) | Persistent storage |
| **ORM** | SQLModel | Type-safe database operations |
| **Auth** | JWT | Secure token-based authentication |

---

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL database (or Neon account)
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run the development server
npm run dev
```

The frontend will be available at http://localhost:3000

### Using Docker Compose

```bash
# Run both frontend and backend
docker-compose up

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create new account |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Tasks (Requires JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks for user |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/{id}` | Get task details |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |

### Chat (Phase III)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to AI assistant |

---

## Features

### Phase II - Web Application

#### Core Features
- User registration and authentication
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Persistent storage in PostgreSQL
- Multi-user support with data isolation

#### Technical Features
- RESTful API with FastAPI
- SQLModel ORM for database operations
- JWT-based authentication
- Password hashing with bcrypt
- Responsive UI with Tailwind CSS
- TypeScript for type safety

### Phase III - AI Chatbot

#### AI Features
- Natural language task management
- Multi-turn conversation support
- Context-aware responses
- Conversation history persistence

#### MCP Tools
1. **add_task** - Create tasks via natural language
2. **list_tasks** - Query tasks with filters
3. **complete_task** - Mark tasks complete
4. **delete_task** - Remove tasks
5. **update_task** - Modify task details

#### Architecture
- Stateless server design (horizontally scalable)
- OpenAI Agents SDK integration
- Custom MCP tools for task operations
- Database-persisted conversation state

---

## Development Workflow

### 1. Spec-Driven Development

All features follow the SDD process:

1. **Specify** - Define requirements in `specs/*/spec.md`
2. **Plan** - Design architecture in `specs/*/plan.md`
3. **Tasks** - Break down work in `specs/*/tasks.md`
4. **Implement** - Write code following the plan

### 2. Git Workflow

```bash
# Always reference specs in commits
git commit -m "feat: Implement chat endpoint per specs/003-chatbot/plan.md"
```

### 3. Testing

```bash
# Backend tests
cd backend
pytest --cov=app

# Frontend tests
cd frontend
npm test
```

---

## Database Schema

### Users Table
- `id` (primary key)
- `email` (unique)
- `password_hash`
- `name`
- `created_at`

### Tasks Table
- `id` (primary key)
- `user_id` (foreign key)
- `title`
- `description`
- `completed`
- `created_at`
- `updated_at`

### Conversations Table (Phase III)
- `id` (primary key)
- `user_id` (foreign key)
- `created_at`
- `updated_at`

### Messages Table (Phase III)
- `id` (primary key)
- `conversation_id` (foreign key)
- `user_id` (foreign key)
- `role` (user/assistant)
- `content`
- `created_at`

---

## Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

### Backend (Railway/Render)

1. Create account on Railway or Render
2. Connect GitHub repository
3. Set environment variables:
   - `DATABASE_URL`
   - `JWT_SECRET`
   - `OPENAI_API_KEY`
4. Deploy

### Database (Neon)

1. Create account at neon.tech
2. Create new project
3. Copy connection string
4. Add to backend `.env` as `DATABASE_URL`

---

## Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgresql://user:password@host/database
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
OPENAI_API_KEY=sk-...
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend Issues

**Database connection fails**
```bash
# Check DATABASE_URL in .env
# Ensure PostgreSQL is running
# Test connection: psql $DATABASE_URL
```

**OpenAI API errors**
```bash
# Verify OPENAI_API_KEY in .env
# Check API key at platform.openai.com
```

### Frontend Issues

**API calls fail**
```bash
# Check NEXT_PUBLIC_API_URL in .env.local
# Ensure backend is running on correct port
# Check browser console for CORS errors
```

**Build errors**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

---

## Contributing

This project follows Spec-Driven Development:

1. Create specification in `specs/`
2. Get spec approved
3. Implement following the spec
4. Reference spec in commit messages

---

## Documentation

- **AGENTS.md** - AI agent collaboration guidelines
- **CLAUDE.md** - Claude Code instructions
- **SDD-SUMMARY.md** - SDD process summary
- **specs/** - All feature specifications
- **.specify/memory/constitution.md** - Project principles

---

## License

MIT License - Part of PIAIC AI-201 Hackathon II

---

## Project Status

- Phase I: Complete
- Phase II: Complete
- Phase III: Complete
- Phase IV (Kubernetes): Coming soon
- Phase V (Cloud Deployment): Coming soon

---

**Built with Spec-Driven Development**  
**Hackathon II: Evolution of Todo**  
**January 2026**
