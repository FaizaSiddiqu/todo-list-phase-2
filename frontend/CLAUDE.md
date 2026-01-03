# Frontend Guidelines - Next.js + TypeScript

> **Context**: Next.js 15+ frontend with TypeScript and Tailwind CSS

---

## Quick Reference

**Read First**: @../AGENTS.md and @../.specify/memory/constitution.md

**Current Phase**: III - AI Chatbot  
**Framework**: Next.js 15+ (App Router)  
**Language**: TypeScript (strict mode)  
**Styling**: Tailwind CSS

---

## Stack

- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript 5.7+ (strict mode)
- **Styling**: Tailwind CSS 3.4+
- **State**: React hooks (useState, useEffect, useContext)
- **Auth**: JWT tokens from backend
- **HTTP**: Fetch API with custom wrapper

---

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout with auth provider
│   │   ├── page.tsx           # Landing/home page
│   │   ├── globals.css        # Global styles
│   │   ├── login/
│   │   │   └── page.tsx       # Login page
│   │   ├── signup/
│   │   │   └── page.tsx       # Signup page
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Task management UI
│   │   └── chat/
│   │       └── page.tsx       # Chat interface (Phase III)
│   ├── components/
│   │   ├── TaskList.tsx       # Task list display
│   │   ├── TaskForm.tsx       # Task creation form
│   │   └── TaskItem.tsx       # Individual task
│   └── lib/
│       ├── api.ts             # API client with JWT
│       └── auth-context.tsx   # Auth context provider
├── public/
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

---

## Code Patterns

### 1. Component Structure

```typescript
'use client'; // Only when needed (interactivity, hooks)

import { useState, useEffect } from 'react';
import { Task } from '@/types';

interface TaskListProps {
  userId: string;
}

export default function TaskList({ userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await api.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} onUpdate={loadTasks} />
      ))}
    </div>
  );
}
```

### 2. Server Components (Default)

```typescript
// app/dashboard/page.tsx
// No 'use client' = Server Component (better performance)

import { TaskList } from '@/components/TaskList';

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <TaskList />
    </div>
  );
}
```

### 3. API Client Usage

```typescript
// lib/api.ts
import { Task, TaskCreate, TaskUpdate } from '@/types';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  async getTasks(): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks`, {
      headers: this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    
    return response.json();
  }

  async createTask(data: TaskCreate): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create task');
    }
    
    return response.json();
  }
}

export const api = new ApiClient();
```

---

## Authentication

### Auth Context Pattern

```typescript
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token');
    if (token) {
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const { access_token } = await response.json();
    localStorage.setItem('token', access_token);
    await fetchCurrentUser(access_token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## Styling with Tailwind

### Pattern
```typescript
export default function TaskItem({ task }: { task: Task }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">
          {task.title}
        </h3>
        {task.completed && (
          <span className="text-green-500 text-sm">✓ Completed</span>
        )}
      </div>
      {task.description && (
        <p className="text-gray-600 mt-2">{task.description}</p>
      )}
    </div>
  );
}
```

### Common Classes
```typescript
// Layout
"container mx-auto px-4"
"flex items-center justify-between"
"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"

// Spacing
"space-y-4" // Vertical spacing between children
"space-x-2" // Horizontal spacing

// Typography
"text-3xl font-bold"
"text-gray-600"

// Interactive
"hover:bg-blue-600 transition-colors"
"focus:outline-none focus:ring-2 focus:ring-blue-500"

// Buttons
"bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
```

---

## Forms

### Pattern
```typescript
'use client';

import { useState, FormEvent } from 'react';
import { api } from '@/lib/api';

export default function TaskForm({ onSuccess }: { onSuccess: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await api.createTask({ title, description });
      setTitle('');
      setDescription('');
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md">
          {error}
        </div>
      )}
      
      <input
        type="text"
        placeholder="Task title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2"
        disabled={loading}
      />
      
      <textarea
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2"
        rows={3}
        disabled={loading}
      />
      
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}
```

---

## TypeScript Types

### Pattern
```typescript
// types/index.ts or inline

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}
```

---

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```typescript
// Usage
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
```

**Note**: Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

---

## Navigation

### Pattern
```typescript
'use client';

import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = async () => {
    // ... login logic
    router.push('/dashboard'); // Navigate after login
  };

  return (
    // ...
  );
}
```

---

## Loading States

### Pattern
```typescript
export default function TaskList() {
  const [loading, setLoading] = useState(true);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    // ... content
  );
}
```

---

## Error Handling

### Pattern
```typescript
export default function TaskList() {
  const [error, setError] = useState<string | null>(null);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
        <p className="font-semibold">Error</p>
        <p>{error}</p>
      </div>
    );
  }

  return (
    // ... content
  );
}
```

---

## Common Patterns

### Protected Routes
```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) return <div>Loading...</div>;
  if (!user) return null;

  return (
    // ... protected content
  );
}
```

---

## Running the Frontend

```bash
# Development
npm run dev

# Build
npm run build

# Production
npm start
```

---

## Critical Rules

1. **Use 'use client' sparingly** - Only for interactivity
2. **Type everything** - TypeScript strict mode enforced
3. **Handle loading states** - Always show feedback
4. **Handle errors** - User-friendly error messages
5. **Responsive design** - Mobile-first approach
6. **JWT in headers** - Always include Authorization header
7. **Validate inputs** - Client-side validation before API calls

---

## Next Steps (Phase IV)

- Dockerize frontend
- Create Dockerfile with multi-stage build
- Optimize for production
- Prepare for Kubernetes deployment

---

**Version**: 1.0.0  
**Phase**: III - AI Chatbot  
**Last Updated**: January 3, 2026
