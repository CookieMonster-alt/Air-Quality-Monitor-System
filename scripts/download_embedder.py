import os
from sentence_transformers import SentenceTransformer

def download_and_cache_model():
    """
    Downloads the all-MiniLM-L6-v2 model and saves it strictly to the local cache directory.
    This prevents internet dependency during startup on the Raspberry Pi.
    """
    target_dir = "ailo/models/embedder"
    model_id = "all-MiniLM-L6-v2"

    print(f"Starting download of '{model_id}'...")

    if os.path.exists(target_dir) and os.listdir(target_dir):
        print(f"Model already exists at {target_dir}. Skipping download.")
        return

    os.makedirs(target_dir, exist_ok=True)

    print("Fetching from HuggingFace Hub (This might take a moment)...")
    try:
        model = SentenceTransformer(model_id)
        model.save(target_dir)
        print(f"Successfully downloaded and cached model to: {target_dir}")
    except Exception as e:
        print(f"Failed to download model: {e}")

if __name__ == "__main__":
    download_and_cache_model()
