---
name: akasha-subagent-dev
description: Workflow for coordinating and developing the "Council of Librarians" through subagent-driven development.
---
# Akasha Subagent-Driven Development

This skill implements the "Council of Librarians" pattern by dispatching independent subagents for complex tasks within the Akasha ecosystem.

## When to Use This Skill
- Decomposing complex features like "Chronos Engine" updates into multi-agent tasks.
- Simultaneously working on backend (FastAPI) and frontend (React) changes.
- Developing and testing multiple librarians in parallel.

## Instructions
1. **Delegation Strategy**: Use the "Head Archivist" role to delegate specific tasks to sub-librarians (Oracle, Scribe, Weaver).
2. **Review Checkpoints**: Each subagent must submit their work for a "Council Review" (automated tests or manual check).
3. **Context Isolation**: Ensure each subagent has only the context necessary for its task.
4. **State Synchronization**: Manage global state (akasha.db, ChromaDB) to prevent race conditions during parallel development.

## Examples
- "Delegate the task of updating the 'Oracle''s search logic while the 'Scribe' improves summarization."
- "Coordinate the 'Sentinel''s health monitoring with the 'Action Engine''s tool execution."
