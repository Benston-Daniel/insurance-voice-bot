Excellent. 👌
You’ve reached the stage where your project needs a **complete documentation set** — something that can stand as a professional handover pack or internal design reference.

Below is a structured, ready-to-use documentation bundle for your **Insurance Voice Agent** project — written like an industry-grade **SRS + SDD + Impact Analysis + Architecture & Logic Flow** package.

You can paste this into your repo as `/docs/Insurance_Voice_Agent_Documentation.md` or export as a PDF.

---

# 🧠 **Insurance Voice Agent — Technical Documentation Suite**

---

## 📘 1. Software Requirements Specification (SRS)

### 1.1 Purpose

The purpose of this system is to build an **AI-powered bilingual (Tamil + English) voice assistant** that can handle end-to-end **insurance customer service tasks** — including policy inquiries, claims initiation, authentication, and FAQs — via a natural voice interface.

### 1.2 Scope

The agent provides:

* **Speech-to-Speech conversations** (Mic input → spoken AI reply).
* **Insurance workflow automation:** policy lookup, claims filing, payment guidance, customer verification.
* **Bilingual fluency (Tamil + English)** with support for code-switching.
* **Context-aware, multi-turn dialogue** through Rasa NLU.
* **Local deployment** for privacy and cost control, using open-source components.

### 1.3 Users & Use Cases

| User Type                   | Description                                      | Key Actions                                            |
| --------------------------- | ------------------------------------------------ | ------------------------------------------------------ |
| **Customer**                | End-user interacting via browser or mobile mic   | Speak or type queries about policies, claims, payments |
| **Insurance Agent / Admin** | Monitors logs, reviews claims                    | View logs, check claims, verify authenticity           |
| **Developer / Maintainer**  | Maintains model training, backend & integrations | Update Rasa models, fine-tune ASR/TTS                  |

### 1.4 Functional Requirements

| ID   | Function                     | Description                                                      |
| ---- | ---------------------------- | ---------------------------------------------------------------- |
| FR-1 | **Voice Input Capture**      | System records user audio via mic and sends it to backend        |
| FR-2 | **ASR (Speech-to-Text)**     | Convert speech to text using Whisper                             |
| FR-3 | **NLU & Dialogue**           | Parse intent/entities using Rasa; manage multi-turn conversation |
| FR-4 | **Business Logic Execution** | Execute logic for policy status, claim creation, authentication  |
| FR-5 | **TTS (Text-to-Speech)**     | Convert agent’s reply text to speech                             |
| FR-6 | **Frontend Interaction**     | Browser client for push-to-talk and audio playback               |
| FR-7 | **Logging & Audit**          | Log ASR text, NLU output, responses, timestamps                  |
| FR-8 | **Error Handling**           | Detect and recover from missing input, unrecognized intent       |

### 1.5 Non-Functional Requirements

| Type            | Requirement                                                 |
| --------------- | ----------------------------------------------------------- |
| Performance     | End-to-end speech latency < 1 s (target < 500 ms with GPU)  |
| Accuracy        | ≥ 90 % ASR WER for clean audio; ≥ 95 % intent accuracy      |
| Reliability     | Should gracefully degrade to text input if mic or TTS fails |
| Scalability     | Modular services (ASR, TTS, NLU) containerized for scaling  |
| Maintainability | All modules documented, with clear API boundaries           |
| Security        | No raw audio or customer data stored without consent        |

### 1.6 Constraints

* Must run locally (offline-capable) using open-source tools.
* Hardware: CPU (min 8 cores / 16 GB RAM); GPU optional for LLM/Whisper large.
* Internet optional (only for gTTS fallback or updates).

---

## ⚙️ 2. System Design Document (SDD)

### 2.1 High-Level Architecture

**Layers**

1. **Frontend (Browser)**

   * HTML/JS UI with push-to-talk button.
   * Captures mic input; sends to backend `/transcribe` endpoint.
   * Plays AI’s spoken reply.

2. **Backend (FastAPI)**

   * Endpoints:

     * `POST /transcribe` → Receives audio, runs ASR → Rasa → TTS → returns WAV.
     * `GET /health` → Basic health check.
   * Manages all pipeline orchestration and logging.

3. **NLU + Dialogue (Rasa)**

   * Detects **intent**, extracts **entities**, manages **dialog flow**.
   * Custom actions implement business logic (policy lookup, claim creation).

4. **ASR Engine (Whisper)**

   * Converts Tamil / English speech to text locally.
   * `small` or `medium` model used for fast inference.

5. **TTS Engine (Coqui / gTTS fallback)**

   * Converts Rasa responses to audio.
   * Returns playable WAV to frontend.

