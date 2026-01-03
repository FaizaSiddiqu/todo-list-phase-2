# Phase II: Task Breakdown

## Backend Tasks

### Task 1: Project Setup
- [x] Create backend directory structure
- [x] Create requirements.txt with dependencies
- [x] Create config.py for settings
- [x] Create database.py for connection

### Task 2: Database Models
- [x] Create User model with SQLModel
- [x] Create Task model with SQLModel
- [x] Set up table creation

### Task 3: Authentication
- [x] Implement password hashing (bcrypt)
- [x] Create JWT token generation
- [x] Create JWT token verification
- [x] Build auth dependency for routes

### Task 4: Auth Routes
- [x] POST /api/auth/signup
- [x] POST /api/auth/login
- [x] GET /api/auth/me (get current user)

### Task 5: Task Routes
- [x] GET /api/tasks - list user tasks
- [x] POST /api/tasks - create task
- [x] GET /api/tasks/{id} - get task
- [x] PUT /api/tasks/{id} - update task
- [x] DELETE /api/tasks/{id} - delete task
- [x] PATCH /api/tasks/{id}/complete - toggle complete

### Task 6: Input Validation
- [x] Create Pydantic schemas
- [x] Add validation to all endpoints

## Frontend Tasks

### Task 7: Project Setup
- [x] Initialize Next.js with TypeScript
- [x] Configure Tailwind CSS
- [x] Create API client utility
- [x] Set up auth context

### Task 8: Auth Pages
- [x] Create login page
- [x] Create signup page
- [x] Handle form validation
- [x] Store JWT token

### Task 9: Dashboard
- [x] Create dashboard layout
- [x] Build task list component
- [x] Build task item component
- [x] Build task form component

### Task 10: Task Operations
- [x] Implement add task
- [x] Implement edit task
- [x] Implement delete task
- [x] Implement toggle complete

## Integration Tasks

### Task 11: Testing
- [ ] Test auth flow
- [ ] Test task CRUD
- [ ] Test error handling

### Task 12: Polish
- [ ] Add loading states
- [ ] Improve error messages
- [ ] Responsive design check
