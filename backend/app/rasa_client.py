"""Helpers to call a Rasa server's HTTP API.
Simple synchronous helper using `requests`. For production, consider
async requests or a more robust client and error handling.
"""
import requests
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

def call_rasa(message_text, sender_id="user"):
    payload = {"sender": sender_id, "message": message_text}
    try:
        r = requests.post(RASA_URL, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return [{"text": "Rasa is not available. Error: " + str(e)}]

