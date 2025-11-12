# Cleanup Log: Rasa → Lightweight NLU+LLM Migration

## Date: November 11, 2025

### Summary
Successfully removed all Rasa artifacts and scaffolded a new lightweight, local LLM-based NLU + agent architecture for the Insurance Voice Bot (bilingual Tamil+English).

---

## ❌ Deleted Items

### 1. **Rasa Project** (`rasa_project/`)
   - **Contents removed:**
     - `data/nlu.yml` — NLU intents
     - `data/stories.yml` — dialogue stories
     - `domain.yml` — Rasa domain
     - `actions.py` — custom actions
     - `endpoints.yml` — action server endpoint config
   - **Reason:** Replaced with lightweight SentenceTransformers embeddings + local LLM runner
   - **Backup:** None (scaffold includes intent examples in `data/intents_bilingual.json`)

### 2. **Rasa Virtual Environment** (`rasa/`)
   - **Contents:** Python venv with Rasa SDK and dependencies
   - **Reason:** No longer needed; new venv created via `scripts/setup_venv.ps1` / `setup_venv.sh`
   - **Size freed:** ~500MB (estimated)

### 3. **Rasa Cache** (`.rasa/`)
   - **Contents:** Rasa model cache and temporary files
   - **Reason:** Stale cache; not applicable to new architecture
   - **Size freed:** ~100MB+ (estimated)

### 4. **Docker Compose Rasa Services** (in `docker-compose.yml`)
   - **Removed services:**
     - `rasa` (Rasa NLU server)
     - `action_server` (Rasa SDK actions)
   - **Updated:** Backend service now self-contained (no external dependencies)
   - **New environment vars:** `NLU_ENGINE`, `LLM_MODEL_NAME`

### 5. **Rasa Client Module** (in `backend/app/rasa_client.py`)
   - **Status:** Kept but deprecated (not used in new flow)
   - **Note:** Can be safely deleted in future refactoring

---

## ✅ Scaffolded Items

### 1. **NLU Engine** (`nlu_engine/`)
   - **Files:**
     - `__init__.py` — module init
     - `intent_classifier.py` — SentenceTransformers-based bilingual intent classifier
   - **Features:**
     - Multilingual embeddings (100+ languages, including Tamil)
     - Cosine similarity matching
     - Confidence thresholding
     - JSON-based intent configuration

### 2. **LLM Runner** (`llm_runner/`)
   - **Files:**
     - `__init__.py` — module init
     - `llm_interface.py` — abstract base + concrete runners
   - **Runners:**
     - `MockLLMRunner` — hardcoded responses (test mode)
     - `LlamaCppRunner` — CPU-optimized GGUF inference (llama.cpp)
     - `TransformersRunner` — HuggingFace transformers (CPU/GPU with bitsandbytes)

### 3. **Backend Updates** (`backend/app/`)
   - **New files:**
     - `orchestrator.py` — `InsuranceAgent` class (NLU + LLM + intent routing)
   - **Updated files:**
     - `main.py` — Rewired FastAPI endpoints to use new orchestrator
     - Endpoints: `/health`, `/query`, `/voice`
   - **Removed dependency:** `rasa_client.py` (deprecated)

### 4. **Data** (`data/`)
   - **Files:**
     - `intents_bilingual.json` — Intent examples (Tamil+English) with 7 sample intents
     - `mock_policies.json` — Mock insurance policy data (2 samples)
     - `mock_claims.json` — Mock claims data (2 samples)
   - **Features:** Bilingual support; easily extensible

### 5. **Scripts** (`scripts/`)
   - **Files:**
     - `setup_venv.ps1` — PowerShell venv setup (Windows)
     - `setup_venv.sh` — Bash venv setup (Linux/Mac)
   - **Features:**
     - Automatic venv creation
     - Interactive backend selection (SentenceTransformers, llama-cpp, transformers)
     - Dependency installation

### 6. **Models** (`models/README.md`)
   - **Content:**
     - Three runtime options with download instructions
     - Model recommendations (Mistral-7B, Llama-2-7B, etc.)
     - HuggingFace authentication steps
     - Bilingual support notes
     - File size reference table

### 7. **Documentation**
   - **Project README.md:** Comprehensive architecture, API docs, testing, development guide
   - **.gitignore:** Updated to exclude Rasa folders, models, venv, audio files, etc.
   - **docker-compose.yml:** Simplified to backend only

---

## 📊 Architecture Changes

### Before (Rasa-based)
```
Frontend → FastAPI Backend → Rasa Server (NLU) → Rasa Action Server
                                      ↓
                           Intent Routing → Policy/Claims Lookup
```

### After (Lightweight NLU+LLM)
```
Frontend → FastAPI Backend → SentenceTransformers (Intent) → Intent Handler
                                      ↓
                              Policy/Claims Lookup OR LLM Fallback
```

**Benefits:**
- ❌ No external Rasa server needed
- ❌ No Docker dependency for NLU
- ✅ Embeddings-based NLU (fast, accurate)
- ✅ Local LLM support (CPU/GPU optional)
- ✅ Lightweight, edge-device friendly
- ✅ Easier to debug and customize

---

## 🔄 Migration Checklist

- [x] Delete `rasa_project/`, `rasa/`, `.rasa/`
- [x] Remove Rasa services from docker-compose.yml
- [x] Create `nlu_engine/` module
- [x] Create `llm_runner/` module
- [x] Create `orchestrator.py` (insurance agent)
- [x] Update `main.py` (FastAPI endpoints)
- [x] Create bilingual intent examples (`data/intents_bilingual.json`)
- [x] Create setup scripts (`setup_venv.ps1`, `setup_venv.sh`)
- [x] Create models guide (`models/README.md`)
- [x] Update project README
- [x] Update docker-compose.yml
- [x] Update `.gitignore`
- [x] Create cleanup log (this file)

---

## 🚀 Next Steps for Users

1. **Setup venv:**
   ```powershell
   # Windows
   .\scripts\setup_venv.ps1
   ```
   ```bash
   # Linux/Mac
   chmod +x scripts/setup_venv.sh
   ./scripts/setup_venv.sh
   ```

2. **Choose LLM backend** (see `models/README.md`):
   - Mock (no download) → fastest to test
   - llama-cpp (GGUF) → CPU-friendly
   - Transformers → GPU-accelerated (optional)

3. **Run backend:**
   ```bash
   export LLM_BACKEND=mock  # or llama-cpp, transformers
   python backend/app/main.py
   ```

4. **Test API:**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"message": "என் பாலிசி நிலை என்ன?"}'
   ```

---

## 📝 Notes

- **Backward Compatibility:** Rasa `.yml` files are NOT compatible with new architecture. Adapt intents to `data/intents_bilingual.json`.
- **Custom Intents:** Add new intents in `data/intents_bilingual.json` and corresponding handlers in `backend/app/orchestrator.py`.
- **Database Integration:** Replace mock policies/claims with real DB queries in `orchestrator.py`.
- **Model Updates:** To add LLM support, download a model and update `LLM_BACKEND` and `MODEL_PATH` environment variables.

---

## 📞 Support

For issues or questions:
1. Check `models/README.md` for model-related setup
2. Review `backend/app/orchestrator.py` for architecture details
3. Test endpoints at `http://localhost:8000/docs` (Swagger UI)

---

**Status:** ✅ Migration Complete  
**Tested:** Basic syntax check passed  
**Ready for:** Development / Model Integration
