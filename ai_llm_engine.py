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


    def parse_intent(self, user_prompt: str) -> dict:
        self._ensure_model_loaded()
        if not self.llm:
            return {"intent": "unknown", "status": "incomplete", "ask_user": "AI engine offline."}

        import datetime
        import json
        today = datetime.date.today().isoformat()

        system_prompt = f"""You are AILO, the Intent Router for an Air Quality Database System.
Today's date is: {today}.

Analyze the user's natural language input and output ONLY a valid JSON object matching this schema:
{{
  "intent": "query" | "insert" | "delete" | "fetch_data" | "navigate",
  "parameters": {{
    "city": string | null,
    "aqi": float | null,
    "date": string | null,
    "start_date": string | null,
    "end_date": string | null,
    "url": string | null,
    "menu_target": string | null
  }},
  "status": "complete" | "incomplete",
  "missing_slot": string | null,
  "ask_user": string | null
}}

Rules:
- "query": User wants to search, read, or analyze data. (e.g. "show me the highest AQI", "what is London's data")
- "insert": User wants to add new data. (e.g. "add paris with aqi 45")
- "delete": User wants to erase data. (e.g. "delete records for london")
- "fetch_data": User wants to bulk import historical/online data (requires start_date, end_date, and url).
- "navigate": User wants to open a menu.
- If an intent requires specific parameters that are missing, set "status": "incomplete", specify "missing_slot", and write a natural question in "ask_user" to prompt the user for it.
- E.g. If insert is requested but aqi is missing, you DO NOT need to ask for aqi, because the system can fetch it autonomously. Just return city.
- DO NOT wrap the output in markdown. Output purely the JSON object.
"""

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"

        try:
            response = self.llm(
                prompt,
                max_tokens=256,
                stop=["<|im_end|>"],
                temperature=0.1
            )
            output_text = response['choices'][0]['text'].strip()

            # Cleanup markdown if model hallucinates it
            if output_text.startswith("```json"):
                output_text = output_text[7:]
            if output_text.startswith("```"):
                output_text = output_text[3:]
            if output_text.endswith("```"):
                output_text = output_text[:-3]

            return json.loads(output_text.strip())
        except Exception as e:
            print(f"Error parsing intent: {e}")
            return {"intent": "unknown", "status": "incomplete", "ask_user": "I failed to parse your intent."}
