# Phase II: Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Login/Signup│  │ Dashboard   │  │ Task Components     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         └────────────────┼────────────────────┘            │
│                          │ HTTP + JWT                       │
└──────────────────────────┼──────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              JWT Auth Middleware                      │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              REST API Routes                          │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLModel ORM                             │   │
│  └────────────────────────┬─────────────────────────────┘   │
└───────────────────────────┼──────────────────────────────────┘
                            ↓
                  ┌──────────────────┐
                  │   PostgreSQL     │
                  │   (Neon)         │
                  └──────────────────┘
```

## Implementation Steps

### Step 1: Backend Setup
1. Create FastAPI project structure
2. Configure SQLModel and database connection
3. Define User and Task models
4. Set up Alembic for migrations

### Step 2: Authentication
1. Implement password hashing
2. Create JWT token generation/verification
3. Build auth middleware
4. Create signup/login endpoints

### Step 3: Task API
1. Implement CRUD operations
2. Add user_id filtering
3. Create all REST endpoints
4. Add input validation

### Step 4: Frontend Setup
1. Initialize Next.js with TypeScript
2. Configure Tailwind CSS
3. Set up API client with JWT handling
4. Create auth context/provider

### Step 5: Frontend Pages
1. Build login/signup forms
2. Create dashboard layout
3. Implement task list component
4. Add task creation/editing forms

### Step 6: Integration
1. Connect frontend to backend
2. Handle auth state
3. Test all flows
4. Error handling

## File Structure

```
todo-fullstack/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── tasks.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── login/
│   │   │   ├── signup/
│   │   │   └── dashboard/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── tailwind.config.ts
├── specs/
│   └── 002-web-app/
└── docker-compose.yml
```

## Environment Variables

### Backend
```
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Frontend
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
