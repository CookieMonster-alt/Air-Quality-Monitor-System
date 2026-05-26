import os

# Always resolve paths relative to this file's directory,
# regardless of the working directory the app is launched from.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        self._manifest_cache = None
        self._memory_cache = {}

    def _get_manifest(self) -> str:
        if self._manifest_cache is not None:
            return self._manifest_cache
        try:
            manifest_path = os.path.join(_BASE_DIR, "ailo_manifest.yaml")
            with open(manifest_path, "r") as f:
                self._manifest_cache = f.read()
        except:
            self._manifest_cache = "Manifest missing."
        return self._manifest_cache

    def _get_memory(self, persona: str) -> list:
        import json
        if persona in self._memory_cache:
            return self._memory_cache[persona]
        try:
            memory_path = os.path.join(_BASE_DIR, f"memory_{persona}.json")
            with open(memory_path, "r") as f:
                mem_data = json.load(f)
                self._memory_cache[persona] = mem_data
                return mem_data
        except:
            self._memory_cache[persona] = []
            return []

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

        manifest = self._get_manifest()
        memory = ""

        mem_data = self._get_memory("router")
        if mem_data:
            memory = "\nSuccessful Past Queries to Learn From:\n"
            # Hafızadan sadece son 5 başarılı deneyimi bağlama dahil ediyoruz
            for m in mem_data[-5:]:
                memory += f"Q: {m['query']}\nSQL: {m['sql']}\n\n"

        system_prompt = f"""You are a strictly Read-Only SQLite query generator for an Air Quality Monitor System.

THE ONLY VALID DATABASE SCHEMA - DO NOT USE ANY OTHER COLUMN NAMES:

TABLE: records
  - id          INTEGER PRIMARY KEY
  - city_name   TEXT
  - aqi_value   REAL    (this is the air quality value - use for highest, lowest, best, worst queries)
  - timestamp   TEXT

TABLE: predictions
  - id              INTEGER PRIMARY KEY
  - city_name       TEXT
  - predicted_aqi   REAL
  - prediction_date TEXT
  - target_date     TEXT
  - decision_made   TEXT

FORBIDDEN COLUMNS (THESE DO NOT EXIST - NEVER USE THEM):
- population, aqi, value, score, index, air_quality, pollution, quality, level, reading

RULES:
- Use ONLY the exact column names listed above. Nothing else.
- For air quality data, ALWAYS use: aqi_value
- Use COLLATE NOCASE when filtering by city_name.
- Return ONLY the raw SQL SELECT statement. No markdown. No explanation.

SYSTEM MANIFEST:
{self._get_manifest()}

{memory}
Examples:
Q: Show highest london data
SQL: SELECT city_name, aqi_value, timestamp FROM records WHERE city_name = 'London' COLLATE NOCASE ORDER BY aqi_value DESC LIMIT 10;

Q: Show me 3 highest london data
SQL: SELECT city_name, aqi_value, timestamp FROM records WHERE city_name = 'London' COLLATE NOCASE ORDER BY aqi_value DESC LIMIT 3;

Q: What is the average aqi for Manchester
SQL: SELECT city_name, AVG(aqi_value) as avg_aqi FROM records WHERE city_name = 'Manchester' COLLATE NOCASE;"""

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
        import difflib

        today = datetime.date.today().isoformat()

        manifest = self._get_manifest()

        # RAG Mimarisi: RAM'deki hafızadan en benzer 3 tecrübeyi bağlama ekleyelim
        past_experiences = ""
        memories = self._get_memory("intent")
        if memories:
            queries = [m['query'] for m in memories]
            matches = difflib.get_close_matches(user_prompt, queries, n=3, cutoff=0.1)

            if matches:
                past_experiences = "\nÖğrenilen Geçmiş Tecrübeler:\n"
                for match in matches:
                    for m in memories:
                        if m['query'] == match:
                            past_experiences += f"Kullanıcı: {m['query']}\nDoğru Çıktı: {m['sql']}\n\n"
                            break

        system_prompt = f"""You are AILO, the Intent Router for an Air Quality Monitor System.
Today's date is: {today}.
{past_experiences}

The database has these tables:
- records: id, city_name, aqi_value, timestamp
- predictions: id, city_name, predicted_aqi, prediction_date, target_date, decision_made

SYSTEM MANIFEST:
{manifest}

Analyze the user's natural language input and output ONLY a valid JSON object:
{{"intent": "query"|"insert"|"delete"|"fetch_data"|"navigate", "parameters": {{"city": string|null, "aqi": float|null, "date": string|null, "start_date": string|null, "end_date": string|null, "url": string|null, "menu_target": string|null}}, "status": "complete"|"incomplete", "missing_slot": string|null, "ask_user": string|null}}

INTENT RULES - READ CAREFULLY:
- "query": User wants to READ, SHOW, DISPLAY, VIEW, SEARCH, FIND, GET, LIST, or ANALYZE data already in the database.
  Keywords: show, display, get, find, list, what is, latest, newest, highest, lowest, average, how many, all, recent
  Examples: "show london data", "latest london data", "show me newest data for london", "what is the highest AQI", "get all records"
- "insert": User wants to ADD or RECORD new data. Keywords: add, record, save, insert, log, enter
  Examples: "add paris with aqi 45", "record london aqi 55"
- "delete": User wants to ERASE or REMOVE data. Keywords: delete, remove, clear, erase
  Examples: "delete london records"
- "fetch_data": User wants to IMPORT a CSV file. This requires a file path or URL. Keywords: import, fetch, load from file, csv
  ONLY use fetch_data if user mentions a file path or CSV. NEVER use fetch_data for show/display/list queries.
  Examples: "import data from /path/to/file.csv", "load historical csv"
- "navigate": User wants to go to a menu. Keywords: go to, open menu, admin, settings

CRITICAL: "latest", "newest", "most recent", "show", "display" are ALWAYS "query" intent. NEVER "fetch_data".

DO NOT wrap output in markdown. Return ONLY the JSON object."""

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"

        try:
            response = self.llm(
                prompt,
                max_tokens=256,
                stop=["<|im_end|>"],
                temperature=0.1
            )
            output_text = response['choices'][0]['text'].strip()

            # Markdown temizliği
            if output_text.startswith("```json"): output_text = output_text[7:]
            if output_text.startswith("```"): output_text = output_text[3:]
            if output_text.endswith("```"): output_text = output_text[:-3]

            # Burada çökme riskine karşı try-except bloğuyla json parse deniyoruz
            try:
                return json.loads(output_text.strip())
            except json.JSONDecodeError:
                # Yerel model JSON'ı bozduysa Cloud Oracle yetişip toparlasın
                return self.ai_intent_oracle_fallback(user_prompt, output_text.strip())

        except Exception as e:
            print(f"Error parsing intent: {e}")
            return {"intent": "unknown", "status": "incomplete", "ask_user": "I failed to parse your intent."}

    def summarize_data(self, df_json: str) -> str:
        self._ensure_model_loaded()
        if not self.llm:
            return "AI offline."

        system_prompt = """You are AILO-Analyst. Read the provided JSON data representing air quality records and provide a 2-3 sentence Executive Summary highlighting key statistics, extremes, or trends. Do NOT use markdown. Do not include greetings. Return only the summary text."""

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\nData:\n{df_json}<|im_end|>\n<|im_start|>assistant\n"

        try:
            response = self.llm(
                prompt,
                max_tokens=256,
                stop=["<|im_end|>"],
                temperature=0.3
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error analyzing data: {e}"

    def ai_intent_oracle_fallback(self, user_prompt: str, bad_output: str) -> dict:
        import google.generativeai as genai
        import os
        import json

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"intent": "unknown", "status": "incomplete", "ask_user": "Oracle offline."}

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""You are the intent classifier for AILO, an Air Quality Monitor System.

