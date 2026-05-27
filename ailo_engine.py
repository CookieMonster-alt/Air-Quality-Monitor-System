import asyncio
from tui_engine import TUIEngine
from async_executor import ailo_executor

class AILOMasterEngine:
    """
    The asynchronous backbone of the AILO interface.
    Manages the Zero-UI prompt loop and background task dispatches.
    """
    def __init__(self):
        self.tui = TUIEngine()
        self.is_running = True

    async def process_command(self, command: str):
        """Simulate sending the command to the background executor."""
        # Visual feedback during the wait
        self.tui.print_system_message(f"Processing command: '{command}' in background...")

        # Dispatch dummy heavy load to thread pool
        import time
        def dummy_heavy_load():
            time.sleep(2)
            return f"Result payload for '{command}'"

        result = await ailo_executor.run_in_background(dummy_heavy_load)

        # Return cleanly back to TUI stream
        self.tui.print_system_message(f"Success: {result}")

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
