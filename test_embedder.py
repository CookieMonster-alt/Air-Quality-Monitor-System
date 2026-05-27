import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import numpy as np
from src.rag.embedder import embedder

def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)

def run_tests():
    print("Test 1: Model Loading Time")
    start = time.time()
    embedder.load_model()
    load_time = time.time() - start
    print(f"Model loaded in {load_time:.2f}s")
    assert load_time < 30.0, "Model loading took too long!"

    print("\nTest 2: Quality Check (Cosine Similarity)")
    v1 = embedder.encode("king")
    v2 = embedder.encode("queen")
    sim = cosine_similarity(v1, v2)
    print(f"Similarity 'king' vs 'queen': {sim:.3f}")
    assert sim > 0.5, "Similarity score is suspiciously low."

    print("\nTest 3: Batch Encoding Performance")
    mock_sentences = [f"This is test sentence number {i} regarding air quality." for i in range(100)]

    start = time.time()
    batch_res = embedder.encode(mock_sentences, batch_size=32)
    batch_time = time.time() - start
    print(f"Encoded 100 sentences in {batch_time:.2f}s")
    assert batch_time < 5.0, "Batch encoding took too long!"

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
