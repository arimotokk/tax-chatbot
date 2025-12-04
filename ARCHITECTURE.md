# RAG Architecture - Phase 1

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                     (Flask Web App)                              │
│                                                                   │
│  ┌────────────────┐                                              │
│  │ User Question  │                                              │
│  └───────┬────────┘                                              │
│          │                                                        │
│          ▼                                                        │
│  ┌─────────────────────────────────────────────┐                │
│  │         1. SEMANTIC SEARCH                   │                │
│  │                                               │                │
│  │  Question → Vector Embedding                 │                │
│  │           → ChromaDB Query                   │                │
│  │           → Retrieve Top 5 Chunks            │                │
│  └─────────────────┬───────────────────────────┘                │
│                    │                                              │
│                    ▼                                              │
│  ┌─────────────────────────────────────────────┐                │
│  │         2. CONTEXT BUILDING                  │                │
│  │                                               │                │
│  │  - Retrieved chunks + metadata               │                │
│  │  - Conversation history (last 3 turns)       │                │
│  │  - Structured prompt template                │                │
│  └─────────────────┬───────────────────────────┘                │
│                    │                                              │
│                    ▼                                              │
│  ┌─────────────────────────────────────────────┐                │
│  │    3. ANSWER GENERATION (Claude Sonnet)     │                │
│  │                                               │                │
│  │  Input: Question + Context                   │                │
│  │  Output: Answer + Citations + Excerpts      │                │
│  └─────────────────┬───────────────────────────┘                │
│                    │                                              │
│                    ▼                                              │
│  ┌─────────────────────────────────────────────┐                │
│  │         4. RESPONSE DISPLAY                  │                │
│  │                                               │                │
│  │  ✓ Formatted answer                          │                │
│  │  ✓ Source citations (doc + page)             │                │
│  │  ✓ Relevant excerpts from sources            │                │
│  └─────────────────────────────────────────────┘                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                   │
│  ┌──────────────────────┐      ┌─────────────────────────┐      │
│  │   NTA PDF Source     │      │   ChromaDB Storage      │      │
│  │                      │      │                         │      │
│  │  • 2024 Income Tax   │ ───▶ │  • Text chunks          │      │
│  │    Guide (72 pages)  │      │  • Vector embeddings    │      │
│  │  • Official English  │      │  • Metadata (page, src) │      │
│  │    translation       │      │  • ~2000+ chunks        │      │
│  └──────────────────────┘      └─────────────────────────┘      │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

Key Features:
✓ Retrieval-Augmented Generation (RAG)
✓ Semantic search using vector embeddings
✓ Context-aware responses with conversation history
✓ Source attribution (document name + page number)
✓ Relevant excerpts for transparency
✓ Session-based conversation memory

Next Phase: Fact-checking agent validation before display
```
