# **InsuranceAI Voice Bot**

AI-powered insurance assistant that supports **Tamil + English**, understands **voice or text**, retrieves answers from real **policy documents** (RAG), and responds using a local **GGUF LLM**.

This project uses:

* **Whisper** for speech-to-text
* **BM25 RAG** over chunked policy PDFs
* **Gemma 2B Tamil GGUF** for answer generation
* **WebSocket + Browser UI** for real-time chat

---

## ** Quick Start (Run in 30 seconds)**

```bash
# 1. Activate virtual environment (Windows)
.\botenv\Scripts\Activate.ps1

# 2. Start backend
python backend/src/main_server.py

# 3. Open frontend
# Simply open   frontend/index.html   in any browser
```

That's it — speak, type, and get policy-grounded answers.

---

## ** Installation & Setup**

### **1. Clone the repository**

```bash
git clone https://github.com/your-username/insurance-voice-bot.git
cd insurance-voice-bot
```

### **2. Create & activate virtual environment**

```bash
python -m venv botenv
.\botenv\Scripts\Activate.ps1   # Windows
# OR
source botenv/bin/activate      # Linux/macOS
```

### **3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### **4. Install ffmpeg (required for Whisper + audio decoding)**

* **Windows**: Download from [https://ffmpeg.org](https://ffmpeg.org) → add `/bin` to PATH
* **Ubuntu**:

  ```bash
  sudo apt install ffmpeg
  ```

---

## ** Download the LLM model (GGUF)**

Place model inside `models/`:

```python
from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="abhinand/gemma-2b-it-tamil-v0.1-alpha-GGUF",
    filename="gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf",
)
```

After download, ensure:

```
models/gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf
```

---

## ** One-Time Setup: Extract Policy Knowledge Base**

Run this once if `data/policies_chunks.jsonl` is missing:

```bash
python backend/src/extract_policies.py
```

This converts the policy PDFs into searchable chunks for RAG.

---

## **▶️ Run the Project**

### **Backend**

```bash
python backend/src/main_server.py
```

This loads:

* Whisper ASR
* BM25 index
* Gemma 2B GGUF LLM
* WebSocket server at `ws://localhost:8765`

### **Frontend**

Just open:

```
frontend/index.html
```

The page provides:

* Chat interface
* Mic recording
* AI responses + optional spoken output

---

## ** Directory Overview**

```
insurance-voice-bot/
│
├── backend/
│   ├── src/
│   │   ├── main_server.py        # WebSocket server (ASR + RAG + LLM)
│   │   ├── retreive_respond.py   # RAG agent (BM25 + LLM generation)
│   │   ├── extract_policies.py   # PDF → text chunk extractor
│   │   ├── index_bm25.py         # BM25 builder
│   │   ├── lang_detect.py        # Tamil/English detector
│   │   └── llm.py                # LLM loading helpers
│   └── requirements.txt
│
├── data/
│   ├── policies_chunks.jsonl     # Chunked knowledge base
│   ├── bm25_index.pkl            # Cached BM25 index
│   └── intents, mocks, etc.
│
├── models/
│   └── gemma-2b-it-tamil…gguf    # Local LLM (download manually)
│
├── frontend/
│   └── index.html                # Chat UI
│
├── policies/                     # Original PDF policies
└── README.md
```

---

## ** Troubleshooting**

Common errors and solutions are documented in:

```
IA.md
```

Topics include:

* ffmpeg decoding issues
* Whisper model slow / missing
* GGUF model not loading
* BM25 index errors
* Token overflow / context window errors

---

## ** What This Project Demonstrates**

* End-to-end LangChain-style RAG **without LangChain**
* Real-time voice conversation using browser WebSocket
* Local offline LLM (GGUF) answering strictly from policy data
* Tamil + English automatic language support
* Minimal, clean, easy-to-run architecture

---
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
# insurance-voice-bot
AI Insurance multi lingual Voice Assistance using RASA NLU
=======
# Insurance Voice Bot (starter)
=======
# Insurance Voice Bot (Bilingual NLU+LLM)
>>>>>>> 8f9c065 (chore: migrate from Rasa; scaffold lightweight NLU/LLM architecture, add nlu_engine, llm_runner, backend, data, scripts)
=======
# **InsuranceAI Voice Bot**
>>>>>>> f5a8b88 (Made major changes in the architecture, used gemma model, developed frontend and a simple socket based realtime audio transcription.)

AI-powered insurance assistant that supports **Tamil + English**, understands **voice or text**, retrieves answers from real **policy documents** (RAG), and responds using a local **GGUF LLM**.

This project uses:

* **Whisper** for speech-to-text
* **BM25 RAG** over chunked policy PDFs
* **Gemma 2B Tamil GGUF** for answer generation
* **WebSocket + Browser UI** for real-time chat

---

## ** Quick Start (Run in 30 seconds)**

```bash
# 1. Activate virtual environment (Windows)
.\botenv\Scripts\Activate.ps1

# 2. Start backend
python backend/src/main_server.py

# 3. Open frontend
# Simply open   frontend/index.html   in any browser
```

That's it — speak, type, and get policy-grounded answers.

---

## ** Installation & Setup**

### **1. Clone the repository**

```bash
git clone https://github.com/your-username/insurance-voice-bot.git
cd insurance-voice-bot
```

### **2. Create & activate virtual environment**

```bash
python -m venv botenv
.\botenv\Scripts\Activate.ps1   # Windows
# OR
source botenv/bin/activate      # Linux/macOS
```

### **3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### **4. Install ffmpeg (required for Whisper + audio decoding)**

* **Windows**: Download from [https://ffmpeg.org](https://ffmpeg.org) → add `/bin` to PATH
* **Ubuntu**:

  ```bash
  sudo apt install ffmpeg
  ```

---

## ** Download the LLM model (GGUF)**

Place model inside `models/`:

```python
from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="abhinand/gemma-2b-it-tamil-v0.1-alpha-GGUF",
    filename="gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf",
)
```

After download, ensure:

```
models/gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf
```

---

## ** One-Time Setup: Extract Policy Knowledge Base**

Run this once if `data/policies_chunks.jsonl` is missing:

```bash
python backend/src/extract_policies.py
```

This converts the policy PDFs into searchable chunks for RAG.

---

## **▶️ Run the Project**

### **Backend**

```bash
python backend/src/main_server.py
```

This loads:

* Whisper ASR
* BM25 index
* Gemma 2B GGUF LLM
* WebSocket server at `ws://localhost:8765`

### **Frontend**

Just open:

```
frontend/index.html
```

The page provides:

* Chat interface
* Mic recording
* AI responses + optional spoken output

---

## ** Directory Overview**

```
insurance-voice-bot/
│
├── backend/
│   ├── src/
│   │   ├── main_server.py        # WebSocket server (ASR + RAG + LLM)
│   │   ├── retreive_respond.py   # RAG agent (BM25 + LLM generation)
│   │   ├── extract_policies.py   # PDF → text chunk extractor
│   │   ├── index_bm25.py         # BM25 builder
│   │   ├── lang_detect.py        # Tamil/English detector
│   │   └── llm.py                # LLM loading helpers
│   └── requirements.txt
│
├── data/
│   ├── policies_chunks.jsonl     # Chunked knowledge base
│   ├── bm25_index.pkl            # Cached BM25 index
│   └── intents, mocks, etc.
│
├── models/
│   └── gemma-2b-it-tamil…gguf    # Local LLM (download manually)
│
├── frontend/
│   └── index.html                # Chat UI
│
├── policies/                     # Original PDF policies
└── README.md
```

---

## ** Troubleshooting**

Common errors and solutions are documented in:

```
IA.md
```

Topics include:

* ffmpeg decoding issues
* Whisper model slow / missing
* GGUF model not loading
* BM25 index errors
* Token overflow / context window errors

---

## ** What This Project Demonstrates**

* End-to-end LangChain-style RAG **without LangChain**
* Real-time voice conversation using browser WebSocket
* Local offline LLM (GGUF) answering strictly from policy data
* Tamil + English automatic language support
* Minimal, clean, easy-to-run architecture

<<<<<<< HEAD
Server starts at `http://localhost:8000`

## 📡 API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Text Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my claim status?"}'
```

### 3. Voice Query (ASR + NLU + TTS)
```bash
curl -X POST http://localhost:8000/voice \
  -F "file=@audio.wav" \
  -F "lang=auto"
```

### 4. Interactive Docs
Open `http://localhost:8000/docs` (Swagger UI)

## 🧪 Testing

**Text Query (Tamil):**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "என் பாலிசி நிலை என்ன?"}'
```

## 🐳 Docker

```bash
docker-compose up --build
```

## 📝 Migration Notes

<<<<<<< HEAD
Notes and next steps:
- `backend/app/asr.py` and `backend/app/tts.py` are stubs. Integrate Whisper/Coqui TTS as needed.
- Add tests and improve CI pipeline.
- Secure production deployments and configure credentials.
>>>>>>> 904de86 (Initial commit for dev branch)
=======
- **Rasa Removed:** Custom lightweight NLU replaces Rasa
- **Benefits:** No heavy Rasa server, easier to embed in edge devices
- See `backups/cleanup_log.md` for migration details.
>>>>>>> 8f9c065 (chore: migrate from Rasa; scaffold lightweight NLU/LLM architecture, add nlu_engine, llm_runner, backend, data, scripts)
=======
---
>>>>>>> f5a8b88 (Made major changes in the architecture, used gemma model, developed frontend and a simple socket based realtime audio transcription.)
