import asyncio
import time
import io
import shutil
import sys
import os
import re

from rich.console import Console
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, FloatContainer, Float
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout import Layout as PTLayout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.completion import WordCompleter

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Ensure path works
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Bizim kütüphanelerimiz
from src.tui.theme import AILO_THEME
from src.tui.layout import create_ailo_layout
from src.tui.components import (
    SystemStats, AQIReading, ModelStats, IntentLayerStatus, ConversationMessage,
    build_header, build_left_sidebar, build_right_sidebar, build_conversation_area
)

# Backend entegrasyonu
from src.intent.cascade_guard import cascade_guard
from src.tools.db_executor import DatabaseExecutor
from async_executor import ailo_executor

# --- 1. MERKEZİ DURUM (STATE) YÖNETİMİ ---
start_time = time.time()
state = {
    "sys_stats": SystemStats(cpu_percent=0.0, mem_percent=0.0, mem_used_gb=0.0, temp_celsius=45.0, uptime_seconds=0, disk_percent=0.0),
    "aqi_reading": AQIReading(pm25=12.5, pm10=14.0, o3=0.04, no2=0.01, co=0.8, timestamp=time.time()),
    "model_stats": ModelStats(model_name="Qwen2.5-1.5B", tokens_generated=0, tokens_per_second=0.0, cache_hit_rate=0.0, total_inferences=0),
    "intent_status": IntentLayerStatus(layer_name="Init", latency_ms=0.0, intent="START", confidence=1.0, is_fallback=False),
    "messages": [
        ConversationMessage(role="ailo", content="AILO Brain Integration Complete. Ready for queries.", timestamp=time.time(), intent="SYS", persona="Core", layer_used="Kernel", confidence=1.0)
    ],
    "scroll_offset": 0
}

# --- 2. ANSI BRIDGE GÖRSELLEŞTİRME MOTORU ---
def get_rendered_layout():
    """Rich layout'u arka planda çizer ve Prompt_Toolkit'e uygun ANSI string'e dönüştürür."""
    cols, rows = shutil.get_terminal_size()
    
    avail_height = max(1, rows - 7)
    avail_width = max(10, cols - 56)
    
    layout = create_ailo_layout()
    
    # Header & Conversation are direct leaf nodes
    layout["header"].update(build_header(state["sys_stats"]))
    layout["conversation"].update(build_conversation_area(state["messages"], state.get("scroll_offset", 0), avail_height, avail_width))
    
    # Left Sidebar: Extract the rendered panels from the Layout object
    left_layout = build_left_sidebar(state["sys_stats"], state["aqi_reading"])
    layout["sys_stats"].update(left_layout["sys_panel"].renderable)
    layout["aqi_readings"].update(left_layout["aqi_panel"].renderable)
    
    # Right Sidebar: Extract the rendered panels from the Layout object
    right_layout = build_right_sidebar(state["model_stats"], state["intent_status"])
    layout["model_stats"].update(right_layout["model_panel"].renderable)
    layout["intent_layer"].update(right_layout["intent_panel"].renderable)

    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, theme=AILO_THEME, width=cols, height=rows - 2)
    console.print(layout)
    return ANSI(string_io.getvalue())

# --- 3. ARKA PLAN GÖREVİ (SYSTEM MONITOR & WORKER) ---
async def background_worker(app):
    """Klavye girişini ASLA bloklamayan, sistem verilerini güncelleyen arka plan döngüsü."""
    while True:
        await asyncio.sleep(2.0)
        
        state["sys_stats"].uptime_seconds = int(time.time() - start_time)
        
        if PSUTIL_AVAILABLE:
            state["sys_stats"].cpu_percent = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            state["sys_stats"].mem_percent = mem.percent
            state["sys_stats"].mem_used_gb = mem.used / (1024 ** 3)
            try:
                state["sys_stats"].disk_percent = psutil.disk_usage('/').percent
            except Exception:
                pass
        else:
            state["sys_stats"].cpu_percent = (state["sys_stats"].cpu_percent + 7.5) % 100
        
        app.invalidate()