INTENT RULES:
- "query": User wants to READ, SHOW, DISPLAY, VIEW, SEARCH, FIND, or ANALYZE existing database data.
  Keywords: show, display, get, find, list, latest, newest, highest, lowest, average, recent, what is, how many
  CRITICAL: "latest", "newest", "show", "display" are ALWAYS "query". NEVER "fetch_data".
- "insert": User wants to ADD new data. Keywords: add, record, save, insert
- "delete": User wants to ERASE data. Keywords: delete, remove, clear
- "fetch_data": ONLY when user explicitly mentions importing a CSV file or file path. Keywords: import csv, load file
- "navigate": User wants to open a menu

The database schema:
- records table: id, city_name, aqi_value, timestamp
- predictions table: id, city_name, predicted_aqi, prediction_date, target_date, decision_made

User said: "{user_prompt}"
Local model produced invalid output: {bad_output}

Return ONLY a valid JSON object (no markdown):
{{"intent": "query"|"insert"|"delete"|"fetch_data"|"navigate", "parameters": {{"city": string|null, "aqi": float|null, "date": string|null, "start_date": string|null, "end_date": string|null, "url": string|null, "menu_target": string|null}}, "status": "complete"|"incomplete", "missing_slot": string|null, "ask_user": string|null}}"""

            response = model.generate_content(prompt)
            fixed_json_str = response.text.strip()

            if fixed_json_str.startswith("```json"): fixed_json_str = fixed_json_str[7:]
            if fixed_json_str.startswith("```"): fixed_json_str = fixed_json_str[3:]
            if fixed_json_str.endswith("```"): fixed_json_str = fixed_json_str[:-3]

            parsed_data = json.loads(fixed_json_str.strip())

            # Correct classification saved to memory so local model learns from it
            self.save_to_memory(user_prompt, json.dumps(parsed_data), persona="intent")
            return parsed_data

        except Exception as e:
            print(f"Oracle intent fallback error: {e}")
            return {"intent": "unknown", "status": "incomplete", "ask_user": "Oracle was unable to parse the intent."}

    def ai_analyst_oracle_fallback(self, data_input: str, bad_output: str) -> str:
        import google.generativeai as genai
        import os

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Oracle offline."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""Veri: {data_input}
Yerel modelin hatalı/boş özeti: {bad_output}

Lütfen bu hava kalitesi verisini okuyup 2-3 cümlelik çok şık ve net bir yönetici özeti yaz. Markdown kullanma."""

            response = model.generate_content(prompt)
            fixed_summary = response.text.strip()

            # Gelecekte aynı veride takılmaması için hafızaya kaydedelim
            self.save_to_memory(data_input, fixed_summary, persona="analyst")
            return fixed_summary
        except Exception as e:
            return f"Oracle analyst fallback error: {e}"

    def ai_teacher_audit_intent(self, user_prompt: str, local_intent_data: dict) -> tuple[dict, bool]:
        import google.generativeai as genai
        import os
        import json

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return local_intent_data, True  # Skip audit if offline

        manifest = self._get_manifest()

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""You are the Cloud Teacher Auditor for AILO.
The local model processed the user's prompt and generated an intent classification.
You must grade this classification.

