"""Helpers to call a Rasa server's HTTP API.
Simple synchronous helper using `requests`. For production, consider
async requests or a more robust client and error handling.
"""
import requests

RASA_URL = "http://rasa:5005/webhooks/rest/webhook"  # docker-compose service name by default


def send_message(message: str, sender_id: str = "user") -> dict:
    payload = {"sender": sender_id, "message": message}
    try:
        r = requests.post(RASA_URL, json=payload, timeout=10)
        r.raise_for_status()
        # Rasa returns a list of messages; return as-is
        return {"status": "ok", "rasa": r.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}
