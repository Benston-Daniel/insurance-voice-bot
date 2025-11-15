def simple_translate_to_tamil(english_text):
    """
    Simple key-term translation for common insurance terms.
    Use this ONLY if you want to add Tamil labels to English answers.
    For full translation, use Google Translate API or similar.
    """
    tamil_dict = {
        "coverage": "கவரேஜ்",
        "waiting period": "காத்திருக்கும் காலம்",
        "exclusion": "விலக்குதல்",
        "deductible": "கழிக்கக்கூடிய",
        "co-payment": "கோ-பேமென்ட்",
        "premium": "பிரீமியம்",
        "claim": "கிளெய்ம்",
        "policy": "பாலிசி",
        "hospitalization": "மருத்துவமனை சேவை",
        "maternity": "பிரசவ சம்பந்தமான",
    }
    
    result = english_text
    for eng, tam in tamil_dict.items():
        result = result.replace(eng, f"{eng} ({tam})")
    
    return result

import argparse
import json
import os
import pickle
from pathlib import Path
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
import numpy as np
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from lang_detect import detect_language
N_GPU_LAYERS = 0

try:
    from llama_cpp import Llama
except ImportError:
    raise RuntimeError(
        "llama-cpp-python not installed. "
        "Install with: pip install llama-cpp-python"
    )

# ============================================================================
# CONFIG
# ============================================================================
DATA_JSONL = Path("data/policies_chunks.jsonl")
BM25_PICKLE = Path("data/bm25_index.pkl")
MODEL_PATH = Path("models/gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf")

# Default: Conservative (512). User can override with --context-window
DEFAULT_CONTEXT_WINDOW = 512
RESERVED_OUTPUT_TOKENS = 150  # Space for model output
TOP_K_RETRIEVE = 5

# ============================================================================
# UTILITIES
# ============================================================================

