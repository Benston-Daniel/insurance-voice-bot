# lang_detect.py
import re

# Very small keyword lists - extend as needed
TAMIL_KEYWORDS = ["அனுமதி","காப்பீடு","முதிர்வு","காப்பீடு", "முன்னோட்டம்", "குற்றச்சாட்டு", "காப்பீட்டு"]
EN_KEYWORDS = ["policy","premium","maturity","claim","waiting period","coverage"]

def detect_language(text):
    t = text.lower()
    ta_hits = sum(1 for kw in TAMIL_KEYWORDS if kw in t)
    en_hits = sum(1 for kw in EN_KEYWORDS if kw in t)
    if ta_hits > en_hits:
        return "ta"
    if en_hits > ta_hits:
        return "en"
    # fallback: simple unicode-range check (Tamil block)
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"
    return "en"
