import re
import chromadb
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Import the pre-warmed embedder
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.rag.embedder import embedder
from async_executor import ailo_executor

try:
    from src.model.inference_engine import InferenceEngine
    LLM_AVAILABLE = True
except ImportError as ie:
    print(f"\n[CRITICAL IMPORT ERROR]\n{ie}\n") # BURAYI EKLEDİK
    LLM_AVAILABLE = False
    InferenceEngine = None

class CascadeGuard:
    """
    A 4-Layer Cascade Guard orchestrator for determining user intent rapidly.
    Layers:
      1. Regex (0.1ms)
      2. ML LogisticRegression (1-5ms)
      3. Semantic RAG via ChromaDB (10-50ms)
      4. Fallback LLM (Deferred to caller if UNKNOWN)
    """
    def __init__(self):
        self._init_layer_1()
        self._init_layer_2()
        self._init_layer_3()

        self.engine = None
        if LLM_AVAILABLE:
            try:
                self.engine = InferenceEngine()
            except Exception as e:
                import traceback
                print(f"\n[CRITICAL INITIALIZATION DEBUG]\n{traceback.format_exc()}\n") # BURAYI EKLEDİK
                self.engine = None

    def _init_layer_1(self):
        # Strict Regex mappings for raw speed
        self.regex_patterns = [
            (r'^\/(router|analyst|visualize|train|backup|export|clear|help|exit)$', "navigate"),
            (r'\b(delete|remove|erase|drop)\b', "delete"),
            (r'\b(add|insert|record|save)\b', "insert"),
            (r'\b(download|fetch|pull|import)\b.*(csv|data|history)', "fetch_data"),
            (r'\b(analyze|average|max|min|count|show|get|what|how)\b', "query")
        ]

    def _init_layer_2(self):
        """Train a lightweight, blazingly fast LogisticRegression classifier."""
        # Minimal training set purely for demonstration/bootstrapping
        # In a real scenario, this would load from a pre-trained pickle
        corpus = [
            "show me the aqi for london", "what is the highest pollution", "average aqi in paris",
            "delete the records for madrid", "erase all data from 2023",
            "add a new city", "insert tokyo with aqi 45",
            "download csv data", "fetch historical air quality",
            "/router", "/help"
        ]
        labels = [
            "query", "query", "query",
            "delete", "delete",
            "insert", "insert",
            "fetch_data", "fetch_data",
            "navigate", "navigate"
        ]

        self.vectorizer = TfidfVectorizer(stop_words='english', analyzer='char_wb', ngram_range=(2,4))
        X = self.vectorizer.fit_transform(corpus)

        # LogisticRegression provides predict_proba unlike LinearSVC
        self.clf = LogisticRegression(class_weight='balanced')
        self.clf.fit(X, labels)

    def _init_layer_3(self):
        """Initialize connection to ChromaDB for Semantic RAG."""
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="ailo_intents",
            metadata={"hnsw:space": "cosine"}
        )

    async def classify(self, text: str):
        """Execute the 4-layer cascade asynchronously."""
        text_lower = text.lower().strip()

        # LAYER 1: Regex Fast-Match
        for pattern, intent in self.regex_patterns:
            if re.search(pattern, text_lower):
                return intent

        # LAYER 2: ML Classifier
        vec = self.vectorizer.transform([text_lower])
        probs = self.clf.predict_proba(vec)[0]
        max_prob_idx = probs.argmax()

        if probs[max_prob_idx] > 0.65:
            return self.clf.classes_[max_prob_idx]

        # LAYER 3: Semantic RAG
        # We need the embedder to be loaded. It should be pre-warmed, but we check.
        if embedder._model is not None:
            emb = embedder.encode(text)

            # ChromaDB expects a list of list of floats
            emb_list = [float(x) for x in emb]

            # We only perform search if there is data in the collection
            if self.collection.count() > 0:
                results = self.collection.query(
                    query_embeddings=[emb_list],
                    n_results=1
                )

                if results['distances'] and results['distances'][0]:
                    # ChromaDB returns cosine distance.
                    # Cosine Similarity = 1 - distance
                    distance = results['distances'][0][0]
                    similarity = 1.0 - distance
                    if similarity > 0.60:
                        # Assuming metadata holds 'intent'
                        meta = results['metadatas'][0][0]
                        if meta and 'intent' in meta:
                            return meta['intent']

        # LAYER 4: LLM Fallback
        if self.engine:
            prompt = f"""<|im_start|>system
You are AILO, a helpful air quality AI assistant.
Determine the user's intent and formulate a helpful response.
You MUST respond strictly in valid JSON matching this schema: {{"intent": "llm_chat", "response": "<your helpful answer>"}}.
<|im_end|>
<|im_start|>user
{text}
<|im_end|>
<|im_start|>assistant
"""
            # Yield to the background executor to keep UI responsive while generating
            result = await ailo_executor.run_in_background(self.engine.generate_json, prompt)
            return result
        else:
            return "UNKNOWN"

# Export singleton
cascade_guard = CascadeGuard()
