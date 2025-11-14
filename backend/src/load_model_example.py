# # tamil_llama_conversational_agent.py
# # Single-file conversational loop that loads a gguf model once and keeps an interactive Tamil-English chat.
# # Uses llama-cpp-python (pip install llama-cpp-python) which supports gguf model files.
# # Tested pattern for Windows paths; adapt params to your runtime/bindings if you use a different library.

from llama_cpp import Llama
import os
import sys
import time

# --- CONFIG ---
MODEL_PATH = r"D:/RASA/Insurance_voice_agent/insurance-voice-bot/models/gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf"
# Max tokens to generate per assistant reply
MAX_NEW_TOKENS = 256
# Decoding settings (deterministic / low sampling to avoid repetitive "thinking loops")
TEMPERATURE = 0.2
TOP_P = 0.9
REPEAT_PENALTY = 1.2
STOP_SEQUENCES = ["\nUser:", "\nUser:", "\n\n"]

# System / assistant persona — keeps responses concise and avoids chain-of-thought
SYSTEM_PROMPT = (
"You are an AI assistant who follows instructions extremely well. Do your best your best to help." \
" Keep replies concise and to the point. Use English as appropriate." \
"Strictly give the response in English." 
)


# Initialize model once
print(f"Loading model from: {MODEL_PATH}")
llm = Llama(model_path=MODEL_PATH, n_gpu_layers=40, gpu_layers=True)
print("Model loaded — ready.")

# Chat history: list of (role, text). Keep small to avoid context length exhaustion.
chat_history = [("system", SYSTEM_PROMPT)]

# Helper to build prompt from history. Keep concise formatting.
def build_prompt(history, user_input=None):
    # Format roles clearly for the model
    parts = []
    for role, text in history:
        if role == "system":
            parts.append(f"System: {text}\n")
        elif role == "user":
            parts.append(f"User: {text}\n")
        elif role == "assistant":
            parts.append(f"Assistant: {text}\n")
    if user_input is not None:
        parts.append(f"User: {user_input}\nAssistant:")
    return "".join(parts)


def generate_reply(prompt):
    # llama-cpp-python returns dict with 'choices' list
    resp = llm(
        prompt=prompt,
        max_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        repeat_penalty=REPEAT_PENALTY,
        stop=STOP_SEQUENCES,
        echo=False,
    )

    # Extract text reliably
    try:
        text = resp["choices"][0]["text"]
    except Exception:
        # fallback for different llama-cpp-python versions
        choices = resp.get("choices") or []
        text = choices[0].get("text") if choices else ""

    # strip leading/trailing whitespace
    return text.strip()


def main_loop():
    print("Interactive Tamil-English conversational agent. Type 'exit' or 'quit' to stop.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        # Append user to history, build prompt and generate
        chat_history.append(("user", user_input))

        # Optionally truncate history to keep length manageable (simple rolling window)
        # Keep the system message + last N turns (user+assistant pairs)
        MAX_TURNS = 6  # tweak this depending on token limits
        sys_msg = [t for t in chat_history if t[0] == "system"]
        non_sys = [t for t in chat_history if t[0] != "system"]
        if len(non_sys) > MAX_TURNS * 2:
            non_sys = non_sys[-MAX_TURNS * 2 :]
        history_for_prompt = sys_msg + non_sys

        prompt = build_prompt(history_for_prompt, user_input=None)
        # We pass the current user turn to build_prompt so assistant is asked to continue
        prompt = build_prompt(history_for_prompt, user_input)

        # Generate
        start = time.time()
        reply = generate_reply(prompt)
        duration = time.time() - start

        # Append assistant reply to history and print
        chat_history.append(("assistant", reply))
        print(f"Assistant: {reply}\n  — ({duration:.2f}s)")


if __name__ == "__main__":
    main_loop()


# from llama_cpp import Llama
# import os

# model_path = r"D:/RASA/Insurance_voice_agent/insurance-voice-bot/models/tamil-llama-7b-instruct-v0.1.Q4_K_S.gguf"

# if not os.path.exists(model_path):
#     raise FileNotFoundError(f"Model not found at {model_path}")

# # Basic CPU load:
# # llm = Llama(model_path=model_path)

# # If you have a GPU build of llama-cpp-python, you can try:
# llm = Llama(model_path=model_path, n_gpu_layers=80, gpu_layers=True)
# # or
# # llm = Llama(model_path=model_path, n_gpu_layers=50)  # tune n_gpu_layers to push layers to GPU

# # Quick test prompt
# resp = llm(prompt="Hello. Generate a 1-line Tamil-English greeting.", max_tokens=64)
# print(resp)
