import os
from docx import Document
# Import extract_text_from_file for PDF and image support
from scan_media import extract_text_from_file

def find_files(directory, exts=None):
    exts = exts or []
    matches = []
    for dirpath, _, filenames in os.walk(directory):
        for fn in filenames:
            if not exts or any(fn.lower().endswith(e) for e in exts):
                matches.append(os.path.join(dirpath, fn))
    return matches

def read_file(path):
    lower_path = path.lower()
    if lower_path.endswith('.docx'):
        try:
            doc = Document(path)
            return '\n'.join([p.text for p in doc.paragraphs])
        except Exception as e:
            return f"[Error reading DOCX: {e}]"
    elif lower_path.endswith('.pdf') or lower_path.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp')):
        try:
            return extract_text_from_file(path)
        except Exception as e:
            return f"[Error extracting text from media: {e}]"
    else:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
