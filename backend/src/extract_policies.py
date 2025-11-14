"""
extract_policies_tamil_friendly.py

Purpose:
  - Extract text from PDFs while preserving Tamil Unicode.
  - Prefer PyMuPDF (fitz) text extraction, fallback to pdfplumber.
  - If a PDF page yields no text (scanned), perform OCR using pytesseract
    with Tamil language (lang='tam') and optionally English as fallback.

Outputs:
  - policies_chunks.jsonl   (one JSON object per chunk)
"""

import os
import json
import re
from pathlib import Path
from tqdm import tqdm
from typing import List

# Prefer PyMuPDF (fitz) for Unicode-preserving extraction
try:
    import fitz  # PyMuPDF
    HAVE_FITZ = True
except Exception:
    HAVE_FITZ = False

# Fallback text extractor
try:
    import pdfplumber
    HAVE_PDFPLUMBER = True
except Exception:
    HAVE_PDFPLUMBER = False

# OCR fallback (for scanned PDFs)
try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    HAVE_OCR = True
except Exception:
    HAVE_OCR = False

# ---------- Configuration ----------
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "data" / "policies"
OUTPUT_JSONL = BASE_DIR / "data" / "policies_chunks.jsonl"
CHUNK_MAX_CHARS = 1200  # tuneable
OCR_LANG = "tam+eng"    # tesseract language codes: 'tam' for Tamil, 'eng' for English
PDF_DPI_FOR_OCR = 300   # DPI for converting PDF pages to images for OCR
FORCE_OCR = '1'
# -----------------------------------

def extract_text_fitz(pdf_path: Path) -> List[str]:
    """
    Extract text per page using PyMuPDF (fitz). Returns list of page texts.
    PyMuPDF generally preserves Unicode (including Tamil) correctly.
    """
    pages_text = []
    doc = fitz.open(str(pdf_path))
    for page in doc:
        try:
            text = page.get_text("text") or ""
        except Exception:
            # sometimes layout or font issues; fallback to blocks
            try:
                text = page.get_text("blocks")
                # blocks is a list of tuples; join text fields
                text = "\n".join(b[4] for b in text if len(b) > 4 and b[4])
            except Exception:
                text = ""
        pages_text.append(text)
    doc.close()
    return pages_text

def extract_text_pdfplumber(pdf_path: Path) -> List[str]:
    """
    Extract text per page using pdfplumber (layout-preserving).
    """
    pages_text = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages_text.append(text)
    return pages_text

