import pymupdf  # aka fitz
from pathlib import Path
import pdfplumber

SAMPLE_DIR = Path.cwd() / "sample_docs"
SAMPLE_PDF  = SAMPLE_DIR / "company_policies.pdf"
SAMPLE_HTML = SAMPLE_DIR / "product_page.html"
SAMPLE_DOCX = SAMPLE_DIR / "onboarding.docx"

# Hard-fail if any are missing — the notebook depends on them
for path in [SAMPLE_PDF, SAMPLE_HTML, SAMPLE_DOCX]:
    assert path.exists(), (
        f"Missing {path.name}. Run: python demos/generate_sample_docs.py"
    )

print("Sample documents ready:")
for path in [SAMPLE_PDF, SAMPLE_HTML, SAMPLE_DOCX]:
    print(f"  {path.name:30s}  {path.stat().st_size:>6d} bytes")
    
### Lets start with PDF
## trying pymupdf
# doc = pymupdf.open(SAMPLE_PDF)
# print(f"Opened PDF: {SAMPLE_PDF.name}")
# print(f"Number of pages: {doc.page_count}")
# for i, page in enumerate(doc, start=1):
#     text = page.get_text()
#     print(f"\n--- Page {i} ---\n")
#     print(text)
    
# doc.close()

## replacing pymuypdf with pdfplumber
# with pdfplumber.open(SAMPLE_PDF) as pdf:
#     first_page = pdf.pages[0]
    
#     # Text extraction — similar to PyMuPDF for prose
#     text = first_page.extract_text()
#     print("Text extraction (same as PyMuPDF for prose):")
#     print(text[:300], "...\n")
    
#     # Table extraction — pdfplumber's superpower
#     tables = first_page.extract_tables()
#     print(f"Tables detected on page 1: {len(tables)}")
#     for i, table in enumerate(tables, 1):
#         print(f"\n══ Table {i} ══")
#         for row in table:
#             print(f"  {' | '.join(str(c) for c in row)}")

# Load the PDF text (page 1 only, for demo compactness)
doc = pymupdf.open(SAMPLE_PDF)
page1_text = doc[0].get_text()
doc.close()

import re

def chunk_recursive(text, max_size=400):
    """Split by paragraphs. If a paragraph exceeds max_size, split by sentences."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    for para in paragraphs:
        if len(para) <= max_size:
            chunks.append(para)
        else:
            # Sentence-level fallback
            sentences = re.split(r'(?<=[.!?])\s+', para)
            current = ""
            for sent in sentences:
                if len(current) + len(sent) + 1 <= max_size:
                    current = (current + " " + sent).strip()
                else:
                    if current:
                        chunks.append(current)
                    current = sent
            if current:
                chunks.append(current)
    return chunks

recursive_chunks = chunk_recursive(page1_text, max_size=400)
print(f"Recursive chunking (max_size=400) → {len(recursive_chunks)} chunks\n")

for i, chunk in enumerate(recursive_chunks):
    ends_mid = not chunk.rstrip().endswith(('.', '!', '?', ':'))
    marker = " ← ends mid-sentence" if ends_mid else " ← clean end"
    preview = chunk[-60:].replace('\n', ' ')
    print(f"  [{i}] {len(chunk):>4d} chars, ends: '...{preview}'{marker}")