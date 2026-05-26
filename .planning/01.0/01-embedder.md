---
phase: 01.0-foundation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified: [src/rag/embedder.py, tests/unit/test_embedder.py]
autonomous: true
requirements: [FR-2.1]
must_haves:
  truths:
    - Embedding model (all-MiniLM-L6-v2) runs on RPi 5 under 100ms per inference.
    - Model uses ONNX INT8 quantization for RAM efficiency.
  artifacts:
    - `src/rag/embedder.py` (Singleton Embedder)
    - ONNX model file in `.cache/ailo/`
---

## Objective

Implement the local embedding model (Sprint 2.1) using ONNX to provide semantic encoding for the RAG and Cascade Bouncer systems. This is a critical dependency for Phase 1.2.

## Context
- New AEGIS v2.1 Roadmap.
- Decision D-03 (ONNX Embeddings).

## Tasks

### Task 1: ONNX Embedder Implementation

**files:** src/rag/embedder.py
**action:**
1. Create a singleton `Embedder` class.
2. Implement model loading for `sentence-transformers/all-MiniLM-L6-v2`.
3. Use `onnxruntime` with INT8 quantization for inference.
4. Implement `encode_once(text)` and `encode(texts)` returning numpy arrays.
5. Set `onnxruntime.SessionOptions` to optimize for RPi 5 CPU (threading/memory).

**verify:** `python -c "from src.rag.embedder import Embedder; e = Embedder(); print(e.encode_once('test').shape)"` should output (384,).
**done:** Singleton embedder working with ONNX.

## Success Criteria
- Embedding generation works with < 100ms latency.
- Singleton pattern prevents multiple model loads.
