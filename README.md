# Todo Full-Stack Web Application with AI Chatbot

> **Hackathon II: Evolution of Todo**  
> **Phase**: III - AI-Powered Chatbot  
> **Built with**: Spec-Driven Development (SDD) methodology

A production-ready, multi-user web application with AI-powered conversational task management, built entirely through **Spec-Driven Development**.

## 📋 Phases Completed

- ✅ **Phase I**: Console App (Python)
- ✅ **Phase II**: Web Application (Next.js + FastAPI)
- ✅ **Phase III**: AI Chatbot (OpenAI + MCP) ← **NEW**

## ✨ Phase III: AI Chatbot Features

### 🤖 Natural Language Task Management
- Conversational interface for all task operations
- Understand natural language commands
- Context-aware multi-turn conversations
- Persistent conversation history

### 🛠️ MCP Tools (5 Task Operations)
- **add_task**: Create new tasks via chat
- **list_tasks**: View tasks with natural filters
- **complete_task**: Toggle completion status
- **delete_task**: Remove tasks by ID or description
- **update_task**: Modify task details

### 🔒 Security & Architecture
- Stateless server design (horizontally scalable)
- JWT authentication for all endpoints
- User data isolation per conversation
- Conversation state persists in database

### 💬 Example Commands
```
"Add a task to buy groceries"
"Show me all my tasks"
"What's pending?"
"Mark task 3 as complete"
"Delete the meeting task"
"Update task 1 to 'Call mom tonight'"
```

---

## 📋 Spec-Driven Development Process

This project was built using the **Spec-Driven Development (SDD)** methodology:

```
Phase III Process:
1. Specification (specs/003-chatbot/spec.md) - Requirements & user stories
   ↓
2. Technical Plan (specs/003-chatbot/plan.md) - Architecture & components
   ↓  
3. Task Breakdown (specs/003-chatbot/tasks.md) - Implementation tasks
   ↓
4. Implementation - Code following the plan
```

## Project Structure

```
todo-fullstack/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py
---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS | Modern React framework with SSR |
| **Backend** | FastAPI, Python 3.13+ | High-performance async API |
| **AI Agent** | OpenAI API (gpt-4o-mini) | Natural language understanding |
| **Tools** | Custom MCP Tools | Task operation functions |
| **Database** | PostgreSQL (Neon Serverless) | Persistent storage |
| **ORM** | SQLModel | Type-safe database operations |
| **Auth** | JWT | Secure token-based authentication |

## 📁 Project Structure

```
todo-fullstack/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app with Phase III router
│   │   ├── models.py        # SQLModel models (Task, User, Conversation, Message)
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # JWT authentication
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   ├── agents/          # ✨ NEW: AI Agent
│   │   │   └── todo_agent.py
│   │   ├── mcp_server/      # ✨ NEW: MCP Tools
│   │   │   └── tools.py
│   │   └── routes/
│   │       ├── auth.py      # Auth endpoints
│   │       ├── tasks.py     # Task CRUD endpoints
│   │       └── chat.py      # ✨ NEW: Chat endpoint
│   ├── migrations/          # ✨ NEW: Database migrations
│   │   └── 003_add_chat_tables.sql
│   └── requirements.txt
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/   # Task dashboard
│   │   │   ├── login/       # Login page
│   │   │   ├── signup/      # Signup page
│   │   │   └── chat/        # ✨ NEW: Chat interface
│   │   ├── components/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   └── TaskForm.tsx
│   │   └── lib/
│   │       ├── api.ts       # API client
│   │       └── auth-context.tsx
│   └── package.json
└── specs/                   # Spec-driven development files
    ├── 002-web-app/        # Phase II specs
    └── 003-chatbot/        # ✨ NEW: Phase III specs
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL database (Neon recommended)
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL (Neon PostgreSQL)
# - JWT_SECRET
# - OPENAI_API_KEY ← NEW for Phase III

# Run database migration (Phase III)
# The tables will be created automatically on first run

# Run the server
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000  
API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at http://localhost:3000

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Tasks (require authentication)
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create a task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Toggle completion

### Chat (Phase III - NEW)
- `POST /api/{user_id}/chat` - Send message, get AI response
- `GET /api/{user_id}/conversations` - List user's conversations
- `GET /api/{user_id}/conversations/{id}/messages` - Get conversation history

---

