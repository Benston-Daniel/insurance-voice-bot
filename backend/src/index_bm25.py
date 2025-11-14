# index_bm25.py
import json
from pathlib import Path
from rank_bm25 import BM25Okapi
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

DATA_FILE = Path("policies_chunks.jsonl")
docs = []
meta = []
for line in open(DATA_FILE, encoding="utf-8"):
    rec = json.loads(line)
    docs.append(rec["content"])
    meta.append({"policy_file": rec["policy_file"], "section": rec["section"], "policy_type": rec["policy_type"]})

# tokenize
tokenized = [word_tokenize(d.lower()) for d in docs]
bm25 = BM25Okapi(tokenized)

def retrieve(query, top_k=3):
    qtok = word_tokenize(query.lower())
    scores = bm25.get_scores(qtok)
    top_idx = scores.argsort()[-top_k:][::-1]
    results = []
    for i in top_idx:
        results.append({"meta": meta[i], "score": float(scores[i]), "content": docs[i]})
    return results

# quick test
if __name__=="__main__":
    q = "What is the waiting period for pre-existing diseases?"
    for r in retrieve(q, top_k=3):
        print(r["meta"], r["score"])