def extract_text_ocr(pdf_path: Path, dpi=PDF_DPI_FOR_OCR, lang=OCR_LANG) -> List[str]:
    """
    Convert PDF pages to images and OCR with pytesseract.
    Requires: poppler for pdf2image and tesseract with Tamil language pack installed.
    """
    pages_text = []
    images = convert_from_path(str(pdf_path), dpi=dpi)
    for img in images:
        try:
            # Ensure image is in RGB mode
            if img.mode != "RGB":
                img = img.convert("RGB")
            text = pytesseract.image_to_string(img, lang=lang) or ""
        except Exception as e:
            print("OCR error:", e)
            text = ""
        pages_text.append(text)
    return pages_text

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Try multiple extractors in order:
      1) PyMuPDF (fitz)
      2) pdfplumber
      3) OCR (pytesseract) - for scanned docs
    Returns full document text (pages joined). Preserves Unicode.
    """
    pages_text = []

    # 1) Try PyMuPDF
    if HAVE_FITZ:
        try:
            pages_text = extract_text_fitz(pdf_path)
            # if all pages empty, treat as potential scanned PDF and fall through
            if any(p.strip() for p in pages_text):
                return "\n\n".join(pages_text)
        except Exception as e:
            print(f"fitz extraction failed for {pdf_path.name}: {e}")

    # 2) Try pdfplumber
    if HAVE_PDFPLUMBER:
        try:
            pages_text = extract_text_pdfplumber(pdf_path)
            if any(p.strip() for p in pages_text):
                return "\n\n".join(pages_text)
        except Exception as e:
            print(f"pdfplumber extraction failed for {pdf_path.name}: {e}")

    # 3) OCR fallback
    if HAVE_OCR:
        try:
            pages_text = extract_text_ocr(pdf_path)
            if any(p.strip() for p in pages_text):
                return "\n\n".join(pages_text)
        except Exception as e:
            print(f"OCR extraction failed for {pdf_path.name}: {e}")

    # If we got here, return joined pages (may be empty)
    return "\n\n".join(pages_text)

def normalize_text_keep_unicode(s: str) -> str:
    """
    Normalize whitespace and line breaks but DO NOT strip Unicode.
    Keep Tamil characters intact.
    """
    if not s:
        return ""
    # Normalize different newline styles
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse repeated blank lines to two
    s = re.sub(r'\n{3,}', '\n\n', s)
    # Strip leading/trailing whitespace
    s = s.strip()
    # Normalize multiple spaces but preserve non-breaking spaces
    s = re.sub(r'[ \t]{2,}', ' ', s)
    return s

def chunk_text(text: str, max_chars: int = CHUNK_MAX_CHARS) -> List[str]:
    """
    Chunk by paragraphs (double newline) then accumulate into chunks up to max_chars.
    Uses simple fallback of splitting long paragraphs if needed.
    """
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    chunks = []
    cur = ""
    for p in paragraphs:
        if len(cur) + len(p) + 2 <= max_chars:
            cur = (cur + "\n\n" + p) if cur else p
        else:
            if cur:
                chunks.append(cur)
            # If paragraph itself > max_chars, split by sentence-like boundaries,
            # but keep unicode-aware splitting (naive char slicing fallback)
            if len(p) > max_chars:
                # Try splitting on punctuation common in both Tamil and English
                splits = re.split(r'(?<=[\.\!\?\।\u0964\u0965])\s+', p)  # includes Devanagari/Tamil common punctuation
                part = ""
                for s in splits:
                    if len(part) + len(s) + 1 <= max_chars:
                        part = (part + " " + s).strip() if part else s
                    else:
                        if part:
                            chunks.append(part)
                        if len(s) > max_chars:
                            # final fallback: slice
                            for i in range(0, len(s), max_chars):
                                chunks.append(s[i:i+max_chars])
                            part = ""
                        else:
                            part = s
                if part:
                    cur = part
                else:
                    cur = ""
            else:
                cur = p
    if cur:
        chunks.append(cur)
    return chunks

def process_pdfs(input_dir: Path, output_jsonl: Path):
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    for pdf_file in sorted(input_dir.glob("*.pdf")):
        print(f"Processing: {pdf_file.name}")
        try:
            raw = extract_text_from_pdf(pdf_file)
        except Exception as e:
            print(f"Error extracting {pdf_file.name}: {e}")
            raw = ""

        raw = normalize_text_keep_unicode(raw)
        chunks = chunk_text(raw)
        policy_type = pdf_file.stem

        with output_jsonl.open("a", encoding="utf-8") as fout:
            for i, chunk in enumerate(chunks):
                rec = {
                    "policy_file": pdf_file.name,
                    "policy_type": policy_type,
                    "section": f"chunk_{i}",
                    "content": chunk,
                    "key_terms": []
                }
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1

    print(f"Done. Wrote {written} chunks to {output_jsonl}")

if __name__ == "__main__":
    if not INPUT_DIR.exists():
        print(f"Input directory {INPUT_DIR} does not exist. Create and add PDF files.")
    else:
        # Remove existing output file to avoid appending duplicates during tests (optional)
        if OUTPUT_JSONL.exists():
            print(f"Overwriting existing {OUTPUT_JSONL} (backup if needed).")
            OUTPUT_JSONL.unlink()
        process_pdfs(INPUT_DIR, OUTPUT_JSONL)
