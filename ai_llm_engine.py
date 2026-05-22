import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from dotenv import load_dotenv
    # Load .env file using its absolute path relative to this script's directory
    base_dir = BASE_DIR
    dotenv_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path)
except ImportError:
    pass

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

        import json
        manifest = ""
        memory = ""
        try:
            with open(os.path.join(BASE_DIR, "ailo_manifest.yaml"), "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."

        history_str = ""
        try:
            with open(os.path.join(BASE_DIR, "ai_memory.json"), "r") as f:
                mem_data = json.load(f)
                if mem_data:
                    has_relative_query = any(w in user_prompt.lower() for w in ["yesterday", "today", "week", "month", "ago", "last"])
                    filtered_mems = []
                    for m in mem_data:
                        mem_s = m.get('sql', '').lower()
                        is_relative_mem = "date('now'" in mem_s or "datetime('now'" in mem_s
                        # If user prompt is relative, only show relative memories
                        if has_relative_query:
                            if not is_relative_mem:
                                continue
                        else:
                            # If user prompt is not relative, exclude relative memories
                            if is_relative_mem:
                                continue
                        filtered_mems.append(m)
                    for m in filtered_mems[-5:]: # Last 5 filtered memories
                        history_str += f"<|im_start|>user\n{m['query']}<|im_end|>\n<|im_start|>assistant\n{m['sql']}<|im_end|>\n"
        except:
            pass

        system_prompt = f"""You are a strictly Read-Only SQLite code generator.
System Identity and Rules:
{manifest}
Generate a SELECT query based on the user's request.

Rules:
- CRITICAL: YOU MUST USE THE EXACT TABLE NAME AND COLUMNS DEFINED IN THE MANIFEST. THE TABLE IS records AND THE CITY COLUMN IS city_name. THE AQI COLUMN IS aqi_value (NOT aqi). DO NOT INVENT TABLES LIKE cities.
- ALWAYS use `SELECT * FROM records` to ensure all columns (like timestamp) are included in the results. Do NOT select specific columns.
- Handle relative time periods in the WHERE clause using SQLite date functions:
  - "yesterday": timestamp >= date('now', '-1 day') AND timestamp < date('now')
  - "last week" or "past week": timestamp >= date('now', '-7 days')
  - "this month": timestamp >= date('now', 'start of month')
- Return ONLY the raw SQL query.
- DO NOT wrap the output in markdown block quotes (e.g. no ```sql).
- DO NOT provide any explanations.
- ONLY return the SQL statement."""

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n{history_str}<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"

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
            
            sql_query = sql_query.strip()

            # SMART SOLUTION: Force SELECT * if the stubborn 0.5B model forgets the timestamp
            import re
            query_upper = sql_query.upper()
            if sql_query.upper().startswith("SELECT") and " FROM " in query_upper:
                if "*" not in sql_query and "TIMESTAMP" not in query_upper:
                    # Only override if it's a simple query without aggregations
                    if not any(agg in query_upper for agg in ["MAX(", "MIN(", "SUM(", "AVG(", "COUNT(", "GROUP BY"]):
                        sql_query = re.sub(r'(?i)^SELECT\s+.*?\s+FROM', 'SELECT * FROM', sql_query)

            return sql_query
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return ""


    def parse_intent(self, user_prompt: str) -> dict:
        self._ensure_model_loaded()
        if not self.llm:
            return {"intent": "unknown", "status": "incomplete", "ask_user": "AI engine offline."}

        import datetime
        import json
        today_dt = datetime.date.today()
        today = today_dt.isoformat()
        yesterday = (today_dt - datetime.timedelta(days=1)).isoformat()
        seven_days_ago = (today_dt - datetime.timedelta(days=7)).isoformat()

        manifest = ""
        try:
            with open(os.path.join(BASE_DIR, "ailo_manifest.yaml"), "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."

        system_prompt = f"""{manifest}
You are AILO, the Intent Router for the System.
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
    "source": "api" | "csv" | null,
    "delete_all": true | false,
    "menu_target": string | null
  }},
  "status": "complete" | "incomplete",
  "missing_slot": string | null,
  "ask_user": string | null
}}

Guidelines:
- "query": Reading, viewing, or searching existing database records (e.g. "what is...", "show...", "get..."). DO NOT extract dates or sources. Only extract "city" if specified. All other parameter fields MUST be null or false.
- "insert": Manually adding/entering a new record, city, and its AQI value to the database. The input will typically contain words like "enter", "insert", "add", "record", "save" along with a city and/or AQI value. You must extract the "city", "aqi" (as a float), and "date" (resolved relative to {today} if yesterday/today/etc. is mentioned).
- "fetch_data": Downloading new/external bulk data from an API or CSV file.
- Automatically calculate start_date and end_date based on today's date ({today}) when translating relative times like "last week" (7 days ago to today) ONLY for fetch_data and delete.

Examples:

User: "What is last week london aqi data"
Result:
{{
  "intent": "query",
  "parameters": {{
    "city": "london",
    "aqi": null,
    "date": null,
    "start_date": null,
    "end_date": null,
    "url": null,
    "source": null,
    "delete_all": false,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}

User: "show the highest record for Berlin"
Result:
{{
  "intent": "query",
  "parameters": {{
    "city": "berlin",
    "aqi": null,
    "date": null,
    "start_date": null,
    "end_date": null,
    "url": null,
    "source": null,
    "delete_all": false,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}

User: "Enter data foramsterdam yesterdays aqi value 5.8"
Result:
{{
  "intent": "insert",
  "parameters": {{
    "city": "amsterdam",
    "aqi": 5.8,
    "date": "{yesterday}",
    "start_date": null,
    "end_date": null,
    "url": null,
    "source": null,
    "delete_all": false,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}

User: "add records for Paris aqi 45"
Result:
{{
  "intent": "insert",
  "parameters": {{
    "city": "paris",
    "aqi": 45.0,
    "date": null,
    "start_date": null,
    "end_date": null,
    "url": null,
    "source": null,
    "delete_all": false,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}

User: "download last week aqi for Tokyo"
Result:
{{
  "intent": "fetch_data",
  "parameters": {{
    "city": "tokyo",
    "aqi": null,
    "date": null,
    "start_date": "{seven_days_ago}",
    "end_date": "{today}",
    "url": null,
    "source": "api",
    "delete_all": false,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}

User: "delete records for Rome yesterday"
Result:
{{
  "intent": "delete",
  "parameters": {{
    "city": "rome",
    "aqi": null,
    "date": "{yesterday}",
    "start_date": null,
    "end_date": null,
    "url": null,
    "source": null,
    "delete_all": false,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}

User: "delete all records"
Result:
{{
  "intent": "delete",
  "parameters": {{
    "city": null,
    "aqi": null,
    "date": null,
    "start_date": null,
    "end_date": null,
    "url": null,
    "source": null,
    "delete_all": true,
    "menu_target": null
  }},
  "status": "complete",
  "missing_slot": null,
  "ask_user": null
}}
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

    def ai_oracle_fallback(self, user_prompt: str, bad_sql: str, sqlite_error: str) -> tuple[str, str]:
        import google.generativeai as genai
        import json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "", "Gemini API key is missing."

        try:
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash as the fast oracle
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""Şema:
table: records
columns: id (INTEGER PRIMARY KEY), city_name (TEXT), aqi_value (REAL), timestamp (TEXT)

Kullanıcı Sorusu: {user_prompt}
Yerel modelin ürettiği bozuk SQL: {bad_sql}
SQLite Hatası: {sqlite_error}

Bozuk SQL'i düzelt ve sebebini açıkla.
Lütfen sadece aşağıdaki JSON formatında yanıt ver (markdown vb. kullanma):
{{
  "fixed_sql": "DÜZELTİLMİŞ SQL BURAYA",
  "explanation": "Hatayı nasıl düzelttiğini anlatan kısa açıklama"
}}"""

            response = model.generate_content(prompt)
            output_text = response.text.strip()

            # Cleanup markdown if model hallucinates it
            if output_text.startswith("```json"):
                output_text = output_text[7:]
            if output_text.startswith("```"):
                output_text = output_text[3:]
            if output_text.endswith("```"):
                output_text = output_text[:-3]
            
            data = json.loads(output_text.strip())
            return data.get("fixed_sql", "").strip(), data.get("explanation", "Gemini fixed the query autonomously.")
        except Exception as e:
            print(f"Oracle fallback error: {e}")
            return "", f"Oracle fallback error: {str(e)}"


    def is_memory_duplicate(self, new_query: str, new_sql: str) -> bool:
        import json
        import difflib
        try:
            with open(os.path.join(BASE_DIR, "ai_memory.json"), "r") as f:
                mem_data = json.load(f)

            for m in mem_data:
                if m.get('sql', '').strip().upper() == new_sql.strip().upper():
                    return True

                ratio = difflib.SequenceMatcher(None, m.get('query', '').lower(), new_query.lower()).ratio()
                if ratio > 0.85:
                    return True
            return False
        except:
            return False

    def save_to_memory(self, new_query: str, new_sql: str) -> bool:
        import json
        if self.is_memory_duplicate(new_query, new_sql):
            return False

        memories = []
        try:
            with open(os.path.join(BASE_DIR, "ai_memory.json"), "r") as f:
                memories = json.load(f)
        except:
            pass

        memories.append({"query": new_query, "sql": new_sql})
        try:
            with open(os.path.join(BASE_DIR, "ai_memory.json"), "w") as f:
                json.dump(memories, f, indent=4)
            return True
        except:
            return False

    def generate_training_questions(self, topic: str, count: int) -> list:
        import google.generativeai as genai
        import json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return []

        manifest = ""
        try:
            with open(os.path.join(BASE_DIR, "ailo_manifest.yaml"), "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

            prompt = f"""{manifest}

You are the Teacher for the AILO system. Generate exactly {count} natural language questions to train the Text-to-SQL engine.
The user requested the topic: '{topic}'.
CRITICAL GUARDRAIL: If the topic is completely irrelevant to air quality or the database schema (e.g., cooking, games, nonsense), you MUST forcefully pivot the topic to an air quality context (e.g., 'impact of restaurants on air pollution') or simply generate standard AQI and city-based queries. Never step outside the schema bounds.
Return a valid JSON array of strings containing the questions. Example: ["question 1", "question 2"]"""

            response = model.generate_content(prompt)
            data = json.loads(response.text.strip())
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
