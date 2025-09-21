from __future__ import annotations
import argparse
from pathlib import Path
import json

from file_handler import *
from ocr_engine import ocr_image, ocr_pdf, OCRConfig
from PIL import Image

def extract_text_from_file(file_path: str) -> str:
    """
    Given a file path to a PDF or image, returns the extracted text.
    Raises ValueError for unsupported file types.
    """
    cfg = OCRConfig()
    p = Path(file_path)
    try:
        if p.suffix.lower() == ".pdf":
            text, _ = ocr_pdf(p, cfg)
        elif p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}:
            text = ocr_image(Image.open(p), cfg)
        else:
            raise ValueError(f"Unsupported file type: {p.suffix}")
    except Exception as e:
        raise RuntimeError(f"OCR failed for {p}: {e}")
    return text