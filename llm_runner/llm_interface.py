"""Abstract LLM interface and lightweight runner for local models."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List


class LLMRunner(ABC):
    """Abstract base class for LLM runners (CPU, GPU, or llama.cpp backends)."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: Input prompt (Tamil, English, or mixed).
            max_tokens: Max output length.
        
        Returns:
            Generated response text.
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str):
        """Load a model from disk.
        
        Args:
            model_path: Path to model file (e.g., GGUF for llama.cpp).
        """
        pass


class LlamaCppRunner(LLMRunner):
    """Runner using llama.cpp (CPU-optimized, GGUF format)."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize llama.cpp runner.
        
        Args:
            model_path: Path to .gguf model file (e.g., mistral-7b-instruct.gguf).
        """
        self.model_path = model_path
        self.llm = None
        
        try:
            from llama_cpp import Llama
            self.Llama = Llama
        except ImportError:
            print("Warning: llama-cpp-python not installed. Run: pip install llama-cpp-python")
            self.Llama = None
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load a GGUF model."""
        if not self.Llama:
            print("Cannot load model: llama-cpp-python not available.")
            return
        
        self.model_path = model_path
        self.llm = self.Llama(model_path=model_path, n_ctx=2048, n_threads=4)
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response using llama.cpp."""
        if not self.llm:
            return "[Error: Model not loaded]"
        
        response = self.llm(prompt, max_tokens=max_tokens, temperature=0.7, top_p=0.9)
        return response['choices'][0]['text']


class TransformersRunner(LLMRunner):
    """Runner using HuggingFace transformers (GPU-optional with bitsandbytes)."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize transformers runner.
        
        Args:
            model_name: HuggingFace model name (e.g., 'mistralai/Mistral-7B-Instruct-v0.1').
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.AutoModelForCausalLM = AutoModelForCausalLM
            self.AutoTokenizer = AutoTokenizer
        except ImportError:
            print("Warning: transformers not installed. Run: pip install transformers torch")
            self.AutoModelForCausalLM = None
            self.AutoTokenizer = None
        
        if model_name:
            self.load_model(model_name)
    
    def load_model(self, model_name: str):
        """Load a model from HuggingFace."""
        if not self.AutoModelForCausalLM or not self.AutoTokenizer:
            print("Cannot load model: transformers or torch not available.")
            return
        
        self.model_name = model_name
        self.tokenizer = self.AutoTokenizer.from_pretrained(model_name)
        
        # Optionally use bitsandbytes for 8-bit quantization on GPU
        try:
            self.model = self.AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                load_in_8bit=True  # Requires bitsandbytes + GPU
            )
        except:
            # Fallback to CPU
            self.model = self.AutoModelForCausalLM.from_pretrained(model_name)
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response using transformers."""
        if not self.model or not self.tokenizer:
            return "[Error: Model not loaded]"
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=max_tokens, temperature=0.7, top_p=0.9)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


class MockLLMRunner(LLMRunner):
    """Mock LLM for testing / development (returns hardcoded responses)."""
    
    def __init__(self):
        """Initialize mock runner."""
        self.responses = {}
    
    def load_model(self, model_path: str):
        """No-op for mock."""
        pass
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Return mock response based on keyword matching."""
        prompt_lower = prompt.lower()
        
        if "claim" in prompt_lower or "கோரிக்கை" in prompt:
            return "Your claim is currently under review. You will be notified within 5-7 business days."
        elif "policy" in prompt_lower or "பாலிசி" in prompt:
            return "Your policy is active and valid till 31-Dec-2025."
        else:
            return "[Mock response] I'm here to help with your insurance queries."
