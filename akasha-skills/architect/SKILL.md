---
name: akasha-architect
description: Expert guidance on the Council of Librarians architecture, multi-agent systems, and digital sovereignty.
---
# Akasha Architect Skill

This skill provides expert knowledge for maintaining and extending the Akasha ecosystem, ensuring that new features adhere to the "Council of Librarians" multi-agent architecture and the principles of digital sovereignty.

## When to Use This Skill
- Adding new librarians to the Council (Head Archivist, Oracle, Scribe, etc.).
- Modifying the "Chronos Engine" for temporal reasoning.
- Integrating new local-first storage or LLM tools (Ollama, ChromaDB, Neo4j).
- Ensuring data remains encrypted, local-first, and sovereign.

## Instructions
1. **Multi-Agent Coordination**: Always decompose complex tasks into sub-tasks for specialized librarians. Use the "Head Archivist" as the router.
2. **Local-First Mandate**: No external API calls are allowed for data processing unless "Sovereign Mode" is explicitly disabled by the user.
3. **Graph-RAG Integration**: When implementing search, prioritize the "Oracle's" Graph-RAG synthesis over basic vector retrieval.
4. **Recursive Synthesis**: Use the "Scribe's" patterns for dynamic schema extraction and multi-stage summarization.
5. **Security & Redaction**: The "Sentinel" must always check for PII (Personally Identifiable Information) before any (optional) cloud interaction.

## Examples
- "Architect a new 'Cartographer' librarian to map geospatial data within the Akasha core."
- "Extend the 'Nocturnal Consolidation' phase to include cross-document contradiction detection."
