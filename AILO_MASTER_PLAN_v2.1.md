# AILO GSD Master Planı: "AEGIS Boru Hattı" v2.1

**Proje:** AILO (AI Local Operator)
**Ortam:** Raspberry Pi 5 (8GB RAM) | SQLite | prompt_toolkit TUI
**Metodoloji:** GSD (Get Shit Done)
**Hazırlayan:** MiniMax Agent Sistem Mimarisi Danışmanı
**Tarih:** 2026-05-26
**Versiyon:** 2.1 (Şelale Mimarisi - Kritik Hata Düzeltmeleri)

---

## Ön Gereksinimler ve Teknik Kısıtlamalar

Bu planda verilen tüm görevler aşağıdaki fiziksel ve yazılımsal kısıtlamalar altında çalışmak ZORUNDADIR:

1. **RAM Tüketimi:** Maksimum 2GB (TUI + Model + RAG + Sistem OS dahil)
2. **Threading:** prompt_toolkit TUI thread'i KESİNLİKLE bloklanamaz. Tüm I/O işlemleri AsyncIO/ThreadPoolExecutor üzerinden çalışmalı.
3. **SQLite Kilitleri:** `WAL mode` ve `check_same_thread=False` zorunlu. YAZMA işlemleri her zaman `begin immediate` transaction ile yapılmalı.
4. **Latency:** Niyet sınıflandırma < 200ms total (tüm katmanlar dahil). Model inference > 10 token/sn.
5. **Dil Kuralı (CRITICAL):** Tüm kod, kurallar, eğitim verileri ve dokümantasyon KESİNLİKLE İNGİLİZCE'dir. Sistem prompt'ları, RAG içerikleri, Regex kuralları dahil. (Tek istisna: Kullanıcı arayüzü metinleri.)

---

## 🚨 KRİTİK HATA DÜZELTİLERİ

### 🔧 DÜZELTME 1: LinearSVC → LogisticRegression

**Problem:** `sklearn.svm.LinearSVC` sınıfının `predict_proba()` metodu **YOKTUR**!

**Düzeltme:**
- **Sprint 1.1'de** `LinearSVC` yerine `LogisticRegression` kullanılacak
- **Neden?**
  - `LogisticRegression` doğrudan olasılık tahmini sunar
  - Daha hızlı eğitim ve tahmin
  - Pi 5'in RAM'ini daha az kullanır
- **Avantaj:** 15ms'de %80+ accuracy ile çalışır

### 🔧 DÜZELTME 2: ChromaDB Cosine Space Ayarı

**Problem:** ChromaDB **varsayılan olarak L2 (Euclidean)** mesafe kullanır. Semantik benzerlik için `Cosine` gereklidir.

**Düzeltme:**
- **Sprint 2.2'de** collection oluştururken `metadata={"hnsw:space": "cosine"}` set edilecek
- **Neden?** Anlam benzerliği için cosine mesafe kritik öneme sahiptir
- **Avantaj:** "Show me money" ile "Query revenue" arasındaki semantik bağ tam olarak yakalanır

---

## EPIC 1: ŞELALE BEKÇİSİ (Cascade Bouncer - 4-Layer Intent Classification)

**Amaç:** LLM'i niyet anlama yükünden kurtarmak ve hataları minimize etmek için 4 katmanlı, giderek daralan ve %100 İngilizce (English-only) dilinde çalışan bir Şelale (Cascade) filtreleme mimarisi kurmak.
**Toplam Tahmini İş Gücü:** 3 Sprint (Ortalama 2-3 gün/sprint)

---

### 🏃 Sprint 1.1: Katman 1 (Regex) ve Katman 2 (ML) Altyapısı

**Hedef:** En hızlı iki filtrenin (Mutlak Kural ve Yazım Hatası tolere eden ML) kurulması.

**🏗️ Mimari Kararlar:**
- **Dil Kuralı:** Tüm Regex kuralları, eğitim verileri ve NLP süreçleri İNGİLİZCE olacaktır.
- **Katman 1 (Mutlak Kural):** Regex ve exact keyword matching (Hız: <1ms).
  - Örnek kalıplar: "analyze data" → ANALYST, "delete record" → ROUTER, "plot chart" → VISUALIZE
  - `src/intent/layers/layer1_regex.py`: `{pattern: Regex, intent: Label}`
- **Katman 2 (Yazım Hatası Tolere):** `scikit-learn` içinde:
  - `TfidfVectorizer(stop_words='english', analyzer='char_wb', ngram_range=(2,4))`
  - `LogisticRegression` (Hız: <50ms) ⭐ **DÜZELTME 1 UYGULANDI**
  - Char n-gram ile "analyz" → "analyze" gibi typo'ları yakalar
  - Stop words (İngilizce bağlaçlar) otomatik elenir
