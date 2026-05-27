import chromadb
import os

def setup_chroma():
    """
    Initializes the ChromaDB persistent client and sets up the semantic RAG collection.
    Enforces 'cosine' similarity space as per architectural constraints.
    """
    db_path = os.path.join("data", "vector_db")
    print(f"Initializing ChromaDB at {db_path}...")

    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)

    # We create or get the collection and enforce cosine distance for our embedder
    collection = client.get_or_create_collection(
        name="ailo_intents",
        metadata={"hnsw:space": "cosine"}
    )

    print("ChromaDB setup complete. Collection 'ailo_intents' ready.")
    print(f"Current document count: {collection.count()}")

if __name__ == "__main__":
    setup_chroma()
