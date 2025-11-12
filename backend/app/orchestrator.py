"""Orchestrator: integrates NLU classifier, LLM runner, and policy/claim databases."""

import json
from typing import Dict, Optional
import os

# Import from our NLU and LLM modules
try:
    from nlu_engine import IntentClassifier
    from llm_runner import LlamaCppRunner, TransformersRunner, MockLLMRunner
except ImportError:
    print("Warning: nlu_engine or llm_runner not available. Check PYTHONPATH.")


class InsuranceAgent:
    """Main insurance bot orchestrator (bilingual Tamil+English)."""
    
    def __init__(self, nlu_intents_path: str, llm_backend: str = "mock"):
        """Initialize the agent.
        
        Args:
            nlu_intents_path: Path to intents JSON file (e.g., data/intents_bilingual.json).
            llm_backend: One of "mock", "llama-cpp", "transformers".
        """
        self.classifier = IntentClassifier()
        self.llm = self._init_llm(llm_backend)
        
        # Load intents
        if os.path.exists(nlu_intents_path):
            self.classifier.load_intents_from_file(nlu_intents_path)
        
        # Load mock data
        self.policies = self._load_json("data/mock_policies.json", [])
        self.claims = self._load_json("data/mock_claims.json", [])
    
    def _init_llm(self, backend: str):
        """Initialize LLM runner based on backend choice."""
        if backend == "mock":
            return MockLLMRunner()
        elif backend == "llama-cpp":
            # Placeholder: user will download model manually
            return LlamaCppRunner(model_path=None)  # Set via env var or config
        elif backend == "transformers":
            # Placeholder: user can specify model name
            return TransformersRunner(model_name=None)
        else:
            return MockLLMRunner()
    
    @staticmethod
    def _load_json(path: str, default=None):
        """Load JSON safely."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default or {}
    
    def process_query(self, user_message: str, customer_id: Optional[str] = None) -> Dict:
        """Process a user query (Tamil/English) and return response.
        
        Args:
            user_message: Query in Tamil, English, or mixed.
            customer_id: Optional customer ID for policy/claim lookup.
        
        Returns:
            {
              "intent": "ask_claim_status",
              "confidence": 0.92,
              "response": "Your claim CLM-2024-001 is approved...",
              "action": "query_claims" | "provide_info" | etc.
            }
        """
        # Step 1: Intent classification
        intent_result = self.classifier.classify(user_message, threshold=0.5)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        # Step 2: Route to action handler
        action_result = self._handle_intent(intent, user_message, customer_id)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "response": action_result["response"],
            "action": action_result.get("action", "provide_info"),
            "metadata": action_result.get("metadata", {})
        }
    
    def _handle_intent(self, intent: str, query: str, customer_id: Optional[str]) -> Dict:
        """Route intent to appropriate handler."""
        
        if intent == "ask_claim_status":
            return self._handle_claim_status(query, customer_id)
        elif intent == "ask_policy_status":
            return self._handle_policy_status(query, customer_id)
        elif intent == "file_claim":
            return self._handle_file_claim(query, customer_id)
        elif intent == "ask_coverage":
            return self._handle_coverage_query(query, customer_id)
        elif intent == "greet":
            return {"response": "வணக்கம்! (Hello!) I'm your insurance assistant. How can I help?", "action": "greet"}
        elif intent == "goodbye":
            return {"response": "விடைபெறுகிறேன்! (Goodbye!) Have a great day.", "action": "goodbye"}
        else:
            # Unknown intent: use LLM for general response
            llm_response = self.llm.generate(f"Insurance query: {query}")
            return {"response": llm_response, "action": "llm_fallback"}
    
    def _handle_claim_status(self, query: str, customer_id: Optional[str]) -> Dict:
        """Handle claim status queries."""
        if self.claims:
            # Mock: return first claim's status
            claim = self.claims[0]
            response = f"Your claim {claim['claim_id']} is {claim['status']}. Amount: ₹{claim['amount']}."
            return {"response": response, "action": "query_claims", "metadata": {"claim_id": claim["claim_id"]}}
        else:
            return {"response": "No claims found.", "action": "query_claims"}
    
    def _handle_policy_status(self, query: str, customer_id: Optional[str]) -> Dict:
        """Handle policy status queries."""
        if self.policies:
            policy = self.policies[0]
            response = f"Your policy {policy['policy_id']} is {policy['status']}. Valid till {policy['expiry_date']}."
            return {"response": response, "action": "query_policies", "metadata": {"policy_id": policy["policy_id"]}}
        else:
            return {"response": "No policies found.", "action": "query_policies"}
    
    def _handle_file_claim(self, query: str, customer_id: Optional[str]) -> Dict:
        """Handle claim filing requests."""
        response = "To file a claim, please provide: (1) Policy number, (2) Date of incident, (3) Description. We'll guide you through the process."
        return {"response": response, "action": "initiate_claim"}
    
    def _handle_coverage_query(self, query: str, customer_id: Optional[str]) -> Dict:
        """Handle coverage queries."""
        if self.policies:
            policy = self.policies[0]
            coverage = ", ".join(policy.get("coverage", []))
            response = f"Your policy covers: {coverage}."
            return {"response": response, "action": "query_coverage", "metadata": {"coverage": coverage}}
        else:
            return {"response": "No policy information found.", "action": "query_coverage"}