- **Threading:** Eğitim süreçleri `ThreadPoolExecutor` ile TUI kesinlikle bloklanmaz.
- **Label Set:** `[ROUTER, ANALYST, VISUALIZE, CHAT]`

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, bugün AILO'nun giriş kapısına 'Şelale Bekçisi'nin ilk iki katmanını kuruyoruz. **Sistemin resmi dili İNGİLİZCE'dir.**
>
> **Kontekst:**
> - Hedef dosya: `src/intent/cascade_bouncer.py` (orchestrator), `src/intent/layers/`
> - Mevcut kod: Eski tek katmanlı `intent_router` fonksiyonu (kaldırılacak)
> - Test dosyası: `tests/unit/test_cascade_bouncer.py`
>
> **Katman 1 - Mutlak Kural (Regex):**
> 1. `src/intent/layers/layer1_regex.py` dosyası oluştur.
> 2. İngilizce keyword → intent mapping dictionary yaz. Örnek:
>    - "analyze", "analysis", "statistics" → ANALYST
>    - "delete", "remove", "drop", "wipe" → ROUTER
>    - "plot", "chart", "graph", "visualize" → VISUALIZE
>    - "hello", "hi", "chat", "talk" → CHAT
> 3. `match(text)` fonksiyonu: Regex veya exact match kontrolü, varsa intent döner.
>
> **Katman 2 - ML Tipo Toleransı:**
> 1. `TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4), stop_words='english')` ile char n-gram vektörleştirme kur.
> 2. `LogisticRegression` pipeline ile 4 class sınıflandırma. ⭐ **NOT:** `LinearSVC` DEĞİL, `LogisticRegression` kullan. `LinearSVC`'nin `predict_proba()` metodu yok!
> 3. `predict_proba` ile confidence hesapla.
> 4. Confidence threshold < 0.6 ise "passthrough" (bir sonraki katmana geç).
>
> **Cascade Orchestrator:**
> 1. `CascadeBouncer` sınıfı: Gelen mesajı sırasıyla Katman 1, 2'ye gönder.
> 2. Her katmandan "passthrough" dönenler bir sonraki katmana geçer.
> 3. Her katman bir öncekinin sonucunu override edebilir.
> 4. **CRITICAL:** Mesajlar İNGİLİZCE olarak işlenir, önce `translate` yok (Kullanıcı İngilizce girerse).
>
> **Threading Notu:**
> - Sınıflandırma senkron olabilir (çok hızlı).
> - Eğitim `ThreadPoolExecutor.submit()` ile arka planda çalışır.
>
> Başla Jules."

---

### 🏃 Sprint 1.2: Katman 3 (Semantik Filtre) Entegrasyonu

**Hedef:** Aynı anlama gelen farklı İngilizce kelimeleri (örneğin "delete" yerine "remove" veya "wipe" denmesi) yakalayacak vektörel anlamsal filtrenin Şelaleye eklenmesi.

**🏗️ Mimari Kararlar:**
- **Bağımlılık:** Bu katman Epic 2'deki İngilizceye özel eğitilmiş `all-MiniLM-L6-v2` modelini (Embedder) ortak kullanacaktır.
- **Mantık:** 1. ve 2. katmandan 'passthrough' dönen mesajlar, Vector DB'deki geçmiş İngilizce niyetlerle semantik olarak karşılaştırılır.
  - Benzerlik > **%85** ise intent Ata
  - Aksi halde 4. katmana (LLM) pasla → `UNKNOWN`