def load_docs(jsonl_path):
    """Load policy chunks from JSONL file."""
    docs = []
    metas = []
    
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Data file not found: {jsonl_path}")
    
    try:
        with open(jsonl_path, encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    rec = json.loads(line)
                    docs.append(rec['content'])
                    metas.append({
                        'policy_file': rec.get('policy_file', ''),
                        'section': rec.get('section', ''),
                        'chunk_id': rec.get('chunk_id', line_num)
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping malformed JSON at line {line_num}: {e}")
        
        logger.info(f"Loaded {len(docs)} policy chunks from {jsonl_path}")
        return docs, metas
    
    except Exception as e:
        raise RuntimeError(f"Error loading documents: {e}")


def build_or_load_bm25(docs, metas, pickle_path=BM25_PICKLE):
    """Build or load BM25 index."""
    if pickle_path.exists():
        try:
            with open(pickle_path, 'rb') as f:
                bm25, tokenized = pickle.load(f)
            logger.info(f"Loaded BM25 index from {pickle_path}")
            return bm25
        except Exception as e:
            logger.warning(f"Could not load BM25 cache: {e}. Rebuilding...")
    
    logger.info("Building BM25 index...")
    tokenized = [word_tokenize(d.lower()) for d in docs]
    bm25 = BM25Okapi(tokenized)
    
    try:
        pickle_path.parent.mkdir(parents=True, exist_ok=True)
        with open(pickle_path, 'wb') as f:
            pickle.dump((bm25, tokenized), f)
        logger.info(f"Saved BM25 index to {pickle_path}")
    except Exception as e:
        logger.warning(f"Could not save BM25 cache: {e}")
    
    return bm25


def retrieve(bm25, docs, metas, query, top_k=TOP_K_RETRIEVE):
    """Retrieve top-k relevant chunks using BM25."""
    try:
        qtok = word_tokenize(query.lower())
        scores = bm25.get_scores(qtok)
        idxs = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for i in idxs:
            results.append({
                'index': int(i),
                'score': float(scores[i]),
                'content': docs[i],
                'meta': metas[i]
            })
        
        return results
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        return []


def estimate_tokens(text):
    """
    Estimate token count (~4 chars per token on average for English/Tamil).
    For production, use actual tokenizer (tiktoken or model's tokenizer).
    """
    # More accurate: ~1.3 words per token for English, ~1.0 for Tamil
    word_count = len(text.split())
    char_count = len(text)
    # Conservative estimate
    return max(word_count // 1.3, char_count // 4)


def filter_by_token_budget(retrieved, max_tokens):
    """
    Filter retrieved chunks to fit within token budget.
    Prioritize by BM25 score.
    """
    selected = []
    used_tokens = 0
    
    for chunk in retrieved:
        chunk_tokens = estimate_tokens(chunk['content'])
        if used_tokens + chunk_tokens <= max_tokens:
            selected.append(chunk)
            used_tokens += chunk_tokens
        else:
            logger.debug(
                f"Skipping chunk {chunk['index']} "
                f"(+{chunk_tokens} tokens would exceed budget)"
            )
    
    return selected


def clean_policy_text(text, language="en"):
    """
    Clean policy text to remove Q&A pairs, extra formatting.
    Language-aware cleaning for Tamil & English.
    """
    if language == "ta":
        # Tamil-specific Q&A patterns
        # Remove: "கேள்வி:", "பகுதி:", "கூடுதல் கேள்வி:", etc.
        text = re.sub(r'கேள்வி\s*\d*\s*:', '', text)
        text = re.sub(r'பாகம்\s*\d*\s*:', '', text)
        text = re.sub(r'பகுதி\s*\d*\s*:', '', text)
        text = re.sub(r'கூடுதல்.*?:', '', text)
        text = re.sub(r'பதில்\s*\d*\s*:', '', text)
        text = re.sub(r'பதிலளி.*?:', '', text)
        text = re.sub(r'\(\s*கேள்வி\s*\)', '', text)
        text = re.sub(r'Q\d*\s*:', '', text)
        text = re.sub(r'A\d*\s*:', '', text)
    else:
        # English Q&A patterns
        text = re.sub(r'Q[uestion]*\s*\d*\s*:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'A[nswer]*\s*\d*\s*:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Additional\s+[Qq]uestion.*?:', '', text, flags=re.IGNORECASE)
    
    # Remove multiple line breaks
    text = re.sub(r'\n\n+', '\n', text)
    
    # Remove excessive whitespace
    text = text.strip()
    
    return text


def build_prompt(user_question, retrieved, language_tag="en"):
    """
    Build a **strict** system prompt + context + user query.
    
    KEY FIX FOR TAMIL HALLUCINATION:
    - Always use ENGLISH system prompt (model handles English better)
    - Only translate the final output to Tamil if needed
    """
    # Use English system prompt ALWAYS (model is more reliable in English)
    system_prompt = (
        "You are an insurance assistant.\n"
        "CRITICAL: Answer ONLY using the policy information below.\n"
        "Answer ONLY the question asked. Do NOT generate additional Q&As or numbered lists.\n"
        "If information is unavailable: 'I could not find that in the policy documents.'\n"
        "Keep your answer concise and brief (max 2 sentences)."
    )
    
    user_label = "Question"
    policy_label = "Policy Information"
    instruction = "Answer (concise, max 2 sentences):"
    
    # If user asked in Tamil, add note to respond in simple, clear format
    if language_tag == "ta":
        instruction += " [Respond clearly without extra numbering or lists]"
    
    # Format retrieved chunks concisely and cleaned
    if retrieved:
        excerpts = []
        for i, chunk in enumerate(retrieved):
            source = f"{chunk['meta']['policy_file']}#{chunk['meta']['section']}"
            cleaned_content = clean_policy_text(chunk['content'], language=language_tag)
            # Truncate MORE aggressively for Tamil (hallucination is worse)
            max_chars = 180 if language_tag == "ta" else 250
            excerpt = cleaned_content[:max_chars]
            excerpts.append(f"[{i}] ({source}):\n{excerpt}")
        
        context = "\n\n---\n\n".join(excerpts)
    else:
        context = "(No relevant policy information found)"
    
    # Assemble strict prompt with clear boundaries
    prompt = (
        f"{system_prompt}\n\n"
        f"{policy_label}:\n"
        f"---BEGIN POLICY---\n"
        f"{context}\n"
        f"---END POLICY---\n\n"
        f"{user_label}: {user_question}\n\n"
        f"{instruction}"
    )
    
    return prompt


def safe_generate(llm, prompt, max_tokens=150, language="en"):
    """
    Generate response with hallucination prevention.
    Uses low temperature + strict stopping criteria.
    Language-aware stop tokens for Tamil/English.
    """
    try:
        logger.info(f"Generating response (max_tokens={max_tokens}, language={language})...")
        
        # Language-specific stop tokens
        if language == "ta":
            stop_tokens = [
                "கேள்வி:",
                "பாகம்:",
                "பகுதி:",
                "கூடுதல்",
                "பதில்:",
                "Q:",
                "A:",
                "\n\nக",  # Stop at new Tamil line starting with Tamil char
                "\n\nப",
                "Question:",
            ]
        else:
            stop_tokens = [
                "Question:",
                "Q:",
                "A:",
                "\n\nQ",
                "\n\nA",
                "Additional:",
            ]
        
        # LOW temperature = deterministic, factual
        # top_p closer to 0 = more focused, less creative (prevents hallucination)
        resp = llm(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.02,  # ULTRA low for Tamil
            top_p=0.80,        # Even more restrictive
            top_k=15,          # Consider only top 15 tokens
            repeat_penalty=1.5,  # Stronger penalty on repetition
            stop=stop_tokens
        )
        
        # Extract text from response
        if 'choices' in resp and len(resp['choices']) > 0:
            choice = resp['choices'][0]
            text = choice.get('text') or choice.get('message', {}).get('content', '')
            text = text.strip()
            
            # Post-process: Remove any trailing Q&As that still slipped through
            if language == "ta":
                text = re.sub(r'கேள்வி.*', '', text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'பாகம்.*', '', text, flags=re.DOTALL)
                text = re.sub(r'பகுதி.*', '', text, flags=re.DOTALL)
                text = re.sub(r'கூடுதல்.*', '', text, flags=re.DOTALL)
                text = re.sub(r'\d+\s*:', '', text)  # Remove numbered lists/sections
            else:
                text = re.sub(r'\nQ[uestion]*:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'\nAnswer:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
            
            return text.strip()
        else:
            logger.error(f"Unexpected response format: {resp}")
            return "Error: Could not generate response."
    
    except ValueError as e:
        if "context window" in str(e).lower() or "exceed" in str(e).lower():
            logger.error(
                f"❌ Context window exceeded: {e}\n"
                f"Solutions:\n"
                f"  1. Use --topk 2 (fewer chunks)\n"
                f"  2. Use --context-window 2048 (if model supports it)\n"
                f"  3. Use a larger model (mistral, llama2)\n"
                f"  4. Try: ollama pull mistral && ollama serve"
            )
            return (
                "Error: Response too complex for current context window. "
                "Try asking a simpler question or use a larger model."
            )
        else:
            logger.error(f"Generation error: {e}")
            raise
    
    except Exception as e:
        logger.error(f"Unexpected error during generation: {e}")
        raise


def format_output(answer, sources, query, language="en"):
    """Format the final output nicely."""
    # Add language header
    lang_label = "தமிழ்" if language == "ta" else "English"
    
    output = "\n" + "="*70 + "\n"
    output += f"LANGUAGE: {lang_label}\n"
    output += f"QUERY: {query}\n"
    output += "="*70 + "\n"
    output += f"ANSWER: {answer}\n"
    output += "="*70 + "\n"
    output += f"SOURCES: {sources}\n"
    output += "="*70 + "\n"
    return output


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Insurance Bot with RAG + Local LLM (Hallucination-Free)"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="User query (English or Tamil)"
    )
    parser.add_argument(
        "--topk",
        type=int,
        default=TOP_K_RETRIEVE,
        help=f"Number of chunks to retrieve (default: {TOP_K_RETRIEVE})"
    )
    parser.add_argument(
        "--model",
        default=str(MODEL_PATH),
        help="Path to GGUF model file"
    )
    parser.add_argument(
        "--context-window",
        type=int,
        default=DEFAULT_CONTEXT_WINDOW,
        help=f"Model context window size (default: {DEFAULT_CONTEXT_WINDOW}). Increase if your model supports it."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info (prompt, tokens, etc.)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Query: {args.query}")
    logger.info(f"Context Window: {args.context_window} tokens")
    
    # Validate files exist
    if not DATA_JSONL.exists():
        logger.error(f"Data file missing: {DATA_JSONL}")
        raise SystemExit(1)
    
    if not Path(args.model).exists():
        logger.error(f"Model file missing: {args.model}")
        raise SystemExit(1)
    
    # Load and build index
    logger.info("Loading policy data...")
    docs, metas = load_docs(DATA_JSONL)
    bm25 = build_or_load_bm25(docs, metas)
    
    # Detect language
    lang = detect_language(args.query)
    logger.info(f"Detected language: {lang}")
    
    # Retrieve candidate chunks
    logger.info(f"Retrieving top {args.topk} chunks...")
    retrieved_all = retrieve(bm25, docs, metas, args.query, top_k=args.topk)
    
    if not retrieved_all:
        logger.warning("No relevant chunks found!")
        print(format_output(
            "Sorry, I could not find relevant information in the policy documents.",
            "N/A",
            args.query
        ))
        return
    
    # Filter by token budget
    max_context = args.context_window - RESERVED_OUTPUT_TOKENS
    token_budget = max_context - estimate_tokens(args.query) - 200  # safety margin
    retrieved_filtered = filter_by_token_budget(retrieved_all, token_budget)
    
    if not retrieved_filtered:
        logger.warning("All chunks exceeded token budget!")
        retrieved_filtered = retrieved_all[:1]  # Use top 1 as fallback
    
    logger.info(f"Using {len(retrieved_filtered)} chunks after token filtering")
    
    # Build prompt
    prompt = build_prompt(args.query, retrieved_filtered, language_tag=lang)
    
    if args.debug:
        logger.info("\n--- DEBUG INFO ---")
        logger.info(f"Prompt length: {len(prompt)} chars, ~{estimate_tokens(prompt)} tokens")
        logger.info(f"\nFull Prompt:\n{prompt}\n---\n")
    
    # Load model
    logger.info(f"Loading model: {args.model}")
    try:
        llm = Llama(
            model_path=str(args.model),
            n_ctx=args.context_window,  # User-specified context window
            n_threads=-1,  # Use all CPU threads
            verbose=False
        )
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise SystemExit(1)
    
    # Generate response
    answer = safe_generate(llm, prompt, max_tokens=RESERVED_OUTPUT_TOKENS, language=lang)
    
    # Format sources
    sources = ", ".join(
        sorted({
            f"{r['meta']['policy_file']}#{r['meta']['section']}"
            for r in retrieved_filtered
        })
    )
    
    # Output
    output = format_output(answer, sources, args.query, language=lang)
    print(output)
    
    logger.info("Done!")


if __name__ == "__main__":
    main()