SYSTEM MANIFEST AND CAPABILITIES:
{manifest}

USER PROMPT: "{user_prompt}"
LOCAL MODEL'S OUTPUT: {json.dumps(local_intent_data)}

Is the local model's output PERFECTLY correct according to the manifest rules (especially the rules about 'download', 'latest', etc.)?
If it is 100% correct, return ONLY the exact word "PASS".
If it is wrong or hallucinated, return ONLY the corrected JSON object. DO NOT include any other text or markdown."""

            response = model.generate_content(prompt)
            result_str = response.text.strip()

            if result_str == "PASS":
                return local_intent_data, True
            
            # Parse corrected JSON
            if result_str.startswith("```json"): result_str = result_str[7:]
            if result_str.startswith("```"): result_str = result_str[3:]
            if result_str.endswith("```"): result_str = result_str[:-3]

            parsed_data = json.loads(result_str.strip())
            
            # Save correction to memory so local model learns
            self.save_to_memory(user_prompt, json.dumps(parsed_data), persona="intent")
            return parsed_data, False
            
        except Exception as e:
            print(f"Teacher Audit Intent error: {e}")
            return local_intent_data, True

    def ai_teacher_audit_sql(self, user_prompt: str, local_sql: str) -> tuple[str, bool]:
        import google.generativeai as genai
        import os

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return local_sql, True  # Skip audit if offline

        manifest = self._get_manifest()

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""You are the Cloud Teacher Auditor for AILO.
The local model generated a SQLite query based on the user's prompt.
You must grade this query for logical accuracy and hallucination.

SYSTEM MANIFEST AND SCHEMA:
{manifest}

USER PROMPT: "{user_prompt}"
LOCAL MODEL'S GENERATED SQL: "{local_sql}"

RULES FOR GRADING:
1. Did the local model hallucinate a city name not in the user's prompt? (e.g. prompt says "show 3 highest", SQL says "WHERE city_name='London'").
2. Did the local model misinterpret date logic? (e.g. prompt says "last week", SQL says "LIMIT 1" instead of a date filter).
3. Is it structurally invalid?

If the SQL is 100% PERFECT and logically matches the prompt, return ONLY the exact word "PASS".
If it is flawed, return ONLY the corrected raw SQL statement. DO NOT include any other text, markdown, or explanations."""

            response = model.generate_content(prompt)
            result_str = response.text.strip()

            if result_str == "PASS":
                return local_sql, True
            
            if result_str.startswith("```sql"): result_str = result_str[6:]
            if result_str.startswith("```"): result_str = result_str[3:]
            if result_str.endswith("```"): result_str = result_str[:-3]
            
            fixed_sql = result_str.strip()
            # Save correction to memory
            self.save_to_memory(user_prompt, fixed_sql, persona="router")
            return fixed_sql, False
            
        except Exception as e:
            print(f"Teacher Audit SQL error: {e}")
            return local_sql, True

    def ai_oracle_fallback(self, user_prompt: str, bad_output: str, intent_type: str = "sql") -> str:
        # Gemini API'yi kullanarak yerel modelin takıldığı SQL komutlarını veya JSON yanıtlarını kurtarır.
        import google.generativeai as genai
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return ""

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""You are a SQLite expert for an Air Quality Monitor System.

