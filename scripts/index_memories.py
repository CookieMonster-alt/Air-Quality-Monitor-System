import json
import glob
import os
import sys
import time

# Ensure we can import the src module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.rag.embedder import embedder

def process_memory_file(filepath: str):
    """
    Reads a memory JSON file, converts the 'query' strings into semantic embeddings,
    and writes the updated structure back to disk. Batch processing is used for speed.
    """
    print(f"Processing {filepath}...")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return

    queries = []
    # Collect queries that don't have embeddings yet
    for item in data:
        if 'query' in item and 'embedding' not in item:
            queries.append(item['query'])

    if not queries:
        print(f"No new queries to index in {filepath}.")
        return

    print(f"Encoding {len(queries)} queries...")
    start_time = time.time()

    # Batch encode
    embeddings = embedder.encode(queries, batch_size=32)

    duration = time.time() - start_time
    print(f"Batch encoded in {duration:.3f} seconds.")

    # Merge embeddings back into the original data
    emb_idx = 0
    for item in data:
        if 'query' in item and 'embedding' not in item:
            # We convert the numpy array to a standard python list of floats for JSON serialization
            item['embedding'] = [float(x) for x in embeddings[emb_idx]]
            emb_idx += 1

    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved embedded data to {filepath}.")
    except Exception as e:
        print(f"Failed to write {filepath}: {e}")

def main():
    print("Initializing AILO Embedder for Memory Indexing...")
    # This will trigger the initial model load
    embedder.load_model()

    memory_files = glob.glob("memory_*.json") + glob.glob("ai_memory.json")
    if not memory_files:
        print("No memory files found.")
        return

    for f in set(memory_files):
        process_memory_file(f)

if __name__ == "__main__":
    main()