## 🔧 Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# JWT Authentication
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OpenAI API (Phase III)
OPENAI_API_KEY=sk-proj-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 💡 Using the AI Chatbot

### Access
1. Log in to the application
2. Click the **🤖 AI Chat** button in the dashboard
3. Start chatting!

### Example Conversations

**Adding a Task:**
```
You: Add a task to buy groceries
Bot: ✅ I've added 'Buy groceries' to your list (Task #5)
```

**Listing Tasks:**
```
You: Show me all my tasks
Bot: You have 3 pending tasks:
     1. Buy groceries (Task #5)
     2. Call mom (Task #3)
     3. Pay bills (Task #7)
```

**Completing a Task:**
```
You: Mark task 3 as complete
Bot: ✅ Marked 'Call mom' as complete!
```

**Updating a Task:**
```
You: Update task 5 to "Buy groceries and fruits"
Bot: ✅ I've updated Task #5 to 'Buy groceries and fruits'
```

**Deleting a Task:**
```
You: Delete task 7
Bot: ✅ I've deleted 'Pay bills' from your list.
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest

# Expected output:
# ====================== test session starts ======================
# collected X items
# tests/test_models.py::test_conversation_creation PASSED
# tests/test_mcp_tools.py::test_add_task PASSED
# ...
# ======================= X passed in Y.Ys =======================
```

### Manual Testing
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Create an account at http://localhost:3000/signup
4. Navigate to http://localhost:3000/chat
5. Test natural language commands

---

## 🔒 Features

## 🔒 Features Summary

### Phase I (Console App)
- ✅ Add, list, update, delete, complete tasks
- ✅ In-memory storage
- ✅ Python CLI interface

### Phase II (Web Application)
- ✅ User authentication (signup/login with JWT)
- ✅ Multi-user support with data isolation
- ✅ Persistent PostgreSQL storage (Neon)
- ✅ Responsive web interface
- ✅ RESTful API

### Phase III (AI Chatbot) ← Current
- ✅ Natural language task management
- ✅ 5 MCP tools for task operations
- ✅ Conversational interface
- ✅ Persistent conversation history
- ✅ Stateless architecture (horizontally scalable)
- ✅ Context-aware multi-turn conversations

---

## 📚 Documentation

- [Phase III Specification](specs/003-chatbot/spec.md) - Requirements and user stories
- [Phase III Plan](specs/003-chatbot/plan.md) - Architecture and design decisions
- [Phase III Tasks](specs/003-chatbot/tasks.md) - Implementation breakdown
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when server running)

---

## 🐛 Troubleshooting

### Backend Issues

**Database Connection Error:**
```bash
# Verify DATABASE_URL in .env
# Test connection:
psql $DATABASE_URL
```

**OpenAI API Error:**
```bash
# Verify OPENAI_API_KEY in .env
# Test with:
python -c "import os; from openai import OpenAI; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print(client.models.list())"
```

**Migration Issues:**
```bash
# Tables should be created automatically
# If not, check models are imported in app/models.py
# Verify database.py calls create_db_and_tables()
```

### Frontend Issues

**Chat Page Not Loading:**
```bash
# Check if user is logged in
# Verify token in localStorage
# Check browser console for errors
```

**API Connection Error:**
```bash
# Verify backend is running on port 8000
# Check CORS settings in backend/app/main.py
# Ensure API URL is correct in api.ts
```

---

## 🎯 Next Steps (Phase IV & V)

### Phase IV: Kubernetes Deployment
- Docker containerization
- Helm charts
- Minikube local deployment
- kubectl-ai for K8s operations

### Phase V: Cloud-Native
- Advanced features (recurring tasks, reminders, priorities)
- Event-driven architecture (Kafka)
- Dapr integration
- Cloud deployment (Oracle/Azure/GCP)

---

## 📝 License

MIT

---

## 🙏 Acknowledgments

- Built for **Hackathon II: Evolution of Todo**
- Methodology: **Spec-Driven Development (SDD)**
- AI Stack: OpenAI GPT-4o-mini
- Database: Neon Serverless PostgreSQL
- Framework: FastAPI + Next.js

---

**Ready for Phase IV: Kubernetes Deployment** 🚀
- ✅ Create, read, update, delete tasks
- ✅ Mark tasks as complete
- ✅ User-specific task isolation
- ✅ Responsive design
- ✅ Real-time form validation
#   t o d o - l i s t - p h a s e - 2  
 