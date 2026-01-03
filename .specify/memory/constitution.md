# Todo Full-Stack Web App - Project Constitution

> **Version**: 2.0.0  
> **Phase**: II - Full-Stack Web Application  
> **Created**: January 3, 2026  
> **Based on**: Phase I Console App (todo-console)

## Purpose

This document establishes the non-negotiable principles, constraints, and standards for the Todo Full-Stack Web Application. This phase evolves the console app into a production-ready, multi-user web application with authentication and persistent storage.

---

## Core Principles

### 1. Code Quality Standards

#### Backend (Python)
- **Type Hints**: All functions MUST have complete type annotations
- **Docstrings**: All public functions MUST have docstrings
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Line Length**: Maximum 88 characters (Black formatter default)
- **Async**: Use async/await for all database operations

#### Frontend (TypeScript)
- **Type Safety**: Full TypeScript strict mode enabled
- **Component Structure**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for functions
- **Formatting**: Prettier with 2-space indentation
- **Import Order**: React imports first, then libs, then local

### 2. Architecture Principles

#### Stateless Services
- Backend API must be stateless (no session storage)
- All state must be in PostgreSQL database
- JWT tokens contain all authentication info
- Services can scale horizontally

#### User Data Isolation
- **CRITICAL**: All queries MUST filter by authenticated user_id
- No user can access another user's data
- Database enforces foreign key relationships
- Middleware validates JWT and extracts user_id

#### RESTful API Design
- Resource-oriented URLs: `/api/{user_id}/tasks`
- Standard HTTP methods: GET, POST, PUT, DELETE, PATCH
- JSON request/response bodies
- Proper HTTP status codes

#### Separation of Concerns
```
Backend:
├── main.py           # FastAPI app initialization
├── config.py         # Environment configuration
├── database.py       # Database connection
├── models.py         # SQLModel ORM models
├── schemas.py        # Pydantic request/response schemas
├── middleware/
│   └── auth.py       # JWT verification middleware
└── routes/
    ├── auth.py       # Authentication endpoints
    └── tasks.py      # Task CRUD endpoints

Frontend:
├── app/
│   ├── (auth)/
│   │   ├── login/    # Login page
│   │   └── signup/   # Signup page
│   ├── dashboard/    # Main task interface
│   └── layout.tsx    # Root layout with auth provider
├── components/
│   ├── TaskList.tsx  # Task list container
│   ├── TaskForm.tsx  # Task creation form
│   └── TaskItem.tsx  # Individual task component
└── lib/
    ├── api.ts        # API client with JWT handling
    └── auth.ts       # Better Auth configuration
```

---

## Technology Stack

### Backend
- **Runtime**: Python 3.13+
- **Framework**: FastAPI 0.128.0+
- **ORM**: SQLModel 0.0.31+ (Pydantic + SQLAlchemy)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **Password Hashing**: bcrypt via passlib
- **JWT Library**: python-jose

### Frontend
- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript 5.7+
- **Styling**: Tailwind CSS 3.4+
- **Authentication**: Better Auth client
- **HTTP Client**: Fetch API with custom wrapper

### Development
- **Package Manager**: 
  - Backend: pip with requirements.txt
  - Frontend: npm
- **Containers**: Docker & Docker Compose
- **Version Control**: Git with conventional commits

### Infrastructure
- **Database**: Neon (PostgreSQL-compatible, serverless)
- **Deployment**: 
  - Frontend: Vercel (Next.js native)
  - Backend: Railway/Render/Fly.io
- **Environment**: Development, Production

---

## Database Schema

### Users Table (Better Auth managed)
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,           -- Better Auth generated ID
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    password_hash VARCHAR,            -- Better Auth handles hashing
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_completed (completed),
    INDEX idx_user_completed (user_id, completed)
);
```

**Key Constraints**:
- All tasks MUST have user_id (foreign key)
- Cascade delete: Delete user → Delete all their tasks
- Indexes on user_id for query performance

---

## API Endpoints

### Authentication Routes (`/api/auth`)

#### POST `/api/auth/signup`
**Purpose**: Create new user account  
**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```
**Response** (201):
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "token": "eyJhbGc..."
}
```

#### POST `/api/auth/login`
**Purpose**: Authenticate existing user  
**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```
**Response** (200):
```json
{
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGc..."
}
```

### Task Routes (`/api/{user_id}/tasks`)
**All routes require**: `Authorization: Bearer <JWT>`

#### GET `/api/{user_id}/tasks`
**Purpose**: List all tasks for authenticated user  
**Response** (200):
```json
[
  {
    "id": 1,
    "user_id": "usr_abc123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-03T10:00:00Z",
    "updated_at": "2026-01-03T10:00:00Z"
  }
]
```

