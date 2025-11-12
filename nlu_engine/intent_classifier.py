"""Intent classifier using SentenceTransformers embeddings (bilingual: Tamil+English)."""

from typing import Dict, List, Tuple
import json

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class IntentClassifier:
    """Embedding-based intent classifier for bilingual insurance queries.
    
    Supports two runtime modes:
    1. Embedding-based (SentenceTransformers) - lightweight, CPU-friendly
    2. LLM-based (via llm_runner) - more powerful, for complex queries
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize the classifier with a multilingual embedding model.
        
        Args:
            model_name: HuggingFace model for embeddings (default supports 100+ languages).
        """
        self.model_name = model_name
        self.model = None
        self.intent_embeddings = {}
        self.intent_labels = []
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
        else:
            print(f"Warning: sentence-transformers not available. Install via: pip install sentence-transformers")
    
    def add_intent(self, intent_label: str, examples: List[str]):
        """Register an intent with example queries (Tamil/English or mixed).
        
        Args:
            intent_label: Unique intent identifier (e.g., 'ask_claim_status').
            examples: List of example queries in Tamil, English, or both.
        """
        if not self.model:
            print(f"Model not loaded. Cannot add intent '{intent_label}'.")
            return
        
        self.intent_labels.append(intent_label)
        embeddings = self.model.encode(examples, convert_to_tensor=False)
        # Average embeddings for this intent
        self.intent_embeddings[intent_label] = embeddings.mean(axis=0)
    
    def classify(self, query: str, threshold: float = 0.5) -> Dict[str, any]:
        """Classify a query (Tamil/English) to an intent.
        
        Args:
            query: User query in Tamil, English, or mixed.
            threshold: Confidence threshold (0-1). Below this, returns 'unknown_intent'.
        
        Returns:
            {
              "intent": "ask_claim_status" | "unknown_intent",
              "confidence": 0.87,
              "alternatives": [("ask_policy", 0.45), ...]
            }
        """
        if not self.model or not self.intent_embeddings:
            return {"intent": "unknown_intent", "confidence": 0.0, "alternatives": []}
        
        query_embedding = self.model.encode(query, convert_to_tensor=False)
        
        scores = {}
        for intent_label, intent_emb in self.intent_embeddings.items():
            # Cosine similarity
            score = self._cosine_sim(query_embedding, intent_emb)
            scores[intent_label] = score
        
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_score = sorted_intents[0] if sorted_intents else ("unknown_intent", 0.0)
        
        if top_score < threshold:
            top_intent = "unknown_intent"
        
        alternatives = sorted_intents[1:] if len(sorted_intents) > 1 else []
        
        return {
            "intent": top_intent,
            "confidence": float(top_score),
            "alternatives": [(label, float(score)) for label, score in alternatives[:3]]
        }
    
    @staticmethod
    def _cosine_sim(a, b) -> float:
        """Compute cosine similarity between two vectors."""
        import numpy as np
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    
    def load_intents_from_file(self, filepath: str):
        """Load intents from a JSON file.
        
        Format:
        {
          "ask_claim_status": [
            "What is the status of my claim?",
            "என் கோரிக்கையின் நிலை என்ன?"
          ],
          ...
        }
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            intents_dict = json.load(f)
        
        for intent_label, examples in intents_dict.items():
            self.add_intent(intent_label, examples)
