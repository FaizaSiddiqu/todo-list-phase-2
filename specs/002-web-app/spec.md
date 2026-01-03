# Phase II: Full-Stack Web App Specification

## Overview
Transform the Phase I console todo app into a multi-user web application with authentication, persistent storage, and a responsive UI.

## Tech Stack
- **Frontend**: Next.js 15+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, SQLModel ORM
- **Database**: PostgreSQL (Neon Serverless)
- **Auth**: Better Auth with JWT tokens

## Requirements

### Functional Requirements
1. All Phase I features available via web interface
2. User registration and login
3. JWT-based authentication
4. Per-user task isolation
5. Persistent storage in PostgreSQL

### API Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/signup | Create new account |
| POST | /api/auth/login | Authenticate and get JWT |

#### Tasks (All require JWT Authorization header)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List all tasks for user |
| POST | /api/tasks | Create new task |
| GET | /api/tasks/{id} | Get task details |
| PUT | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| PATCH | /api/tasks/{id}/complete | Toggle completion |

### Data Models

#### User
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str | None = None
    created_at: datetime
```

#### Task
```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str
    description: str | None = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime
```

### Frontend Pages
1. `/` - Landing page (redirect to login or dashboard)
2. `/login` - Login form
3. `/signup` - Registration form
4. `/dashboard` - Main task management interface

### Security Requirements
1. Password hashing with bcrypt
2. JWT tokens with expiration
3. User can only access their own tasks
4. Input validation on all endpoints
5. CORS configuration for frontend

## Non-Functional Requirements
1. Responsive design (mobile-friendly)
2. Loading states for async operations
3. Error handling with user-friendly messages
4. Type safety throughout (TypeScript + Python type hints)
