/**
 * API client for communicating with the backend.
 */

const API_BASE = "/api";

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
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

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Auth API
export const authApi = {
  signup: (data: SignupData) =>
    request<User>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (credentials: LoginCredentials) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    }),

  me: () => request<User>("/auth/me"),
};

// Tasks API
export const tasksApi = {
  list: () => request<Task[]>("/tasks"),

  get: (id: number) => request<Task>(`/tasks/${id}`),

  create: (data: TaskCreate) =>
    request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TaskUpdate) =>
    request<Task>(`/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    request<void>(`/tasks/${id}`, {
      method: "DELETE",
    }),

  toggleComplete: (id: number) =>
    request<Task>(`/tasks/${id}/complete`, {
      method: "PATCH",
    }),
};