6. **Data Layer**

   * Local JSON/CSV store for mock policy and claim data.
   * Log file (`logs/conversations.jsonl`) for audit trail.

---

### 2.2 Data Flow Diagram

```
[User Mic]
   ↓
[Frontend JS] 
   ↓ (Audio Blob)
[FastAPI /transcribe]
   ↓
[Whisper ASR]
   ↓ (Text)
[Rasa NLU/Core]
   ↓ (Response Text)
[TTS Engine]
   ↓ (Audio File)
[Frontend Audio Player → User]
```

---

### 2.3 Component Diagram

```
Frontend
 ├── Mic Recorder
 ├── HTTP Client
 └── Audio Player
Backend (FastAPI)
 ├── ASR Module (whisper)
 ├── Rasa Client (REST API)
 ├── TTS Module (Coqui/gTTS)
 └── Logger
Rasa Core
 ├── NLU (intent/entity)
 ├── Dialogue Manager
 └── Actions (custom business logic)
```

---

### 2.4 Database / Storage Design

| Data              | Storage                               | Format |
| ----------------- | ------------------------------------- | ------ |
| Conversation logs | Local file                            | JSONL  |
| Claims            | Local file `rasa_claims/claims.jsonl` | JSONL  |
| Mock policy data  | JSON or SQLite (future)               | JSON   |

Example claim entry:

```json
{
  "claim_ref": "CLM-12AB34CD",
  "policy_id": "POL-12345",
  "incident_type": "Accident",
  "incident_date": "2025-10-01",
  "timestamp": "2025-11-10T14:22:55Z"
}
```

---

### 2.5 Business Logic Flow

#### A. Policy Status Inquiry

1. User: “Check my policy number 12345.”
2. ASR → “Check my policy number 12345.”
3. Rasa Intent: `policy_status`; Entity: `policy_id = 12345`
4. Action: Retrieve policy info from mock DB.
5. Reply: “Your policy 12345 is active. Premium due 31-Dec-2025.”
6. TTS converts reply → audio → frontend playback.

#### B. Claim Filing

1. User: “I want to file a claim for theft on 1 Nov.”
2. Intent: `file_claim`; Entities: `incident_type = theft`, `incident_date = 2025-11-01`.
3. Action: Generate claim_ref = `CLM-XYZ123`.
4. Store in `claims.jsonl`.
5. Respond: “Your claim has been created. Reference CLM-XYZ123.”

#### C. Authentication Flow

1. Bot: “Please provide your policy ID.”
2. User: “POL-56789.”
3. Slot `policy_id` filled.
4. Proceed to policy or claim flow.

---

### 2.6 API Contract

| Endpoint                      | Method | Request                          | Response             |
| ----------------------------- | ------ | -------------------------------- | -------------------- |
| `/transcribe`                 | POST   | multipart/form-data (audio file) | `audio/wav`          |
| `/health`                     | GET    | —                                | `{ "status": "ok" }` |
| `Rasa /webhooks/rest/webhook` | POST   | `{sender, message}`              | `[{text: "..."}]`    |

---

### 2.7 Error Handling

| Case                  | Action                                               |
| --------------------- | ---------------------------------------------------- |
| ASR failure / silence | Return “I couldn’t hear you clearly, please repeat.” |
| Rasa timeout          | Return generic fallback text                         |
| TTS failure           | Return text response instead of audio                |

---

### 2.8 Logging & Monitoring

* Each turn logged with timestamp, transcript, intent, entities, response text, latency.
* Log file location: `logs/conversations.jsonl`.
* Sample:

```json
{
  "time": "2025-11-11T16:32:05Z",
  "asr_text": "Check my policy",
  "intent": "policy_status",
  "entities": {"policy_id": "12345"},
  "response": "Your policy 12345 is ACTIVE."
}
```

---

## 📊 3. Impact Analysis

| Aspect                  | Impact                               | Explanation                                      |
| ----------------------- | ------------------------------------ | ------------------------------------------------ |
| **Business Efficiency** | ↓ call-center load (~80 %)           | Automates routine insurance queries              |
| **Customer Experience** | 24×7 instant bilingual support       | Natural voice interactions in Tamil + English    |
| **Market Expansion**    | Access to Tamil-speaking demographic | First-mover advantage in regional CX             |
| **Operational Costs**   | Lower support cost                   | Fewer human agents needed for FAQs               |
| **Technical Risk**      | Moderate                             | Dependent on ASR/TTS accuracy and latency        |
| **Data Privacy**        | High importance                      | All processing local; no external API dependency |

