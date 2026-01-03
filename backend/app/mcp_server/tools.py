"""MCP tools for task operations.

This module implements 5 Model Context Protocol (MCP) tools that the AI agent
uses to perform task operations. Each tool validates user_id and performs
database operations using SQLModel.

Tools:
1. add_task - Create a new task
2. list_tasks - Retrieve tasks with optional filtering
3. complete_task - Toggle task completion status
4. delete_task - Remove a task
5. update_task - Modify task title or description
"""
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from datetime import datetime

from ..models import Task
from ..database import engine


class MCPTools:
    """Collection of MCP tools for task management."""
    
    @staticmethod
    async def add_task(
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new task for the user.
        
        Args:
            user_id: User identifier
            title: Task title (1-200 characters)
            description: Optional task description (max 1000 characters)
        
        Returns:
            dict with task_id, status, title, description, created_at
        """
        # Validate inputs
        if not title or not title.strip():
            return {
                "error": "Title is required and cannot be empty",
                "status": "validation_error"
            }
        
        if len(title) > 200:
            return {
                "error": "Title must be 200 characters or less",
                "status": "validation_error"
            }
        
        if description and len(description) > 1000:
            return {
                "error": "Description must be 1000 characters or less",
                "status": "validation_error"
            }
        
        # Create task
        try:
            with Session(engine) as session:
                task = Task(
                    user_id=user_id,
                    title=title.strip(),
                    description=description.strip() if description else None,
                    completed=False
                )
                session.add(task)
                session.commit()
                session.refresh(task)
                
                return {
                    "task_id": task.id,
                    "status": "created",
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
        except Exception as e:
            return {
                "error": f"Failed to create task: {str(e)}",
                "status": "error"
            }
    
    @staticmethod
    async def list_tasks(
        user_id: str,
        status: str = "all"
    ) -> Dict[str, Any]:
        """
        List tasks for the user with optional status filter.
        
        Args:
            user_id: User identifier
            status: Filter by 'all', 'pending', or 'completed'
        
        Returns:
            dict with status, count, and array of tasks
        """
        # Validate status
        if status not in ["all", "pending", "completed"]:
            return {
                "error": "Status must be 'all', 'pending', or 'completed'",
                "status": "validation_error"
            }
        
        try:
            with Session(engine) as session:
                # Build query
                query = select(Task).where(Task.user_id == user_id)
                
                if status == "pending":
                    query = query.where(Task.completed == False)
                elif status == "completed":
                    query = query.where(Task.completed == True)
                
                # Execute query
                tasks = session.exec(query.order_by(Task.created_at.desc())).all()
                
                return {
                    "status": "success",
                    "count": len(tasks),
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "completed": task.completed,
                            "created_at": task.created_at.isoformat(),
                            "updated_at": task.updated_at.isoformat()
                        }
                        for task in tasks
                    ]
                }
        except Exception as e:
            return {
                "error": f"Failed to list tasks: {str(e)}",
                "status": "error"
            }
    
    @staticmethod
    async def complete_task(
        user_id: str,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Toggle task completion status.
        
        Args:
            user_id: User identifier
            task_id: Task ID to complete
        
        Returns:
            dict with task_id, status, title, completed
        """
        try:
            with Session(engine) as session:
                # Fetch task
                task = session.get(Task, task_id)
                
                if not task:
                    return {
                        "error": f"Task {task_id} not found",
                        "status": "not_found"
                    }
                
                # Verify ownership
                if task.user_id != user_id:
                    return {
                        "error": "Unauthorized: task belongs to another user",
                        "status": "unauthorized"
                    }
                
                # Toggle completion
                task.completed = not task.completed
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)
                
                return {
                    "task_id": task.id,
                    "status": "completed" if task.completed else "pending",
                    "title": task.title,
                    "completed": task.completed,
                    "updated_at": task.updated_at.isoformat()
                }
        except Exception as e:
            return {
                "error": f"Failed to complete task: {str(e)}",
                "status": "error"
            }
    
    @staticmethod
    async def delete_task(
        user_id: str,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Delete a task.
        
        Args:
            user_id: User identifier
            task_id: Task ID to delete
        
        Returns:
            dict with task_id, status, title
        """
        try:
            with Session(engine) as session:
                # Fetch task
                task = session.get(Task, task_id)
                
                if not task:
                    return {
                        "error": f"Task {task_id} not found",
                        "status": "not_found"
                    }
                
                # Verify ownership
                if task.user_id != user_id:
                    return {
                        "error": "Unauthorized: task belongs to another user",
                        "status": "unauthorized"
                    }
                
                # Store info before deletion
                task_info = {
                    "task_id": task.id,
                    "title": task.title
                }
                
                # Delete task
                session.delete(task)
                session.commit()
                
                return {
                    **task_info,
                    "status": "deleted"
                }
        except Exception as e:
            return {
                "error": f"Failed to delete task: {str(e)}",
                "status": "error"
            }
    
    @staticmethod
    async def update_task(
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update task details.
        
        Args:
            user_id: User identifier
            task_id: Task ID to update
            title: New task title (optional)
            description: New task description (optional)
        
        Returns:
            dict with task_id, status, title, description
        """
        # Validate at least one field provided
        if title is None and description is None:
            return {
                "error": "At least one field (title or description) must be provided",
                "status": "validation_error"
            }
        
        # Validate title length
        if title and len(title) > 200:
            return {
                "error": "Title must be 200 characters or less",
                "status": "validation_error"
            }
        
        # Validate description length
        if description and len(description) > 1000:
            return {
                "error": "Description must be 1000 characters or less",
                "status": "validation_error"
            }
        
        try:
            with Session(engine) as session:
                # Fetch task
                task = session.get(Task, task_id)
                
                if not task:
                    return {
                        "error": f"Task {task_id} not found",
                        "status": "not_found"
                    }
                
                # Verify ownership
                if task.user_id != user_id:
                    return {
                        "error": "Unauthorized: task belongs to another user",
                        "status": "unauthorized"
                    }
                
                # Update fields
                if title is not None:
                    task.title = title.strip()
                if description is not None:
                    task.description = description.strip() if description else None
                
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)
                
                return {
                    "task_id": task.id,
                    "status": "updated",
                    "title": task.title,
                    "description": task.description,
                    "updated_at": task.updated_at.isoformat()
                }
        except Exception as e:
            return {
                "error": f"Failed to update task: {str(e)}",
                "status": "error"
            }


# Export tools instance
mcp_tools = MCPTools()
