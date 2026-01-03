# AGENTS.md

## Purpose

This project uses **Spec-Driven Development (SDD)** — a workflow where **no agent is allowed to write code until the specification is complete and approved**.

All AI agents (Claude Code, Copilot, Gemini, etc.) must follow the **Spec-Kit lifecycle**:

> **Specify → Plan → Tasks → Implement**

This prevents "vibe coding," ensures alignment across agents, and guarantees that every implementation step maps back to an explicit requirement.

---

## How Agents Must Work

Every agent in this project MUST obey these rules:

1. **Never generate code without a referenced specification.**
2. **Never modify architecture without updating the plan document.**
3. **Never propose features without updating the spec document (WHAT).**
4. **Never change approach without updating the constitution (Principles).**
5. **Every code file must be traceable to spec sections.**

If an agent cannot find the required spec, it must **stop and request it**, not improvise.

---

## Spec-Kit Workflow (Source of Truth)

### 1. Constitution (WHY — Principles & Constraints)

File: `.specify/memory/constitution.md`

Defines the project's non-negotiables:
- Architecture values
- Security rules
- Tech stack constraints
- Performance expectations
- Allowed patterns

Agents must check this before proposing solutions.

---

### 2. Specify (WHAT — Requirements, Journeys & Acceptance Criteria)

Files: `specs/*/spec.md`

Contains:
- User journeys
- Requirements
- Acceptance criteria
- Domain rules
- Business constraints

Agents must not infer missing requirements — they must request clarification or propose specification updates.

---

### 3. Plan (HOW — Architecture, Components, Interfaces)

Files: `specs/*/plan.md`

Includes:
- Component breakdown
- APIs & schema diagrams
- Service boundaries
- System responsibilities
- High-level sequencing

All architectural output MUST be generated from the Specify file.

---

### 4. Tasks (BREAKDOWN — Atomic, Testable Work Units)

Files: `specs/*/tasks.md`

Each Task must contain:
- Task ID
- Clear description
- Preconditions
- Expected outputs
- Artifacts to modify
- Links back to Specify + Plan sections

Agents **implement only what these tasks define**.

---

### 5. Implement (CODE — Write Only What the Tasks Authorize)

Agents now write code, but must:
- Reference specification sections
- Follow the Plan exactly
- Not invent new features or flows
- Stop and request clarification if anything is underspecified

> The golden rule: **No spec = No code.**

---

## Project Structure

This is a monorepo with the following structure:

```
todo-fullstack/
├── AGENTS.md                     # This file
├── CLAUDE.md                     # Claude Code entry point
├── .specify/
│   └── memory/
│       └── constitution.md       # Core principles
├── specs/
│   ├── 002-web-app/             # Phase II specifications
│   │   ├── spec.md              # Requirements
│   │   ├── plan.md              # Architecture
│   │   └── tasks.md             # Implementation tasks
│   └── 003-chatbot/             # Phase III specifications
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── backend/
│   ├── CLAUDE.md                # Backend-specific instructions
│   └── app/                     # FastAPI application
├── frontend/
│   ├── CLAUDE.md                # Frontend-specific instructions
│   └── src/                     # Next.js application
└── docker-compose.yml
```

---

## Agent Behavior in This Project

### When generating code:

Agents must reference:
```
[Spec]: specs/002-web-app/spec.md §2.1
[Plan]: specs/002-web-app/plan.md §3.4
```

### When proposing architecture:

Agents must reference:
```
Update required in specs/*/plan.md → add component X
```

### When proposing new behavior or a new feature:

Agents must reference:
```
Requires update in specs/*/spec.md (WHAT)
```

### When changing principles:

Agents must reference:
```
Modify .specify/memory/constitution.md → Principle #X
```

---

## Agent Failure Modes (What Agents MUST Avoid)

Agents are NOT allowed to:
- Freestyle code or architecture
- Generate missing requirements
- Create tasks on their own
- Alter stack choices without justification
- Add endpoints, fields, or flows that aren't in the spec
- Ignore acceptance criteria
- Produce "creative" implementations that violate the plan

