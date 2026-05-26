---
project: AILO (AI Local Operator)
version: 2.1
---

# Requirements (AEGIS Pipeline v2.1)

## Functional Requirements

### Epic 1: Cascade Bouncer (Intent Classification)
- FR-1.1: Multi-layer intent classification (Regex, LogisticRegression, Semantic, LLM).
- FR-1.2: LogisticRegression for probability estimation (Fix 1).
- FR-1.3: Asynchronous feedback logging for self-correction.

### Epic 2: Semantic RAG
- FR-2.1: Local embedding model (all-MiniLM-L6-v2) in ONNX format.
- FR-2.2: ChromaDB vector store using Cosine similarity (Fix 2).
- FR-2.3: Semantic memory retrieval with thresholding (>85%).

### Epic 3: Brain Transplant (Model Upgrade)
- FR-3.1: Support for GGUF models (Llama-3.2 or Qwen-2.5-1.5B).
- FR-3.2: Streaming inference with constrained decoding (Grammar/JSON).

### Epic 4 & 5: Autonomous Repair & Night Watchman
- FR-4.1: User feedback loop (/fix, /wrong).
- FR-5.1: Autonomous night training loop with Gemini API for synthetic data.

## Non-Functional Requirements
- NFR-01: RAM consumption < 2GB total.
- NFR-02: Intent classification latency < 200ms.
- NFR-03: Inference speed > 10 tokens/sec.
- NFR-04: 100% English-only system prompts and internal logic.

## Constraints
- Hardware: Raspberry Pi 5 (8GB).
- SQLite WAL mode & `check_same_thread=False` required.
- TUI thread MUST NOT be blocked (use AsyncIO/ThreadPool).

## Key Fixes Applied (v2.1)
- D-1: Use `LogisticRegression` instead of `LinearSVC` (for `predict_proba`).
- D-2: Use `cosine` space in ChromaDB (instead of default L2).