# --- 4. ASENKRON BEYİN ENTEGRASYONU ---
async def process_query(app, text):
    """Kullanıcı sorgusunu arka planda işleyen fonksiyon."""
    t0 = time.time()
    
    # 1. CASCADE GUARD İLE NİYET ANALİZİ
    intent_result = await cascade_guard.classify(text)
    latency_ms = (time.time() - t0) * 1000
    
    if isinstance(intent_result, dict):
        # LLM Fallback (Layer 4)
        layer = "LLM Fallback"
        intent = intent_result.get("intent", "llm_chat").upper()
        confidence = 0.9
        is_fallback = True
        response_text = intent_result.get("response", "")
        if intent_result.get("error"):
            response_text = f"[Hata] {intent_result.get('error')}"
    else:
        # Layer 1-3
        layer = "Cascade Guard"
        intent = str(intent_result).upper()
        confidence = 0.98
        is_fallback = False
        response_text = f"Niyet başarıyla çözümlendi: {intent}"

    state["intent_status"] = IntentLayerStatus(layer_name=layer, latency_ms=latency_ms, intent=intent, confidence=confidence, is_fallback=is_fallback)
    app.invalidate()
    
    # 2. VERİTABANI VE SQL ÜRETİMİ (Eğer niyet QUERY ise)
    if intent == "QUERY":
        if not cascade_guard.engine:
            state["messages"].append(ConversationMessage(role="ailo", content="LLM Motoru yüklenmedi. SQL sorgusu üretilemiyor.", timestamp=time.time(), intent="ERROR"))
            app.invalidate()
            return

        state["messages"].append(ConversationMessage(role="ailo", content="Veritabanı için SQL üretiliyor...", timestamp=time.time(), intent="SYS"))
        app.invalidate()
        
        # SQL Üretimi
        t_gen_start = time.time()
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
            f"<|im_start|>user\n{text}\n<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        
        sql_query = await ailo_executor.run_in_background(cascade_guard.engine.generate_sql, prompt)
        t_gen_time = time.time() - t_gen_start
        
        # Model İstatistiklerini Güncelle
        tokens = len(sql_query) // 4
        state["model_stats"].tokens_generated += tokens
        if t_gen_time > 0:
            state["model_stats"].tokens_per_second = tokens / t_gen_time
        state["model_stats"].total_inferences += 1
        
        # Veritabanını Çalıştır
        db = DatabaseExecutor()
        db_result = db.execute_read_query(sql_query)
        
        if "error" in db_result:
            content = f"SQL Hata: {db_result['error']} - {db_result.get('details', '')}"
        else:
            lines = [f"[bold cyan]Executed:[/] {sql_query}"]
            cols = db_result.get("columns", [])
            lines.append(" | ".join([f"[bold]{c}[/]" for c in cols]))
            lines.append("-" * 40)
            for row in db_result.get("rows", []):
                lines.append(" | ".join([str(item) for item in row]))
            content = "\n".join(lines)
            
        state["messages"].append(ConversationMessage(role="ailo", content=content, timestamp=time.time(), intent="RESULT"))
        if len(state["messages"]) > 50:
            state["messages"] = state["messages"][-50:]
        
    elif intent != "QUERY" and response_text:
        state["messages"].append(ConversationMessage(role="ailo", content=response_text, timestamp=time.time(), intent=intent))
        if len(state["messages"]) > 50:
            state["messages"] = state["messages"][-50:]

    app.invalidate()

# --- 5. ANA ASENKRON UYGULAMA (PROMPT_TOOLKIT) ---
def main():
    command_completer = WordCompleter(
        ['/router', '/analyst', '/visualize', '/chat', '/quit', '/exit'],
        ignore_case=True,
        pattern=re.compile(r'[a-zA-Z0-9_/]+')
    )
    
    input_field = TextArea(
        height=1,
        prompt=' [AILO] ❯ ',
        style='class:input-field',
        multiline=False,
        completer=command_completer,
        complete_while_typing=True
    )

    def accept(buff):
        text = input_field.text
        if not text.strip():
            return
        
        if text.lower() in ["/quit", "/exit"]:
            app.exit()
            return
        
        # Mesajı listeye ekle
        state["messages"].append(ConversationMessage(role="user", content=text, timestamp=time.time()))
        if len(state["messages"]) > 50:
            state["messages"] = state["messages"][-50:]
            
        state["scroll_offset"] = 0
        input_field.text = "" # Satırı temizle
        
        # Arka planda AILO beyin fonksiyonunu çağır
        state["intent_status"].intent = "THINKING..."
        state["intent_status"].latency_ms = 0.0
        app.invalidate()
        
        asyncio.create_task(process_query(app, text))

    input_field.accept_handler = accept

    kb = KeyBindings()
    @kb.add("c-c")
    def _(event):
        event.app.exit()
        
    @kb.add("up")
    def _(event):
        state["scroll_offset"] += 1
        app.invalidate()
        
    @kb.add("down")
    def _(event):
        state["scroll_offset"] = max(0, state["scroll_offset"] - 1)
        app.invalidate()
        
    @kb.add("pageup")
    def _(event):
        state["scroll_offset"] += 10
        app.invalidate()
        
    @kb.add("pagedown")
    def _(event):
        state["scroll_offset"] = max(0, state["scroll_offset"] - 10)
        app.invalidate()

    root_container = HSplit([
        Window(content=FormattedTextControl(text=get_rendered_layout)),
        Window(height=1, char='─', style='class:line'),
        input_field
    ])

    # Wrap the root container in a FloatContainer to render the popup menu
    layout_with_menus = FloatContainer(
        content=root_container,
        floats=[
            Float(xcursor=True, ycursor=True, content=CompletionsMenu(max_height=10, scroll_offset=1))
        ]
    )

    app = Application(
        layout=PTLayout(layout_with_menus),
        key_bindings=kb,
        full_screen=True
    )

    loop = asyncio.get_event_loop()
    loop.create_task(background_worker(app))
    
    try:
        loop.run_until_complete(app.run_async())
    except KeyboardInterrupt:
        pass
    
    ailo_executor.shutdown()
    print("\n[AILO] Güvenli Çıkış (Graceful Shutdown) Başarılı. Kontrol Merkezi Kapatıldı.")

if __name__ == "__main__":
    main()