#### POST `/api/{user_id}/tasks`
**Purpose**: Create new task  
**Request**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```
**Response** (201):
```json
{
  "id": 1,
  "user_id": "usr_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-03T10:00:00Z",
  "updated_at": "2026-01-03T10:00:00Z"
}
```

#### PUT `/api/{user_id}/tasks/{id}`
**Purpose**: Update task title/description  
**Request**:
```json
{
  "title": "Buy groceries and gas",
  "description": "Updated description"
}
```
**Response** (200): Updated task object

#### DELETE `/api/{user_id}/tasks/{id}`
**Purpose**: Delete task  
**Response** (204): No content

#### PATCH `/api/{user_id}/tasks/{id}/complete`
**Purpose**: Toggle task completion status  
**Response** (200): Updated task object

---

## Authentication Flow

### 1. User Registration
```
User fills signup form
→ Frontend sends POST /api/auth/signup
→ Backend creates user via Better Auth
→ Backend issues JWT token
→ Frontend stores token in localStorage/cookie
→ Frontend redirects to dashboard
```

### 2. User Login
```
User fills login form
→ Frontend sends POST /api/auth/login
→ Backend validates credentials via Better Auth
→ Backend issues JWT token
→ Frontend stores token
→ Frontend redirects to dashboard
```

### 3. API Requests
```
Frontend makes API call
→ Includes: Authorization: Bearer <JWT>
→ Backend middleware extracts JWT
→ Backend verifies signature and expiration
→ Backend extracts user_id from payload
→ Backend filters queries by user_id
→ Backend returns user-specific data
```

### 4. Token Expiration
```
Token expires after 7 days
→ API returns 401 Unauthorized
→ Frontend detects 401
→ Frontend redirects to login
→ User logs in again
```

---

## Security Requirements

### 1. Password Security
- Minimum 8 characters
- Better Auth handles hashing (bcrypt)
- Never log or expose passwords
- Use HTTPS in production

### 2. JWT Security
- Sign with BETTER_AUTH_SECRET
- Include expiration (`exp` claim)
- Include user_id in payload
- Verify signature on every request
- Use HS256 algorithm

### 3. User Data Isolation
```python
# CRITICAL: Always filter by authenticated user
@app.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Filter by user_id
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return tasks
```

### 4. Input Validation
- Validate all inputs server-side
- Title: 1-200 characters, required
- Description: max 1000 characters, optional
- Sanitize HTML if rendering user input

### 5. CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful GET/PUT/PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing/invalid JWT
- **403 Forbidden**: Valid JWT but wrong user
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Unexpected errors

### Error Response Format
```json
{
  "detail": "Task not found"
}
```

### Frontend Error Handling
```typescript
try {
  const response = await fetch(url, options);
  if (response.status === 401) {
    // Redirect to login
    router.push('/login');
    return;
  }
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  return await response.json();
} catch (error) {
  // Show user-friendly error message
  toast.error(error.message);
}
```

---

## Testing Requirements

### Backend Tests
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test API endpoints
- **Coverage**: Minimum 80%
- **Framework**: pytest + httpx
- **Database**: Use in-memory SQLite for tests

### Frontend Tests
- **Component Tests**: Test React components
- **Integration Tests**: Test user flows
- **Framework**: Jest + React Testing Library
- **Mocking**: Mock API calls

---

## Environment Configuration

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:8000
ENVIRONMENT=development
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
```

**CRITICAL**: 
- Same BETTER_AUTH_SECRET for frontend and backend
- Never commit .env files to Git
- Use different secrets for dev and production

---

## Migration from Phase I

### What Stays the Same
- Task model structure (id, title, description, completed, timestamps)
- CRUD operation logic (add, list, update, delete, complete)
- Validation rules (title length, description length)

### What Changes
```python
# Phase I (Console)
class TodoApp:
    def __init__(self):
        self.tasks: list[Task] = []
    
    def add_task(self, title: str, description: str | None) -> Task:
        task = Task(id=len(self.tasks) + 1, title=title, ...)
        self.tasks.append(task)
        return task

# Phase II (Web)
class TaskOperations:
    def add_task(
        self,
        user_id: str,
        title: str,
        description: str | None,
        session: Session
    ) -> Task:
        task = Task(user_id=user_id, title=title, ...)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

**Key Differences**:
1. Add `user_id` parameter to all operations
2. Use SQLModel Session instead of in-memory list
3. Add database commit/refresh operations
4. Add JWT authentication checks

---

## Deployment Strategy

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production
```bash
# Backend (Railway/Render)
- Connect to GitHub repo
- Set environment variables
- Deploy main branch

# Frontend (Vercel)
- Connect to GitHub repo
- Set environment variables
- Deploy main branch
- Auto-deploys on push
```

---

## Non-Negotiables

1. **No Manual Coding**: All code generated via Spec-Driven Development
2. **Security First**: Always validate JWT and filter by user_id
3. **Stateless Backend**: No session storage, JWT contains all auth info
4. **Database as Truth**: All state must be in PostgreSQL
5. **Type Safety**: Full type hints (Python) and TypeScript strict mode
6. **Test Before Deploy**: All tests must pass
7. **User Isolation**: Zero tolerance for data leaks between users

---

## Success Criteria

### Functional
- ✅ User can sign up with email/password
- ✅ User can log in and receive JWT token
- ✅ User can add tasks with title and description
- ✅ User can view their tasks (only their own)
- ✅ User can update task title/description
- ✅ User can mark tasks as complete/incomplete
- ✅ User can delete tasks
- ✅ All data persists to PostgreSQL
- ✅ Frontend deployed to Vercel
- ✅ Backend deployed to Railway/Render

### Technical
- ✅ API is stateless and horizontally scalable
- ✅ All endpoints require JWT authentication
- ✅ All queries filter by authenticated user_id
- ✅ Passwords are hashed with bcrypt
- ✅ JWT tokens expire after 7 days
- ✅ CORS configured correctly
- ✅ Error messages are user-friendly
- ✅ Tests have >80% coverage

### Process
- ✅ Constitution file exists and is followed
- ✅ Spec file documents all requirements
- ✅ Plan file details architecture
- ✅ Tasks file breaks down implementation
- ✅ Code generated via /sp.implement
- ✅ Git history shows spec-driven commits

---

**This constitution is immutable for Phase II. Any deviations must be documented in ADR (Architecture Decision Records).**
