import os

try:
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class AIEngine:
    def __init__(self):
        self.model_id = "Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF"
        self.filename = "qwen2.5-coder-0.5b-instruct-q4_k_m.gguf"
        self.llm = None

    def _ensure_model_loaded(self):
        if not AI_AVAILABLE:
            print("AI libraries not installed. Please install huggingface_hub and llama-cpp-python.")
            return

        if self.llm is not None:
            return

        print("Downloading/Loading AI model. This may take a moment...")
        try:
            model_path = hf_hub_download(repo_id=self.model_id, filename=self.filename)
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                verbose=False
            )
        except Exception as e:
            print(f"Failed to load AI model: {e}")

    def translate_text_to_sql(self, user_prompt: str) -> str:
        self._ensure_model_loaded()
        if not self.llm:
            return ""

        system_prompt = """You are a strictly Read-Only SQLite code generator.
The database contains a table named 'records' with the following schema:
- id (INTEGER PRIMARY KEY)
- city_name (TEXT)
- aqi_value (REAL)
- timestamp (TEXT)

Generate a SELECT query based on the user's request.
Note: City names are typically capitalized (e.g. 'London', not 'london'). Please apply COLLATE NOCASE or upper/lower functions if filtering by city_name to ensure case-insensitive matching.
Return ONLY the raw SQL query.
DO NOT wrap the output in markdown block quotes (e.g. no ```sql).
DO NOT provide any explanations.
ONLY return the SQL statement."""

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"

        try:
            response = self.llm(
                prompt,
                max_tokens=150,
                stop=["<|im_end|>"],
                temperature=0.1
            )
            sql_query = response['choices'][0]['text'].strip()

            # Additional cleanup in case the model ignores instructions and returns markdown
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]

            return sql_query.strip()
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return ""
