import asyncio
from tui_engine import TUIEngine
from async_executor import ailo_executor
from src.intent.cascade_guard import cascade_guard
from src.tools.db_executor import DatabaseExecutor
from rich.table import Table
from rich import box

# --- SPRINT 5 EKLENTİLERİ ---
from src.tools.db_executor import DatabaseExecutor
from rich.table import Table
from rich.console import Console

class AILOMasterEngine:
    """
    The asynchronous backbone of the AILO interface.
    Manages the Zero-UI prompt loop and background task dispatches.
    """
    def __init__(self):
        self.tui = TUIEngine()
        self.is_running = True

    async def process_command(self, command: str):
        """Routes the command through the 4-Layer Cascade Guard asynchronously."""
        # Visual feedback
        self.tui.print_system_message(f"Analyzing intent via Cascade Guard...")

        # Execute the cascade guard parsing which handles the 4 layers.
        # It's an async function and manages background execution internally for Layer 4.
        # But we still print the "Thinking..." indicator before Layer 4 gets hit if possible.
        # Actually, since we don't know if it hits Layer 4 until inside `classify`,
        # but to satisfy the requirement: we print it before awaiting `classify`.
        self.tui.print_system_message("[AILO] 🧠 Complex query detected. Deep thinking in background...")

        result = await cascade_guard.classify(command)

        if isinstance(result, dict):
            # It came from Layer 4 LLM fallback JSON
            intent = result.get("intent", "llm_chat")
            response = result.get("response", "")
            error = result.get("error", "")

            if error:
                self.tui.print_system_message(f"LLM generated invalid format: {error}", level="error")
                # Attempt to dump raw text if available
                raw_text = result.get("raw_text", "")
                if raw_text:
                    self.tui.print_system_message(f"Raw Output: {raw_text}")
            elif response:
                # Let AILO speak directly!
                self.tui.print_system_message(f"🧠 Brain: {response}")

            self.tui.print_system_message(f"Intent resolved via LLM: [{intent.upper()}]")
        elif result == "UNKNOWN":
            self.tui.print_system_message("Cascade Guard exhausted. LLM Fallback unavailable.", level="error")
        elif result == "query":
            self.tui.print_system_message(f"Intent resolved rapidly: [QUERY]")
            # Step A: Non-blocking log
            self.tui.print_system_message("Generating SQL for database...", level="system")

            # Step B: LLM generation in background
            if cascade_guard.engine:
                prompt = f"Convert this text to a SQL read query for the table 'air_quality' (id, timestamp, location, aqi_level, temperature): '{command}'"
                sql_query = await ailo_executor.run_in_background(cascade_guard.engine.generate_sql, prompt)

                # Step C: Execute generated SQL safely
                self.tui.print_system_message(f"Executing: {sql_query}")
                db_exec = DatabaseExecutor()
                db_result = db_exec.execute_read_query(sql_query)

                # Step D: Error Check
                if "error" in db_result:
                    self.tui.print_system_message(f"Execution Error: {db_result['error']} - {db_result.get('details', '')}", level="error")
                else:
                    # Step E: Instantiate Rich Table
                    table = Table(title="Data Results", box=box.SQUARE, show_lines=True)

                    for col in db_result.get("columns", []):
                        table.add_column(col)

                    for row in db_result.get("rows", []):
                        # Convert all tuple elements to string for rich Table API
                        table.add_row(*[str(item) for item in row])

                    # Step F: Print Rich Table natively
                    self.tui.print_rich_table(table)
            else:
                self.tui.print_system_message("LLM Engine unavailable to generate SQL.", level="error")
        else:
            self.tui.print_system_message(f"Intent resolved rapidly: [{result.upper()}]")
            
            # --- SPRINT 5 PART 2: VERİTABANI İNFAZ MOTORU ---
            if result.upper() == "QUERY":
                if not cascade_guard.engine:
                    self.tui.print_system_message("LLM Engine is unavailable. Cannot generate SQL for this query.", level="error")
                    return

                self.tui.print_system_message("Generating SQL for database...", level="system")
                try:
                    # 1. Beyinden (LLM) SQL Sorgusu İste
                    prompt = (
                        "<|im_start|>system\n"
                        "You are a SQL generator. Generate a SELECT query to retrieve the requested data.\n"
                        "Table schema:\n"
                        "CREATE TABLE air_quality (\n"
                        "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                        "    timestamp TEXT NOT NULL,\n"
                        "    location TEXT NOT NULL,\n"
                        "    aqi_level INTEGER NOT NULL,\n"
                        "    temperature REAL NOT NULL\n"
                        ")\n"
                        "Rules:\n"
                        "- ONLY filter by columns that are explicitly mentioned in the user prompt (e.g. location, aqi_level, etc.).\n"
                        "- Do NOT add timestamp filters unless the user specifies a date or time.\n"
                        "- Response must be a single SELECT query matching the schema and grammar. Do not explain.\n"
                        "<|im_end|>\n"
                        f"<|im_start|>user\n{command}\n<|im_end|>\n"
                        "<|im_start|>assistant\n"
                    )
                    sql_query = await ailo_executor.run_in_background(cascade_guard.engine.generate_sql, prompt)
                    
                    # 2. Veritabanına Bağlan ve Sorguyu Çalıştır
                    db = DatabaseExecutor()
                    db_result = db.execute_read_query(sql_query)
                    
                    # 3. Sonuçları Rich Tablosuna Çevir
                    if "error" in db_result:
                        self.tui.print_system_message(f"SQL Hata: {db_result['error']} - {db_result.get('details', '')}", level="error")
                    else:
                        table = Table(title="AILO Air Quality Data", show_header=True, header_style="bold cyan")
                        for col in db_result["columns"]:
                            table.add_column(col)
                        for row in db_result["rows"]:
                            table.add_row(*[str(item) for item in row])
                        
                        # Ekrana Bas (Jules tui_engine'i güncellemediyse diye doğrudan Console kullanıyoruz)
                        Console().print(table)
                        
                except Exception as e:
                    self.tui.print_system_message(f"Database Execution Error: {e}", level="error")

    async def pre_warm_models(self):
        """Asynchronously loads heavy AI models into RAM to prevent UI blocking."""
        import sys
        import os
        # sys.path hacking so we can import src without proper package structure
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        try:
            from src.rag.embedder import embedder
            self.tui.print_system_message("Model is loading in background...")
            # Yield to thread pool for the 10s load time
            await ailo_executor.run_in_background(embedder.load_model)
            self.tui.print_system_message("Semantic Embedder loaded successfully.", level="success")
        except Exception as e:
            self.tui.print_system_message(f"Failed to pre-warm models: {e}", level="error")

    async def run(self):
        """The core asyncio event loop powering the TUI."""
        import os
        self.tui.show_splash_screen()

        # Fire and forget the pre-warming task
        asyncio.create_task(self.pre_warm_models())

        while self.is_running:
            try:
                # Non-blocking async prompt from prompt_toolkit
                user_input = await self.tui.get_omnibar_input_async()

                if not user_input:
                    continue

                if user_input.lower() in ["/exit", "/quit"]:
                    self.tui.print_system_message("AILO shutting down. Goodbye!")
                    self.is_running = False
                    break

                # Schedule processing as a background task so we could, in theory,
                # accept multiple commands or stream tokens simultaneously.
                # However, for pure synchronous UI expectations, we just await it here.
                # The crucial part is that `await process_command` yields control to asyncio.
                await self.process_command(user_input)

            except KeyboardInterrupt:
                # Handle Ctrl+C cleanly
                self.tui.print_system_message("Action cancelled.")
                continue
            except EOFError:
                # Handle Ctrl+D
                self.tui.print_system_message("AILO shutting down. Goodbye!")
                self.is_running = False
                break

        # Clean teardown
        ailo_executor.shutdown()

if __name__ == "__main__":
    engine = AILOMasterEngine()
    # Python 3.7+ approach to running an async entry point
    asyncio.run(engine.run())
