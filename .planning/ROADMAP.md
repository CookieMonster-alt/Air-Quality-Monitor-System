---
project: AILO (AI Local Operator)
version: 2.1
---

# Roadmap (AEGIS Pipeline v2.1)

## Phase 01: Intent & RAG Foundation
- **Goal:** Establish the Cascade Bouncer and Semantic Embedder.
- **Sprints:** 2.1 (Embedder), 1.1 (ML Intent), 1.2 (Semantic Intent).
- **Deliverables:** `src/rag/embedder.py`, `src/intent/cascade_bouncer.py`.

## Phase 02: Memory & TUI Integration
- **Goal:** Persistent vector memory and Omnibar suggestions.
- **Sprints:** 1.3 (LLM Fallback), 2.2 (ChromaDB), 2.3 (TUI Integration).
- **Deliverables:** `src/rag/vector_store.py`, Updated `tui_engine.py`.

## Phase 03: Brain Transplant
- **Goal:** Switch to a more powerful local LLM with constrained decoding.
- **Sprints:** 3.1 (Benchmark), 3.2 (Llama-cpp), 3.3 (Grammar), 3.4 (Pipeline).

## Phase 04: Feedback & Learning
- **Goal:** Self-correction loop and feedback logging.
- **Sprints:** 4.1 (Feedback Loop), 4.2 (Error Analysis).

## Phase 05: Night Watchman
- **Goal:** Autonomous night training with Gemini.
- **Sprints:** 5.1 (Cron Pipeline), 5.2 (Synthetic Data).

## Phase 06: Future Vision (IoT/Vision)
- **Goal:** Tool calling, GPIO control, OpenCV integration.
