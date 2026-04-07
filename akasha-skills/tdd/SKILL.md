---
name: akasha-tdd
description: Test-Driven Development (TDD) practitioner for the Akasha multi-agent ecosystem.
---
# Akasha TDD Practitioner

This skill ensures that all new functionality in Akasha is built using a strict TDD workflow to maintain system stability and agentic reliability.

## When to Use This Skill
- Before implementing any new librarian, tool, or engine component.
- When fixing bugs in the backend (FastAPI) or CLI interface.
- Ensuring integration between multiple librarians (Council of Librarians).

## Instructions
1. **Test-First**: Write a failing test case before any implementation code.
2. **Pytest Focused**: Use `pytest` for backend tests.
3. **Agent Mocking**: When testing a librarian, mock the responses of other librarians to isolate behavior.
4. **Local Integration**: Ensure tests can run against a local SQLite (`akasha.db`) and local ChromaDB.
5. **Coverage**: Maintain high coverage for "Sentinel" healthy-check and "Action Engine" tool calls.

## Examples
- "Write a failing test for the 'Oracle' librarian's synthesis method before implementation."
- "Fix a bug in the 'akasha ego' CLI command by first reproducing it with a test."
