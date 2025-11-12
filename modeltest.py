from llama_cpp import Llama
llm = Llama(model_path="D:\RASA\Insurance_voice_agent\insurance-voice-bot\models\Qwen3-4B-tamil-16bit-Instruct.i1-Q4_K_S.gguf", n_ctx=4096, n_gpu_layers=35)
resp = llm("### Instruction: Respond as an insurance assistant in Tamil or English.\n\nUser: Explain policy coverage for accident insurance.\n\nAssistant:", max_tokens=256)
print(resp["choices"][0]["text"])