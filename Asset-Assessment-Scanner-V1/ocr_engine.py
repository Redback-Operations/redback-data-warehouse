from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path
import re

import numpy as np
from PIL import Image
import pytesseract
import cv2

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except Exception:
    PDF2IMAGE_AVAILABLE = False

@dataclass
class OCRConfig:
    dpi: int = 300
    deskew: bool = True
    binarize: bool = True
    oem: int = 3
    psm: int = 3
    lang: str = "eng"

def _to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def _to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))

def _normalize_dpi(img: Image.Image, target_dpi: int) -> Image.Image:
    dpi = img.info.get("dpi", (target_dpi, target_dpi))[0]
    if dpi < target_dpi:
        scale = target_dpi / dpi
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)
        img.info["dpi"] = (target_dpi, target_dpi)
    return img

def _deskew(cv_img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if coords.size == 0:
        return cv_img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = cv_img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(cv_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def _binarize(cv_img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 35, 11)
    return cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)

def preprocess_image(img: Image.Image, cfg: OCRConfig) -> Image.Image:
    img = _normalize_dpi(img, cfg.dpi)
    cv_img = _to_cv(img)
    if cfg.deskew:
        cv_img = _deskew(cv_img)
    if cfg.binarize:
        cv_img = _binarize(cv_img)
    return _to_pil(cv_img)

def _tesseract_args(cfg: OCRConfig) -> str:
    return f"--oem {cfg.oem} --psm {cfg.psm}"

def ocr_image(img: Image.Image, cfg: Optional[OCRConfig] = None) -> str:
    cfg = cfg or OCRConfig()
    img_p = preprocess_image(img, cfg)
    text = pytesseract.image_to_string(img_p, lang=cfg.lang, config=_tesseract_args(cfg))
    return text.strip()

def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> List[Image.Image]:
    if not PDF2IMAGE_AVAILABLE:
        raise RuntimeError("pdf2image not available or poppler missing.")
    return convert_from_path(str(pdf_path), dpi=dpi)

def ocr_pdf(pdf_path: str | Path, cfg: Optional[OCRConfig] = None) -> Tuple[str, List[str]]:
    cfg = cfg or OCRConfig()
    pages = pdf_to_images(pdf_path, dpi=cfg.dpi)
    page_texts = [ocr_image(p, cfg) for p in pages]
    return "\n".join(page_texts), page_texts