- **Hız:** ~150ms (Embed + Cosine Similarity)
- **Cache:** Bekleme süresini kısaltmak için son 100 query embedding cache'lenebilir.

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, Şelale Bekçisi'ne 3. Katmanı ekliyoruz. İlk iki katmandan 'passthrough' dönen mesajları doğrudan LLM'e atmıyoruz. Araya bir Semantik Filtre koyacağız.
>
> **Kontekst:**
> - Embedder: `src/rag/embedder.py` (Epic 2 Sprint 2.1'den hazır olacak, BİLİNMEZSE mock encode kullan)
> - Vector DB: `src/rag/vector_store.py` (memory_intents collection)
> - Hedef dosya: `src/intent/layers/layer3_semantic.py`
>
> **Dikkat Etmen Gereken Bağımlılık Notu:**
> 1. Bu sprint Epic 2 Sprint 2.1'e BAĞLIDIR. Embedder hazır değilse:
>    - Mock olarak `np.random.rand(384)` ile sahte embedding kullan.
>    - Gerçek embedder geçtiğinde sadece import değişecek.
> 2. İngilizce semantic search yapılacak (tüm intent history İngilizce).
>
> **Görev Detayı:**
> 1. `Layer3Semantic` sınıfı:
>    - `cosine_similarity(embed_a, embed_b)` helper fonksiyonu
>    - `match(text, threshold=0.85)` fonksiyonu:
>      a. Kullanıcı mesajını embed et
>      b. Vector DB'deki tüm intent embedding'lerini çek
>      c. Max cosine similarity'yi bul
>      d. Threshold üzerindeyse intent Ata, değilse `UNKNOWN` döner
> 2. Cascade içinde `Layer3Semantic` çağrısı ekle.
> 3. **İngiliziz Konuşma Algılama:** Eğer mesaj Türkçe ise `translate` flag ver ve Layer 4'e (LLM) pasla. (LLM translate edebilir.)
>
> **Threading Notu:**
> - Vector search `ThreadPoolExecutor` ile çalışır (150ms block acceptable ama tercih edilmez).
>
> Başla Jules."

---

### 🏃 Sprint 1.3: Katman 4 (LLM Fallback) ve Asenkron Öğrenme

**Hedef:** İlk 3 katmandan kaçan en zorlu mesajları Yerel LLM'e (Inference Engine) devretmek ve hatalı/bilinmeyen kararları gece eğitimi için kaydetmek.

**🏗️ Mimari Kararlar:**
- **Katman 4 (LLM):** Bouncer'dan hala 'UNKNOWN' çıkarsa, yerel model (Inference Engine) devreye grin ve İngilizce dilinde mantık yürüterek kararı verir.
  - Hız: 1-2 sn (kabul edilebilir, en zorlu sorular içn)
  - Prompt: Basit "Classify this intent: ROUTER, ANALYST, VISUALIZE, or CHAT?"
- **Asenkron Öğrenme:** Şelale Bekçisi gündüzleri gerçek zamanlı eğitim (fit) YAPMAZ.
  - Katman 4'ün bulduğu sonuçlar → `feedback_logs` tablosuna insert
  - Kullanıcının `/wrong` diyerek düzelttiği niyetler → `feedback_logs` tablosuna insert
  - Gece Bekçisi (Cron job) bu tabloyu okuyup Katman 2 ve Katman 3'ü offline olarak günceller.
- **Unknown Intent Log:** `unknown_intents` tablosuna yazılır, sentetik veri üretimi için kullanılır.

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, Şelale Bekçisi'nin son aşamasındayız. İlk 3 katmandan kaçan mesajları LLM'e paslayacağız ve sistemin kendi kendini güncellemesini sağlayacağız.
>
> **Kontekst:**
> - Inference Engine: `src/model/inference_engine.py` (Epic 3 Sprint 3.2, hazır değilse mock)
> - Database: `data/feedback_logs.db`, `data/unknown_intents.db`
> - Hedef dosya: `src/intent/layers/layer4_llm.py`, `src/intent/cascade_bouncer.py`
>
> **Katman 4 - LLM Wrapper:**
> 1. `Layer4LLM` sınıfı:
>    - `classify_unknown(text)` fonksiyonu
>    - Prompt template (İngilizce): "Classify this user request into one of these intents: ROUTER (SQL/database), ANALYST (data analysis), VISUALIZE (charts/plots), CHAT (general chat). User says: {text}"
>    - Response parser: İlk kelimeyi intent olarak çıkar
> 2. Timeout: 3 saniye. Aşılırsa varsayılan olarak CHAT'e Ata.
> 3. **Fallback:** Inference Engine crash ederse otomatik CHAT'e düş.
>
> **Asenkron Öğrenme Mekanizması:**
> 1. `FeedbackLogger` sınıfı (SQLite async writer):
>    - `record_decision(original_text, predicted_intent, source_layer)` - Katman 4 kararı
>    - `record_correction(original_text, wrong_intent, correct_intent)` - Kullanıcı düzeltmesi
>    - `record_unknown(text)` - Geç 3 katmanı geçen mesajlar
> 2. **CRITICAL:** ASLA anlık `model.fit()` yapma. Sadece database insert.
> 3. Batch insert kullan (tek tek değil, 10-50 batch).
>
> **Cascade Final Entegrasyonu:**
> 1. `on_input` hook'a CascadeBouncer entegre et.
> 2. 10 mesajdan 3+ "UNKNOWN" düşerse log warning.
> 3. Metric toplama: Her katmanın hit rate'i ölçülür (`cascade_stats.json`).
>
> Başla Jules."

---

## EPIC 2: KÜTÜPHANECİ (Semantic RAG) — REVISED

**Amaç:** `difflib` söküp atılarak vektörel semantik arama ile memory çağırma sistemi kurmak. **EPIC 1 Sprint 1.2'NİN BAĞIMLILIĞINI KARŞILAMAK için önceliklendirilmiştir.**
**Toplam Tahmini İş Gücü:** 4 Sprint

---

### 🏃 Sprint 2.1: Embedding Model Kurulumu (ÖNCELEK - FIRST PRIORITY)

**Hedef:** `all-MiniLM-L6-v2` embedding modelinin Pi 5'te çalışır hale getirilmesi.

**🏗️ Mimari Kararlar:**
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (80MB, ONNX formatında ~60MB)
- **Quantization:** `onnxruntime` ile INT8 inference (RAM: ~200MB yerine ~80MB)
- **Cache:** `/home/ailo/.cache/ailo/embeddings/` dizininde saklanır.
- **İngilizce Odaklı:** Model İngilizce eğitimli, İngilizce metinlerde optimum performans.

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, bu sprint EPIC 1 Sprint 1.2'nin BAĞIMLILIĞIDIR. Önce bu bitmeli.
>
> **Kontekst:**
> - Model: `sentence-transformers/all-MiniLM-L6-v2`
> - Format: ONNX (`onnxruntime` ile çalışacak)
> - Hedef dosya: `src/rag/embedder.py`
> - Test dosya: `tests/unit/test_embedder.py`
>
> **Dikkat Etmen Gereken Raspberry Pi 5 Kısıtlamaları:**
> 1. **RAM:** `onnxruntime.SessionOptions` üzerinde `memory_per_thread` optimizizasyonu yap.
>  2. **Embedding Boyutu:** 384 boyut (çok düşük RAM).
> 3. **Inference Hızı:** Hedef < 100ms/embed (Pi 5 CPU).
> 4. **Cache:** Modeli bir kez yükle ve `singleton` pattern ile paylaş.
>
> **Görev Detayı:**
> 1. Modeli HuggingFace'ten indir ve ONNX'e çevir (veya `optimum` library kullan).
> 2. `Embedder` singleton sınıfı: `encode(texts)` ve `encode_once(text)`.
> 3. Unit test: İki İngilizce cümlenin cosine similarity'si hesaplanabilir.
> 4. **İngilizce Calibration:** "analyze data" ve "look at statistics" benzer olmalı, "delete file" farklı olmalı.
>
> Başla Jules."

---

### 🏃 Sprint 2.2: Vektör Veritabanı (ChromaDB)

**Hedef:** Memory verilerinin vektörel olarak saklanması ve semantik arama yapılması.

**🏗️ Mimari Kararlar:**
- **Vektör DB:** `ChromaDB` (Pi 5 uyumlu, persistent client)
- **Persist:** `/data/ailo/memory_vectors/` dizininde kalıcı saklama.
- **Collections:**
  - `memory_intents` → Intent history (Şelale Bekçisi için)
  - `memory_router` → /router persona Tecrübeleri
  - `memory_analyst` → /analyst persona Tecrübeleri
  - `memory_visualize` → /visualize persona Tecrübeleri
  - `default` → Genel konuşma hafızası
- **RAM Limit:** Persistent client, tüm veri RAM'e yüklenmez.
- **⭐ DÜZELTME 2 UYGULANDI:** Collection oluştururken `metadata={"hnsw:space": "cosine"}` set edilmeli. ChromaDB varsayılanı L2 (Euclidean) kullanır ama semantik arama için Cosine şart!

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, Embedder hazır. Şimdi onu bir vektör veritabanına bağlıyoruz.
>
> **Kontekst:**
> - Embedder: `src/rag/embedder.py` (Sprint 2.1'den hazır)
> - Veritabanı: ChromaDB
> - Mevcut Memory: `data/memory_*.json` dosyaları (İngilizce'ye çevrilecek)
> - Hedef dosya: `src/rag/vector_store.py`
>
> **Dikkat Etmen Gereken Teknik Detaylar:**
> 1. **ChromaDB Client:** `chromadb.PersistentClient(path="/data/ailo/memory_vectors")` kullan.
> 2. **⭐ CRITICAL: Cosine Mesafe Ayarı:** Collection oluştururken `metadata={"hnsw:space": "cosine"}` set et. ChromaDB varsayılanı L2 (Euclidean) kullanır, ama semantik benzerlik için Cosine şart! "Show me money" ile "Query revenue" arasındaki bağ ancak Cosine ile yakalanır.
> 3. **Upsert:** Aynı ID ile yeniden insert yapılabilmeli (güncelleme).
> 4. **Query:** `n_results=3` ile en yakın 3 sonuç dönsün.
> 5. **İngilizce İçerik:** Tüm memory içerikleri İngilizce olmalı. Türkçe varsa boş.
>
> **Görev Detayı:**
> 1. `src/rag/memory_loader.py`: Eski `memory_*.json` dosyalarını ChromaDB'ye import (İngilizce çeviri ile).
> 2. `src/rag/vector_store.py`: `add_memory`, `search_memory`, `delete_memory`.
> 3. Sistemin İNGİLİZCE konuşma yapacak şekilde memory population et.
>
> **NOT:** `difflib` kodunu HENÜZ SİLME. Paralel çalışsın.
>
> Başla Jules."

---

### 🏃 Sprint 2.3: Semantic Search Entegrasyonu (TUI)

**Hedef:** TUI içinde kullanıcı sorgularına anlamsal yanıt verilmesi ve Omnibar'da Ghost Text önerileri.

**🏗️ Mimari Kararlar:**
- **PromptCompletion:** Kullanıcı `/` tuşuna bastığında İngilizce embed'e göre öneri göster.
- **ContextInjection:** Model çağrılmadan önce en yakın 3 memory TUI içinde context olarak enjekte edilir.
- **HybridSearch:** Vektör + keyword (BM25) birlikte (ileride).

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, bugün Kütüphaneci'yi TUI'ye bağlıyoruz.
>
> **Kontekst:**
> - `tui_engine.py`: Omnibar'da Ghost Text önerileri
> - `vector_store.py`: Semantik arama fonksiyonları
> - Hedef: Omnibar'da `/` basılınca vektörel arama sonuçları göster
>
> **Dikkat Etmen Gereken UI Tuzakları:**
> 1. **Async:** Semantik arama `ThreadPoolExecutor` üzerinden çalışır (blok yok).
> 2. **Latency:** Arama sonucu 200ms içinde Omnibar'da görünmeli.
> 3. **Fallback:** Arama boşsa "No similar experience found" göster.
>
> **Görev Detayı:**
> 1. `src/tui/omnibar_suggestions.py`: Omnibar'da `/` aramasında Semantic Search hook.
> 2. Model PromptTemplate'ine context injection noktası ekle.
> 3. Yeni memory otomatik kaydedilsin (`auto_save=True`).
>
> Başla Jules."

---

### 🏃 Sprint 2.4: Legacy difflib Temizliği ve Optimizasyon

**Hedef:** Eski `difflib` kodunun sökülmesi, ChromaDB indeksleme optimizasyonu.

**🏗️ Mimari Kararlar:**
- **Silinecek:** `src/memory/difflib_ranker.py`
- **İndeksleme:** HNSW algorithm (ChromaDB varsayılanı)
- **Archive:** `archive/dates/difflib_legacy_*.py` ve `archive/dates/memory_*.json`

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, bugün temizlik günü. Eski `difflib` kodunu sökeceğiz.
>
> **Dikkat Etmen Gereken Migration Kısıtlamaları:**
> 1. **A/B Test:** `difflib` silmeden önce 1 hafta paralel çalışsın.
> 2. **Backup:** Önce `archive/dates/` altına yedekle.
> 3. **Migration Doc:** `docs/MIGRATION_v1_to_v2.md` raporu yaz.
>
> **Görev Detayı:**
> 1. Silinecek dosyaları listele ve raporla.
> 2. Sil ve migration doc yaz.
>
> Başla Jules."

---

## EPIC 3: BEYİN TRANSPLANTI (Model Yükseltmesi)

**Amaç:** Qwen 0.5B'nin sökülüp Pi 5'te akıcı çalışan daha güçlü bir model entegre edilmesi. Inference Engine İNGİLİZCE prompt'lar için optimize edilecektir.
**Toplam Tahmini İş Gücü:** 5 Sprint

---

### 🏃 Sprint 3.1: Model Seçimi ve Benchmark

**Hedef:** Pi 5 performansına göre en uygun modelin belirlenmesi.

**🏗️ Mimari Kararlar:**
- **Kriter:** > 10 token/sn, < 2GB RAM, Q4_K_M quant
- **Aday Modeller:**
  - `Qwen/Qwen2.5-1.5B-Instruct-GGUF` (İngilizce+Türkçe yetenek, hızlı)
  - `lmstudio-community/Llama-3.2-3B-Instruct-GGUF` (Genel İngilizce kalite)
- **Inference Engine:** `llama-cpp-python`

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, bugün AILO'nun beynini seçiyoruz. Bu benchmark maratonu olacak.
>
> **Donanım Kısıtlamaları:**
> 1. **RAM:** `n_gpu_layers=0`, `n_threads=4`
> 2. **Context:** `n_ctx=2048`
> 3. **GGUF:** Sadece Q4_K_M quant
>
> **Görev Detayı:**
> 1. Her model için benchmark script: latency, token/sn, RAM kullanımı.
> 2. İNGİLİZCE test dataset: 50 soru-cevap çifti (analyze, delete, visualize, chat)
> 3. JSON çıktısı: `benchmark_results/{model_name}.json`
>
> Başla Jules."

---

### 🏃 Sprint 3.2: llama-cpp-python Entegrasyonu

**Hedef:** Seçilen modelin sisteme entegre edilmesi.

**🏗️ Mimari Kararlar:**
- **Binding:** `llama-cpp-python`
- **Threading:** `ThreadPoolExecutor` ile inference
- **Streaming:** Token-by-token TUI'ye

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, benchmark'ta kazanan modeli montaj ediyoruz.
>
> **CRITICAL Threading Tuzakları:**
> 1. **SQLite:** Inference tamamlanana kadar başka thread yazma yapabilir. `asyncio` ile senkronize et.
> 2. **TUI:** Streaming callback `main_event_loop.call_soon_threadsafe()` ile gönder.
> 3. **RAM:** `mmap_size` 2GB.
>
> **Görev Detayı:**
> 1. `InferenceEngine` sınıfı: init, load_model, generate, stream_generate.
> 2. Context management ve RAM temizliği.
> 3. Sistem prompt template (İNGİLİZCE, persona başına ayrı).
>
> Başla Jules."

---

### 🏃 Sprint 3.3: Constrained Decoding (Grammar Constraints)

**Hedef:** Model halüsinasyonlarını donanım seviyesinde engellemek.

**🏗️ Mimari Kararlar:**
- **Library:** `outlines` (JSON grammar) veya `llama-cppgrammar` (SQL)
- **Output Types:** JSON, SQL, Markdown
- **Constraint:** ROUTER persona'larında SQL grammar

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, modeli dizginliyoruz (halüsinasyon engeli).
>
> **Performans Kısıtlamaları:**
> 1. **RAM:** Constrained decoding ~20% daha yavaş.
> 2. **Memory Leak:** Her inference sonrası `gc.collect()`.
> 3. **Fallback:** Parse hatalarında serbest markdown'a düş.
>
> **Görev Detayı:**
> 1. JSON schema: `{type, data, confidence}`
> 2. SQL grammar: sadece `SELECT ... FROM ... WHERE ...`
> 3. ROUTER modu için grammar强制
> 4. Parse validator
>
> Başla Jules."

---

### 🏃 Sprint 3.4: Şelale Bekçisi + Model Pipeline Entegrasyonu

**Hedef:** Cascade Bouncer + Model pipeline'ının birleştirilmesi.

**🏗️ Mimari Kararlar:**
- **Flow:**
  1. Mesaj → Katman 1 (Regex) → Katman 2 (LogisticRegression) → Katman 3 (Semantic) → Katman 4 (LLM)
  2. Intent'li mesaj + Memory → Inference Engine
  3. Constrained Output → TUI
- **Timeout:** Toplam pipeline < 3 saniye

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, parçaları birleştiriyoruz.
>
> **Pipeline Tuzakları:**
> 1. **Cascade Failure:** Bouncer hata verirse → CHAT'e düş
> 2. **Memory Timeout:** Vector search 500ms aşarsa resultsiz devam et
> 3. **Model Timeout:** 30s sonrası "Thinking..." göster
>
> **Görev Detayı:**
> 1. `src/pipeline/orchestrator.py`: Tüm modülleri zincirle
> 2. `on_input` hook'u orchestrator'a bağla
> 3. Error middleware + performans loglama
>
> Başla Jules."

---

### 🏃 Sprint 3.5: Model Eğitim Veri Türetme

**Hedef:** Mevcut memory'lerden fine-tuning veri seti türetme.

**🏗️ Mimari Kararlar:**
- **Format:** Alpaca instruction-tuning
- **Kalite:** Sadece human-verified feedback'ler

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, geleceğe yatırım: Veri seti türetiyoruz.
>
> **Kalite Kısıtlamaları:**
> 1. Sadece `corrected=True` feedback'ler kullanılacak
> 2. Deduplication
> 3. İNGİLİZCE Alpaca formatı: `<|im_start|>user...`
>
> **Görev Detayı:**
> 1. Memory + Feedback'ten alpaca formatında veri çıkar
> 2. Train/Val split (%90/%10)
> 3. `out/ailo_train_v1.jsonl` çıktısı
>
> Başla Jules."

---

## EPIC 4: OTONOM ONARIM (RLHF / Human-in-the-Loop)

**Amaç:** Kullanıcının `/fix` veya `/wrong` komutuyla hata düzeltmesi ve sistemin kendi kendini onarması.
**Toplam Tahmini İş Gücü:** 2 Sprint

---

### 🏃 Sprint 4.1: Feedback Loop Mekanizması

**Hedef:** `/fix` veya `/wrong` ile hata düzeltmesi ve veritabanına kayıt.

**🏗️ Mimari Kararlar:**
- **DB:** `feedback_logs` tablosu
- **Schema:** `id, timestamp, user_input, predicted_intent, corrected_intent, source_layer, status`
- **UI:** Minimal, sessiz overlay

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, bugün öğrenme refleksini kodluyoruz.
>
> **Teknik Detaylar:**
> 1. **Async:** Feedback kaydetme `loop.run_in_executor()` ile arka planda
> 2. **Undo:** `/undo` komutuyla son feedback silinebilir
> 3. **Batch:** 1000 satırı geçerse en eski %20归档
>
> **Görev Detayı:**
> 1. SQLite migration: `feedback_logs` tablosu
> 2. `FeedbackHandler` sınıfı: `record_feedback()`, `get_recent()`, `undo()`
> 3. TUI overlay: `[Wrong intent? /fix ROUTER]`
>
> Başla Jules."

---

### 🏃 Sprint 4.2: Kritik Hata Analizi ve Auto-Retrain Tetikleyicisi

**Hedef:** Feedback'lere dayanarak sistemin kalıcı kendini düzeltmesi.

**🏗️ Mimari Kararlar:**
- **Threshold:** 10+ aynı intent düzeltmesi → Otomatik retrain tetikle
- **Action:** Retrain scripti cronjob 04:00'te çalışır
- **Cooldown:** Minimum 24 saat between retrain attempts
- **Rollback:** Yeni model F1 < 0.80 → otomatik rollback

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, Kendi kendini düzelten sistem.
>
> **Looping Engeli:**
> 1. Bir intent 10+ düzeltiliyorsa retrain durur, insan müdahalesi beklenir
> 2. Backup: Her retrain öncesi `archive/models/bouncer_backup_{timestamp}.joblib`
> 3. Rollback: F1 < 0.80 ise eski modele dön
>
> **Görev Detayı:**
> 1. `ErrorAnalyzer`: Her label için düzeltme sayısı pattern çıkarma
> 2. `TriggerRetrain`: Threshold aşılırsa retrain çağır
> 3. `CronWrapper`: 04:00 scripti
> 4. `RollbackHandler`: Başarısız retrain sonrası eski modele dön
>
> Başla Jules."

---

## EPIC 5: GECE BEKÇİSİ (Night Watchman - Otonom Gece Eğitimi)

**Amaç:** Gece 04:00'te Gemini kullanarak sentetik veri üretmek ve Şelale Bekçisi'ni güncellemek.
**Toplam Tahmini İş Gücü:** 2 Sprint

---

### 🏃 Sprint 5.1: Cron Job ve Gece Pipeline'sı

**Hedef:** 04:00 cronjob ile gece eğitim döngüsünün kurulması.

**🏗️ Mimari Kararlar:**
- **Trigger:** `0 4 * * * /usr/local/bin/ailo_nightwatch.sh`
- **Runtime:** `nohup` ile çalışır, loglar `/logs/nightwatch.log`
- **Guard:** Kilitle dosyası ile önceki işlem kontrolü

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, AILO uyurken gece bekçisi çalışacak.
>
> **Cron Ortam Kısıtlamaları:**
> 1. **Environment:** `PATH`, `PYTHONPATH` manuel set edilmeli
> 2. **Lock:** `/data/ailo/nightwatch.lock` kontrolü
> 3. **Cleanup:** İşlem sonu lock silme ve RAM temizliği
>
> **Görev Detayı:**
> 1. `scripts/watchdog.sh`: Lock, ortam, başlatıcı
> 2. `scripts/nightwatch_main.py`: Pipeline orchestration
> 3. Pipeline: Feedback analizi → Gemini çağrısı → Sentetik veri → Retrain
>
> Başla Jules."

---

### 🏃 Sprint 5.2: Gemini ile Sentetik Veri Üretimi

**Hedef:** `feedback_logs` ve `unknown_intents` tabanlı sentetik eğitim verisi üretimi.

**🏗️ Mimari Kararlar:**
- **API:** Google Gemini 2.0 Flash
- **PromptEngineering:** Few-shot İngilizce prompt
- **Format:** İNGİLİZCE Alpaca formatında
- **Kalite:** Çıktılar `pending_validation` tablosuna gider

**🤖 Jules İçin İnsancıl Prompt:**

> "Selam Jules, Gemini'ye "Bulut Öğretmen" rolü verdiriyoruz.
>
> **API ve Maliyet Kısıtlamaları:**
> 1. **Bütçe:** Günlük max $0.50, batch 50 token
> 2. **RateLimit:** 60 req/dakika, `time.sleep(1)` koy
> 3. **İNGİLİZCE Output:** Gemini İngilizce sentetik veri üretir
> 4. **Validation:** `pending_validation` tablosuna insert
>
> **Görev Detayı:**
> 1. `SyntheticGenerator` sınıfı: `generate_for_intent(intent, count=10)`
> 2. Few-shot İngilizce prompt template
> 3. Gemini response parser
> 4. `pending_validation` tablosuna batch insert
> 5. Rapor: veri sayısı, maliyet, başarı oranı
>
> Başla Jules."

---

## EPIC 6: GELECEK VİZYON (İsteğe Bağlı)

---

### 🏗️ Epic 6.1: Tool Calling & MCP Mimarisi
- MCP SDK ile tool tanımlama
- GPIO, HTTP, PDF export
- Sadece ROBOT, IOT persona'ları etkin

### 🏗️ Epic 6.2: IoT Sensör Ağı & FSM
- Pandas/NumPy ile anomali tespiti
- Telegram/APRS bildirimi
- 1 dk periyotlarla sensör okuma

### 🏗️ Epic 6.3: Bilgisayarlı Görü (Vision)
- MediaPipe gesture recognition
- OpenCV nesne tespiti
- Kamera FPS < 10

### 🏗️ Epic 6.4: Plug-and-Play Personalar
- `personas/*.yaml` dosya formatı
- Hot-reload mekanizması
- Auto-Routing

---

## Sprint Özet Matrisi (Sıralı Görünüm) — v2.1 REVISED

| Sıra | Epic | Sprint | Tahmini Süre | Öncelik | Bağımlılık | Düzeltme |
|------|------|--------|--------------|---------|------------|----------|
| **1** | Epic 2 | Sprint 2.1 **(ÖNCELİK)** | 2-3 gün | **KRITIK** | Yok (Şelale 1.2 için şart) | - |
| 2 | Epic 1 | Sprint 1.1 | 2-3 gün | KRITIK | Yok | ⭐ Düzeltme 1: LogisticRegression |
| 3 | Epic 1 | Sprint 1.2 | 2-3 gün | KRITIK | 2.1 | - |
| 4 | Epic 1 | Sprint 1.3 | 2-3 gün | YÜKSEK | 1.2 | - |
| 5 | Epic 2 | Sprint 2.2 | 2-3 gün | YÜKSEK | 2.1 | ⭐ Düzeltme 2: Cosine Space |
| 6 | Epic 2 | Sprint 2.3 | 2-3 gün | YÜKSEK | 2.2 | - |
| 7 | Epic 2 | Sprint 2.4 | 1-2 gün | ORTA | 2.3 | - |
| 8 | Epic 3 | Sprint 3.1 | 3-4 gün | KRITIK | Yok | - |
| 9 | Epic 3 | Sprint 3.2 | 3-4 gün | KRITIK | 3.1 | - |
| 10 | Epic 3 | Sprint 3.3 | 2-3 gün | YÜKSEK | 3.2 | - |
| 11 | Epic 3 | Sprint 3.4 | 2-3 gün | KRITIK | 3.3, 1.3, 2.3 | - |
| 12 | Epic 3 | Sprint 3.5 | 1-2 gün | ORTA | 3.4 | - |
| 13 | Epic 4 | Sprint 4.1 | 2-3 gün | YÜKSEK | 1.1 | - |
| 14 | Epic 4 | Sprint 4.2 | 2-3 gün | YÜKSEK | 4.1 | - |
| 15 | Epic 5 | Sprint 5.1 | 2-3 gün | ORTA | 4.2, 3.4 | - |
| 16 | Epic 5 | Sprint 5.2 | 3-4 gün | ORTA | 5.1 | - |

**Toplam:** ~35-45 iş günü

**Yeni Başlangıç Sıralaması:**
1. **Sprint 2.1** → Epic 1 Sprint 1.2'nin bağımlılığı için ÖNCE çalışmalı
2. **Sprint 1.1** → İlk geliştirme sprinti (bağımsız)
3. Paralel izleme: Epic 2 ve Epic 1 birbirine bağımlı

---

## Sonraki Adımlar (Immediate Actions)

1. **Jules'a İlk Sprint Ver:** Sprint **2.1** (Embedder) — Şelale 1.2'nin bağımlılığı için şart
2. **Jules'a İkinci Sprint Ver:** Sprint **1.1** (Regex + **LogisticRegression**) — ⭐ Düzeltme 1 uygulandı
3. **Dockerfile Güncelle:** `Dockerfile.arm64` (Pi 5, `pyproject.toml`)
4. **CI/CD:** GitHub Actions `:arm64` auto-build
5. **API Key:** `get_secrets()` ile yönet

---

## ✅ DÜZELTME ÖZETİ (v2.1)

| Düzeltme | Sprint | Değişiklik | Neden |
|----------|--------|------------|-------|
| **1** | Sprint 1.1 | `LinearSVC` → `LogisticRegression` | `LinearSVC`'nin `predict_proba()` metodu yok. Olasılık tahmini için LogisticRegression şart. |
| **2** | Sprint 2.2 | ChromaDB collection'da `metadata={"hnsw:space": "cosine"}` | Semantik arama için Cosine mesafe şart. Varsayılan L2 Euclidean semantik benzerliği yakalayamaz. |

---

*Bu plan GSD metodolojisine sadık, modüler ve iteratif ilerlemeye uygun olarak tasarlanmıştır. Her Sprint sonunda kısa retrospektif yapılması önerilir.*

*v2.1 Değişiklikleri:*
- *Kritik Hata Düzeltmeleri: LinearSVC → LogisticRegression (Düzeltme 1)*
- *Kritik Hata Düzeltmeleri: ChromaDB Cosine Space (Düzeltme 2)*
- *Tüm sprintlerde ilgili değişiklikler uygulandı*
- *Düzeltme matrisi eklendi*
