Here is a **clear, short, step-by-step instruction message** you can send him.
It includes all commands, all setup steps, and exactly what he needs to run the project.

You can copy-paste this into a **text file**, chat message, or README for him.

---

# **How to Run the Insurance Voice Bot (Setup Guide)**

Follow these steps to clone, set up, and run the project on your local machine.

---

## **1. Clone the repository**

```bash
git clone https://github.com/Benston-Daniel/insurance-voice-bot.git
cd insurance-voice-bot
```

---

## **2. Create & activate the virtual environment**

### **Windows (PowerShell)**

```powershell
python -m venv botenv
.\botenv\Scripts\Activate.ps1
```

### **Mac / Linux**

```bash
python3 -m venv botenv
source botenv/bin/activate
```

---

## **3. Install project dependencies**

Make sure the virtual environment is **activated**, then run:

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

---

## **4. Install ffmpeg**

Whisper requires ffmpeg for audio decoding.

### **Windows**

1. Download from: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   Choose a *static* Windows build.
2. Extract it.
3. Add the `/bin` folder to your System PATH:

   ```
   C:\ffmpeg\bin
   ```
4. Close & reopen terminal.

### **Mac**

```bash
brew install ffmpeg
```

### **Linux (Ubuntu)**

```bash
sudo apt install ffmpeg -y
```

To verify:

```bash
ffmpeg -version
```

---

## **5. Download the LLM model (GGUF)**

Run Python and use this snippet:

```python
from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="abhinand/gemma-2b-it-tamil-v0.1-alpha-GGUF",
    filename="gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf",
)

print("Downloaded.")
```

This will place the model under:

```
models/gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf
```

---

## **6. If you do NOT have a GPU**

Open:

```
backend/src/main_server.py
```

Find the llama model loader and set:

```python
n_gpu_layers = 0
```

This forces CPU mode.

If needed, reduce model size by switching to `"tiny"` Whisper:

```powershell
setx WHISPER_MODEL tiny
```

---

## **7. Run the backend server**

From the project root (venv active):

```bash
python backend/src/main_server.py
```

This will:

* Load Whisper
* Load BM25 RAG
* Load the Gemma GGUF model
* Start the WebSocket server at `ws://localhost:8765`

---

## **8. Run the frontend**

Simply open:

```
frontend/index.html
```

in any browser (Chrome recommended).

You will see:

* Chat interface
* Mic recording
* AI responses (Tamil or English)
* Optional text-to-speech playback

---
