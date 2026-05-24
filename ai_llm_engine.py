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

            with open("memory_router.json", "r") as f:

            with open(os.path.join(BASE_DIR, "ai_memory.json"), "r") as f:
main
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

    def explain_sql(self, sql_query: str) -> str:
        self._ensure_model_loaded()
        if not self.llm:
            return "AI engine offline."
            
        system_prompt = "You are a helpful data assistant. Explain the following SQL query in one short, simple natural language sentence so a non-technical user can understand it."
        user_prompt = f"Explain this SQL query:\n{sql_query}"
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        try:
            response = self.llm(
                prompt,
                max_tokens=80,
                stop=["<|im_end|>"],
                temperature=0.3
            )
            explanation = response['choices'][0]['text'].strip()
            return explanation
        except Exception as e:
            return "Could not generate explanation."


    def parse_intent(self, user_prompt: str) -> dict:
        self._ensure_model_loaded()
        if not self.llm:
            return {"intent": "unknown", "status": "incomplete", "ask_user": "AI engine offline."}

        import datetime
        import json

        import difflib

        today = datetime.date.today().isoformat()

        today_dt = datetime.date.today()
        today = today_dt.isoformat()
        yesterday = (today_dt - datetime.timedelta(days=1)).isoformat()
        seven_days_ago = (today_dt - datetime.timedelta(days=7)).isoformat()
main

        manifest = ""
        try:
            with open(os.path.join(BASE_DIR, "ailo_manifest.yaml"), "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."


        # RAG Mimarisi: Geçmişte yaşadığımız tecrübelerden en benzer 3 tanesini bulup bağlama ekleyelim.
        past_experiences = ""
        try:
            with open("memory_intent.json", "r") as f:
                memories = json.load(f)

            if memories:
                queries = [m['query'] for m in memories]
                # En çok benzeyen 3 sorguyu yakalayalım
                matches = difflib.get_close_matches(user_prompt, queries, n=3, cutoff=0.1)

                if matches:
                    past_experiences = "\nÖğrenilen Geçmiş Tecrübeler:\n"
                    for match in matches:
                        for m in memories:
                            if m['query'] == match:
                                past_experiences += f"Kullanıcı: {m['query']}\nDoğru Çıktı: {m['sql']}\n\n"
                                break
        except Exception:

        intent_memories_str = ""
        try:
            with open(os.path.join(BASE_DIR, "ai_intent_memory.json"), "r") as f:
                memories = json.load(f)
                for mem in memories[-5:]:
                    intent_memories_str += f"\nUser: \"{mem['query']}\"\nResult:\n{json.dumps(mem['json'], indent=2)}\n"
        except:
main
            pass

        system_prompt = f"""{manifest}
You are AILO, the Intent Router for the System.
Today's date is: {today}.
{past_experiences}

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
- "query": Reading, viewing, calculating, or searching existing database records (e.g. "what is...", "show...", "get...", "mean", "average"). DO NOT extract dates or sources for query. Only extract "city" if specified. All other parameter fields MUST be null or false.
- "insert": Manually adding/entering a new record, city, and its AQI value to the database. The input will typically contain words like "enter", "insert", "add", "record", "save" along with a city and/or AQI value. You must extract the "city", "aqi" (as a float), and "date" (resolved relative to {today} if yesterday/today/etc. is mentioned).
- "fetch_data": Downloading new/external bulk data from an API or CSV file. DO NOT use this for answering questions like "what is" or "show".
- Automatically calculate start_date and end_date based on today's date ({today}) when translating relative times like "last week" (7 days ago to today) ONLY for fetch_data and delete.

Examples:

User: "What is mean value for last week?"
Result:
{{
  "intent": "query",
  "parameters": {{
    "city": null,
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
{intent_memories_str}
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

    def ai_oracle_fallback(self, user_prompt: str, bad_sql: str, sqlite_error: str) -> tuple[str, str]:
        import google.generativeai as genai
        import json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "", "Gemini API key is missing."
main

        try:
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash as the fast oracle
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""Kullanıcı cümlesi: {user_prompt}
Yerel modelin ürettiği hatalı çıktı: {bad_output}


Lütfen bu cümleyi sistem manifestomuza uygun olarak analiz et ve SADECE geçerli bir JSON objesi döndür.
Beklenen alanlar: intent, parameters (city, aqi, vb.), status, missing_slot, ask_user.
Hiçbir ek açıklama yapma."""

            response = model.generate_content(prompt)
            fixed_json_str = response.text.strip()

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
main

            if fixed_json_str.startswith("```json"): fixed_json_str = fixed_json_str[7:]
            if fixed_json_str.startswith("```"): fixed_json_str = fixed_json_str[3:]
            if fixed_json_str.endswith("```"): fixed_json_str = fixed_json_str[:-3]

            parsed_data = json.loads(fixed_json_str.strip())


            # Hatayı düzeltmeyi başardık, bunu hafızaya kazıyalım ki bir daha yaşanmasın.
            self.save_to_memory(user_prompt, json.dumps(parsed_data), persona="intent")
            return parsed_data

        except Exception as e:
            print(f"Oracle intent fallback error: {e}")
            return {"intent": "unknown", "status": "incomplete", "ask_user": "Oracle was unable to parse the intent."}

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
main

    def ai_analyst_oracle_fallback(self, data_input: str, bad_output: str) -> str:
        import google.generativeai as genai
        import os

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:

            return "Oracle offline."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

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
main

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

            print(f"Error generating questions: {e}")
            return []

    def ai_oracle_intent_fallback(self, user_prompt: str) -> tuple[dict, str]:
        import google.generativeai as genai
        import json
        import datetime
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"intent": "unknown", "status": "incomplete", "ask_user": "Gemini API key missing."}, "Gemini API key missing."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            today = datetime.date.today().isoformat()
            
            prompt = f"""You are the Cloud Oracle for Intent Parsing. The local model failed to parse this user prompt:
"{user_prompt}"

Return a valid JSON object matching the required schema and an explanation string.
Return EXACTLY this JSON structure, nothing else:
{{
  "json_output": {{
    "intent": "query" | "insert" | "delete" | "fetch_data" | "navigate",
    "parameters": {{ ... }},
    "status": "complete",
    "missing_slot": null,
    "ask_user": null
  }},
  "explanation": "Why the local model might have failed and how you resolved it."
}}
Today's date is {today}.
"""
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            
            data = json.loads(text.strip())
            return data.get("json_output", {}), data.get("explanation", "Parsed via Gemini.")
        except Exception as e:
            return {"intent": "unknown", "status": "incomplete", "ask_user": f"Oracle error: {e}"}, str(e)

    def save_intent_memory(self, user_prompt: str, intent_json: dict) -> bool:
        import json
        memory_file = os.path.join(BASE_DIR, "ai_intent_memory.json")
        memories = []
        try:
            with open(memory_file, "r") as f:
                loaded = json.load(f)
                if isinstance(loaded, list): memories = loaded
        except:
            pass
            
        for m in memories:
            if m.get("query") == user_prompt:
                return False
                
        memories.append({"query": user_prompt, "json": intent_json})
        
        try:
            with open(memory_file, "w") as f:
                json.dump(memories, f, indent=4)
            return True
        except:
            return False
main