If a conflict arises between spec files, the **Constitution > Specify > Plan > Tasks** hierarchy applies.

---

## Technology Stack (Non-Negotiable)

### Phase II - Web Application
- **Frontend**: Next.js 15+, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT with bcrypt

### Phase III - AI Chatbot
- **AI Framework**: OpenAI Agents SDK
- **Tools**: Custom MCP Tools (Official MCP SDK)
- **Chat UI**: OpenAI ChatKit
- **Conversation State**: Stateless (persisted to DB)

---

## Development Workflow

### Starting a New Phase

1. **Read Constitution**: `.specify/memory/constitution.md`
2. **Create Specification**: `specs/00X-feature/spec.md`
3. **Generate Plan**: `specs/00X-feature/plan.md`
4. **Break into Tasks**: `specs/00X-feature/tasks.md`
5. **Implement**: Write code following the plan

### Modifying Existing Features

1. **Update Specification**: Modify relevant `spec.md`
2. **Update Plan**: Reflect changes in `plan.md`
3. **Update Tasks**: Add/modify tasks in `tasks.md`
4. **Implement**: Execute changes

---

## Spec-Driven Commands

When using Spec-Kit Plus or similar tools:

```bash
# Initialize project with constitution
specifyplus init todo-fullstack

# Create specification for a feature
specifyplus specify --feature "task management"

# Generate technical plan from spec
specifyplus plan --from-spec specs/002-web-app/spec.md

# Break plan into implementation tasks
specifyplus tasks --from-plan specs/002-web-app/plan.md

# Implement tasks with AI assistance
specifyplus implement --task T-001
```

---

## Git Workflow

All commits should follow the SDD lifecycle:

```
# Good commit sequence
1. "docs: Add Phase III specification (chatbot)"
2. "docs: Generate Phase III technical plan"
3. "docs: Break Phase III into tasks"
4. "feat: Implement Phase III - AI chatbot (T-001 to T-015)"

# Bad commit sequence
❌ "feat: Add chatbot" (no spec, no plan, no tasks)
```

---

## Multi-Agent Collaboration

When multiple AI agents work on this project:

1. **Always read AGENTS.md first** to understand the workflow
2. **Read the Constitution** to understand constraints
3. **Read relevant specs** before proposing changes
4. **Reference spec sections** in all proposals
5. **Update specs** before implementing changes

---

## For Claude Code Users

Claude Code should load this file automatically via `CLAUDE.md`.

Key points:
- Use `@specs/002-web-app/spec.md` to reference specifications
- Use `@.specify/memory/constitution.md` for principles
- Follow the Spec → Plan → Tasks → Implement workflow
- Never write code without a corresponding specification

---

## For GitHub Copilot Users

Add this to your `.github/copilot-instructions.md`:

```markdown
This project follows Spec-Driven Development. Before suggesting code:
1. Check if feature is specified in specs/*/spec.md
2. Verify architecture in specs/*/plan.md
3. Reference task IDs from specs/*/tasks.md
4. Follow patterns in .specify/memory/constitution.md
```

---

## Questions & Clarifications

If an agent encounters:
- **Missing specification**: Ask the developer to create one
- **Ambiguous requirement**: Request clarification in the spec
- **Conflicting guidance**: Follow the hierarchy (Constitution > Spec > Plan > Tasks)
- **Unclear task**: Request task breakdown in `tasks.md`

---

## Summary

This project is built with **Spec-Driven Development**:
- ✅ All features start with specifications
- ✅ Architecture is planned before implementation
- ✅ Tasks are explicit and traceable
- ✅ Code maps back to requirements
- ❌ No "vibe coding" allowed

**Agents**: Read this file first. Follow the workflow. Reference specs. Ask when unclear.

---

**Version**: 1.0.0  
**Phase**: III - AI Chatbot  
**Updated**: January 3, 2026
