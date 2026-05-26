---
project: AILO (AI Local Operator)
created: 2026-05-26
---

# Project Context (AEGIS v2.1)

## Vision
AILO (AI Local Operator) is a privacy-first Edge AI IoT hub for RPi 5. It uses a 4-layer cascade for intent routing and semantic RAG for memory, with autonomous night-time learning.

## Tech Stack
- **Language:** Python 3.x
- **Embedder:** `all-MiniLM-L6-v2` (ONNX)
- **Vector DB:** ChromaDB (Cosine Space)
- **LLM Engine:** `llama-cpp-python` (Llama 3.2 or Qwen 2.5)
- **Database:** SQLite (WAL mode)
- **TUI:** `rich` + `prompt_toolkit`
- **Fallback:** Google Gemini 2.0 Flash

## Architecture
- **Cascade Bouncer:** Regex -> LogisticRegression -> Semantic -> LLM.
- **Waterfall Pipeline:** Efficient routing before hitting heavy LLM.
- **Knowledge Distillation:** Nightly synthetic data generation from failures.

## Decisions
| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| D-01 | LogisticRegression | `LinearSVC` lacks `predict_proba`. Required for confidence. | locked |
| D-02 | Cosine Space | Better for semantic similarity in ChromaDB than L2. | locked |
| D-03 | ONNX Embeddings | Faster inference & lower RAM on RPi 5. | locked |
| D-04 | WAL Mode | Concurrent SQLite access during TUI/Inference. | locked |