---

## 🧩 4. Architecture Summary

**Type:** Modular, loosely coupled micro-modules (backend ↔ Rasa ↔ ASR ↔ TTS)
**Technology Stack:**

| Layer        | Tool                          | Purpose                               |
| ------------ | ----------------------------- | ------------------------------------- |
| Frontend     | HTML / JS                     | Mic capture + audio playback          |
| Backend      | FastAPI (Python 3.10)         | API gateway / orchestration           |
| ASR          | OpenAI Whisper (small/medium) | Speech → text                         |
| NLU + Dialog | Rasa 3.6                      | Intent/entity detection + policy flow |
| TTS          | Coqui / gTTS                  | Text → speech                         |
| Data Store   | JSON / SQLite (optional)      | Claims + logs                         |
| DevOps       | VS Code + GitHub              | CI/CD + versioning                    |

---

## 🔄 5. Sequence Flow (Unified View)

```
User Speaks ─► Frontend (Audio)
                │
                ▼
         FastAPI /transcribe
                │
                ▼
          Whisper ASR → Text
                │
                ▼
          Rasa NLU/Core → Intent/Entities
                │
                ▼
         Business Logic (Action)
                │
                ▼
          TTS → Speech Output
                │
                ▼
             Frontend → Play reply
```

---

## 🧮 6. Business Logic Table

| Intent          | Trigger Phrase Examples                        | Slots / Entities                 | Action / Response                             |
| --------------- | ---------------------------------------------- | -------------------------------- | --------------------------------------------- |
| `greet`         | “Hi”, “வணக்கம்”                                | —                                | utter_greet                                   |
| `policy_status` | “Check my policy”, “என் போலிசி நிலை சொல்லுங்க” | `policy_id`                      | utter_ask_policy → utter_policy_status        |
| `file_claim`    | “File a claim for accident”                    | `incident_type`, `incident_date` | utter_ask_claim_details → action_create_claim |
| `authenticate`  | “My policy id is 12345”                        | `policy_id`                      | Slot fill → Next intent                       |
| `goodbye`       | “Thanks”, “Bye”                                | —                                | utter_goodbye                                 |

---

## 🧰 7. Development & Deployment Notes

### Local Development Workflow

```bash
# (1) Start Rasa
cd rasa_project
rasa train
rasa run --enable-api --cors "*"
rasa run actions

# (2) Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# (3) Serve frontend
cd frontend
python -m http.server 5500
```

### Git Workflow

| Branch                 | Purpose                |
| ---------------------- | ---------------------- |
| `main`                 | stable / release       |
| `dev`                  | active development     |
| `feature/rasa-intents` | intent and NLU updates |
| `feature/tts`          | audio enhancements     |

---

## 📈 8. Future Enhancements

| Area                         | Upgrade                                           |
| ---------------------------- | ------------------------------------------------- |
| **Realtime Voice Streaming** | Replace push-to-talk with LiveKit for full-duplex |
| **Tamil ASR Optimization**   | Swap Whisper → AI4Bharat IndicConformer           |
| **Natural TTS**              | Fine-tune VITS/Glow-TTS Tamil voice               |
| **LLM Reasoning**            | Integrate Ollama/vLLM for policy document Q&A     |
| **RAG Knowledge Base**       | ChromaDB + vector search                          |
| **Human Handoff**            | Dashboard for live agent takeover                 |
| **Messenger Integration**    | Add webhook for Facebook Messenger text+voice     |

---

## 📋 9. Deliverables Checklist

* [x] Functional prototype (Speech → Speech insurance assistant)
* [x] Rasa project (NLU + stories + actions)
* [x] FastAPI backend orchestration
* [x] Frontend mic UI
* [x] Logs + audit trail
* [x] Documentation (SRS + SDD + Impact Analysis + Architecture)

---

## 📑 10. Summary

The **Insurance Voice Agent** is a modular, locally hosted, bilingual conversational system capable of performing real insurance workflows through speech. It unites ASR (Whisper), NLU (Rasa), TTS (Coqui/gTTS), and FastAPI orchestration in a lightweight architecture that can evolve toward full real-time streaming and enterprise integration.

---

### 📂 Suggested Folder Layout for Docs

```
docs/
├─ SRS.md
├─ SDD.md
├─ Impact_Analysis.md
├─ Architecture_Diagram.png
└─ Business_Flows.md
```

---

Would you like me to **generate editable `.md` or `.docx` templates** for each section (SRS, SDD, Impact Analysis) so you can directly push them into your repo?
I can also produce the **architecture diagrams (PNG / Mermaid)** to accompany these docs.
