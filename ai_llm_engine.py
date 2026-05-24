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

        import json
        manifest = ""
        memory = ""
        try:
            with open("ailo_manifest.yaml", "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."

        try:
            with open("memory_router.json", "r") as f:
                mem_data = json.load(f)
                if mem_data:
                    memory = "\nSuccessful Past Queries to Learn From:\n"
                    for m in mem_data[-5:]: # Last 5 memories
                        memory += f"Q: {m['query']}\nSQL: {m['sql']}\n\n"
        except:
            pass

        system_prompt = f"""You are a strictly Read-Only SQLite code generator.
System Identity and Rules:
{manifest}
{memory}
Generate a SELECT query based on the user's request.
CRITICAL: YOU MUST USE THE EXACT TABLE NAME AND COLUMNS DEFINED IN THE MANIFEST. THE TABLE IS records AND THE CITY COLUMN IS city_name. DO NOT INVENT TABLES LIKE cities.
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
        import difflib

        today = datetime.date.today().isoformat()

        manifest = ""
        try:
            with open("ailo_manifest.yaml", "r") as f:
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
- "fetch_data": User wants to fetch or download historical data. This ALWAYS requires 'url' (the file path to the CSV). If 'url', 'start_date', or 'end_date' are missing, you MUST set status to 'incomplete', specify the missing_slot, and ask for it in 'ask_user'.
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
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = f"""Kullanıcı cümlesi: {user_prompt}
Yerel modelin ürettiği hatalı çıktı: {bad_output}

Lütfen bu cümleyi sistem manifestomuza uygun olarak analiz et ve SADECE geçerli bir JSON objesi döndür.
Beklenen alanlar: intent, parameters (city, aqi, vb.), status, missing_slot, ask_user.
Hiçbir ek açıklama yapma."""

            response = model.generate_content(prompt)
            fixed_json_str = response.text.strip()

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

    def ai_analyst_oracle_fallback(self, data_input: str, bad_output: str) -> str:
        import google.generativeai as genai
        import os

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Oracle offline."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

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

    def is_memory_duplicate(self, new_query: str, new_sql: str, persona: str = "router") -> bool:
        import json
        import difflib
        filename = f"memory_{persona}.json"
        try:
            with open(filename, "r") as f:
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

    def save_to_memory(self, new_query: str, new_sql: str, persona: str = "router") -> bool:
        import json
        if self.is_memory_duplicate(new_query, new_sql, persona):
            return False

        filename = f"memory_{persona}.json"
        memories = []
        try:
            with open(filename, "r") as f:
                memories = json.load(f)
        except:
            pass

        memories.append({"query": new_query, "sql": new_sql})
        try:
            with open(filename, "w") as f:
                json.dump(memories, f, indent=4)
            return True
        except:
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
            with open("ailo_manifest.yaml", "r") as f:
                manifest = f.read()
        except:
            manifest = "Manifest missing."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

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
