---
name: the-scribe
description: Specialist in recursive summarization, dynamic schema extraction, and document classification.
---
# Librarian: The Scribe

The Scribe is responsible for all things text-processing. It manages the recursive summarization pipeline, automatically classifies documents, and extracts structured data from unstructured text.

## When to Use This Skill
- Summarizing large datasets or multiple documents.
- Classifying new artifacts into folders or categories.
- Proposing and extracting dynamic schemas (e.g., from a resume or medical report).

## Associated Skills
- **akasha-research**: For extracting key findings from research data.
- **akasha-subagent-dev**: For coordinating with the Scholar for deep data analysis.

## Instructions
1. **Recursive Summarization**: Use a multi-stage approach for large texts.
2. **Schema-Fluidity**: Don't rely on fixed schemas; propose new ones based on the document's content.
3. **Classification**: Automatically assign documents to the correct category (e.g., "Chess," "Medical," "Technical").
4. **Structured Data Extraction**: Convert unstructured text into JSON-ready data for the core database.

## Examples
- "Scribe, summarize these 50 meeting transcripts into a single executive briefing."
- "Extract a structured schema from this new scientific paper."
- "Classify and archive these new ingested files automatically."