CRITICAL - THE ONLY VALID DATABASE SCHEMA IS:

TABLE: records
  COLUMNS (EXACT NAMES, NO OTHERS EXIST):
    - id          (INTEGER PRIMARY KEY)
    - city_name   (TEXT)
    - aqi_value   (REAL)   <- Use this for AQI, air quality, pollution level, highest/lowest queries
    - timestamp   (TEXT)

TABLE: predictions
  COLUMNS (EXACT NAMES, NO OTHERS EXIST):
    - id              (INTEGER PRIMARY KEY)
    - city_name       (TEXT)
    - predicted_aqi   (REAL)
    - prediction_date (TEXT)
    - target_date     (TEXT)
    - decision_made   (TEXT)

RULES:
- There is NO column called: population, aqi, value, air_quality, pollution, score, index, or any other name.
- The ONLY column for air quality values is: aqi_value
- Always use COLLATE NOCASE when filtering by city_name.
- Only generate SELECT statements.
- Return ONLY the raw SQL query, no markdown, no explanation.

The user asked: {user_prompt}
A broken SQL was generated: {bad_output}

The broken SQL is WRONG because it uses non-existent columns. Write a correct SQL query that answers the user's question using ONLY the valid columns listed above."""

            response = model.generate_content(prompt)
            fixed_data = response.text.strip()

            # Markdown kalıntılarını süpürüyoruz
            if fixed_data.startswith("```sql"): fixed_data = fixed_data[6:]
            if fixed_data.startswith("```json"): fixed_data = fixed_data[7:]
            if fixed_data.startswith("```"): fixed_data = fixed_data[3:]
            if fixed_data.endswith("```"): fixed_data = fixed_data[:-3]

            return fixed_data.strip()
        except Exception as e:
            print(f"Oracle fallback error: {e}")
            return ""

    def is_memory_duplicate(self, new_query: str, new_sql: str, persona: str = "router") -> bool:
        import difflib

        # Sadece RAM'deki hafızaya bakıyoruz, disk I/O yapmıyoruz
        mem_data = self._get_memory(persona)

        for m in mem_data:
            if m.get('sql', '').strip().upper() == new_sql.strip().upper():
                return True

            ratio = difflib.SequenceMatcher(None, m.get('query', '').lower(), new_query.lower()).ratio()
            if ratio > 0.85:
                return True
        return False

    def save_to_memory(self, new_query: str, new_sql: str, persona: str = "router") -> bool:
        import json
        if self.is_memory_duplicate(new_query, new_sql, persona):
            return False

        memories = self._get_memory(persona)
        memories.append({"query": new_query, "sql": new_sql})
        self._memory_cache[persona] = memories

        memory_path = os.path.join(_BASE_DIR, f"memory_{persona}.json")
        try:
            with open(memory_path, "w") as f:
                json.dump(memories, f, indent=4)
            return True
        except Exception as e:
            print(f"[AILO Memory] Warning: could not save memory to {memory_path}: {e}")
            return False

    def generate_training_questions(self, topic: str, count: int, department: str = "sql") -> list:
        import google.generativeai as genai
        import json
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return []

        manifest = ""
        try:
            manifest_path = os.path.join(_BASE_DIR, "ailo_manifest.yaml")
            with open(manifest_path, "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

            if department == "niyet":
                task_desc = "Kullanıcıların niyet çözücüye (Intent Parser) sorabileceği doğal dilde komutlar üret (örneğin: 'son 3 günün verisini sil', 'parisi 45 aqi ile ekle', 'londra verilerini getir')."
            elif department == "analist":
                task_desc = "Bir analistin özetlemesi için içinde 'city_name', 'aqi_value', 'timestamp' olan sahte JSON formatında küçük hava kalitesi verileri üret. Her soru bir JSON string olmalı."
            else:
                task_desc = "Yerel modelin SQL (Text-to-SQL) becerilerini test etmek için karmaşık SQL gerektiren doğal dil soruları üret."

            prompt = f"""{manifest}

Sen AILO sisteminin eğitimcisisin. Sadece bu manifestodaki şemaya uygun {count} adet soru/girdi üret.
Kullanıcının seçtiği konu: {topic}.
Görev: {task_desc}

DİKKAT: Eğer bu konu hava kalitesi veya veritabanı şemamızla tamamen alakasızsa (Örn: yemek tarifi, oyun vb.), konuyu ZORLA hava kalitesi bağlamına çevir. Asla şema dışına çıkma.
Sadece JSON dizisi (array of strings) döndür. Örnek: ["soru 1", "soru 2"]"""

            response = model.generate_content(prompt)
            data = json.loads(response.text.strip())
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
