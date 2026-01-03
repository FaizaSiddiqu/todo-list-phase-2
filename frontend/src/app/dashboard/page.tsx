"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { tasksApi, Task } from "@/lib/api";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";

export default function DashboardPage() {
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      loadTasks();
    }
  }, [user]);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const data = await tasksApi.list();
      setTasks(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTask = async (title: string, description?: string) => {
    try {
      const newTask = await tasksApi.create({ title, description });
      setTasks([newTask, ...tasks]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    try {
      const updatedTask = await tasksApi.toggleComplete(taskId);
      setTasks(tasks.map((t) => (t.id === taskId ? updatedTask : t)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await tasksApi.delete(taskId);
      setTasks(tasks.filter((t) => t.id !== taskId));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const handleUpdateTask = async (
    taskId: number,
    title: string,
    description?: string
  ) => {
    try {
      const updatedTask = await tasksApi.update(taskId, { title, description });
      setTasks(tasks.map((t) => (t.id === taskId ? updatedTask : t)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const pendingTasks = tasks.filter((t) => !t.completed);
  const completedTasks = tasks.filter((t) => t.completed);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Todo App</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push("/chat")}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center space-x-1"
              >
                <span>🤖</span>
                <span>AI Chat</span>
              </button>
              <span className="text-gray-600">
                {user.name || user.email}
              </span>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
            <button
              onClick={() => setError("")}
              className="float-right text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        )}

        <div className="mb-8">
          <TaskForm onSubmit={handleAddTask} />
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-8">
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Pending Tasks ({pendingTasks.length})
              </h2>
              <TaskList
                tasks={pendingTasks}
                onToggleComplete={handleToggleComplete}
                onDelete={handleDeleteTask}
                onUpdate={handleUpdateTask}
              />
            </section>

            {completedTasks.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-500 mb-4">
                  Completed ({completedTasks.length})
                </h2>
                <TaskList
                  tasks={completedTasks}
                  onToggleComplete={handleToggleComplete}
                  onDelete={handleDeleteTask}
                  onUpdate={handleUpdateTask}
                />
              </section>
            )}

            {tasks.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No tasks yet. Add your first task above!
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
