#!/usr/bin/env python3
"""
scanner.py — unified scanner compatible with:
  - patterns.json (dict: {id: {pattern, risk, description}})
  - reporter.py (Belle's Stream 4: write_report & generate_console_report)

Findings schema produced here:
  { "pattern": <id>, "file": <path>, "line": <int>, "match": <raw>, "description": <str> }

Exit code:
  - 1 if any High-risk finding (per risk_rules.json via reporter.write_report)
  - 0 otherwise
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from bisect import bisect
from typing import Dict, Any, Iterable, List, Tuple
import os

# v1/v3 utilities (project-provided)
from file_handler import find_files, read_file

# Belle's reporter (Stream 4)
from reporter import write_report, generate_console_report

# ---- Defaults (align with your repo) ----
DEFAULT_PATTERNS_FILE = "patterns.json"
DEFAULT_TARGET_EXTS = [".py", ".txt", ".md", ".cfg", ".json", ".docx", ".csv", ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"]
DEFAULT_OUT = "scan_report.json"

# ---- Patterns ----

def load_patterns(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load pattern definitions from patterns.json
    Expected shape:
      {
        "email": { "pattern": "...", "risk": "Low|High|...", "description": "..." },
        ...
      }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("patterns.json must be a JSON object mapping ids to rules.")
    for pid, rule in data.items():
        if "pattern" not in rule:
            raise ValueError(f"Pattern '{pid}' is missing the 'pattern' field.")
    return data

def compile_patterns(patterns: Dict[str, Dict[str, Any]]) -> Dict[str, re.Pattern]:
    """Compile all regexes once with DOTALL (to match across lines where needed)."""
    compiled: Dict[str, re.Pattern] = {}
    for pid, rule in patterns.items():
        pat = rule["pattern"]
        try:
            compiled[pid] = re.compile(pat, re.DOTALL)
        except re.error as e:
            raise ValueError(f"Invalid regex for pattern '{pid}': {e}")
    return compiled

# ---- Scanning helpers ----

def _newline_indices(text: str) -> List[int]:
    return [i for i, ch in enumerate(text) if ch == "\n"]

def _line_number(newlines: List[int], idx: int) -> int:
    # 1-based line numbers: count of newlines before idx + 1
    return bisect(newlines, idx) + 1

def scan_text(text: str, file_path: str,
              compiled: Dict[str, re.Pattern],
              meta: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Run all compiled patterns over a text blob, recording file and line per match.
    Returns a list of finding dicts for reporter.py.
    """
    findings: List[Dict[str, Any]] = []
    if not text:
        return findings

    newlines = _newline_indices(text)
    for pid, regex in compiled.items():
        desc = meta.get(pid, {}).get("description", pid)
        for m in regex.finditer(text):
            start = m.start()
            line = _line_number(newlines, start)
            raw = m.group(0)
            findings.append({
                "pattern": pid,
                "file": file_path,
                "line": line,
                "match": raw,
                "description": desc
            })
    return findings

def scan_paths(paths: Iterable[str],
               compiled: Dict[str, re.Pattern],
               meta: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_findings: List[Dict[str, Any]] = []
    for path in paths:
        content = read_file(path)
        # Ensure we have text (read_file should return str; if bytes, decode)
        if isinstance(content, bytes):
            try:
                content = content.decode("utf-8")
            except UnicodeDecodeError:
                content = content.decode("latin-1", errors="ignore")
        if not isinstance(content, str):
            continue
        all_findings.extend(scan_text(content, path, compiled, meta))
    return all_findings

# ---- CLI ----

def parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Unified sensitive-data scanner")
    ap.add_argument("--file", help="Single file to scan (overrides --root and --ext)")
    ap.add_argument("--root", default=".", help="Root directory to scan (default: current dir)")
    ap.add_argument("--patterns", default=DEFAULT_PATTERNS_FILE, help="Path to patterns.json")
    ap.add_argument("--out", default=DEFAULT_OUT, help="Path to JSON report output")
    ap.add_argument("--ext", nargs="*", default=DEFAULT_TARGET_EXTS,
                    help="File extensions to include (e.g., .py .txt .md .cfg .json)")
    ap.add_argument("--no-console", action="store_true", help="Skip console summary output")
    return ap.parse_args(argv)

# Function to get a valid directory path from the user
def get_valid_path():
    while True:
        path = input("Enter the directory path containing the files to scan (press Enter to use the project folder): ").strip()
        path = path.strip('"').strip("'")  # Remove surrounding quotes if present
        if not path:  # If no input is provided, use the current directory
            print("No path provided. Files will be scanned in the project folder.")
            print("-" * 63)
            return os.getcwd()
        elif os.path.isdir(path):  # Validate the provided path
            print("-" * 63)
            return path
         
        else:
            print("We cannot find that path. Please enter a valid directory or press Enter to use the project folder.")

# ---- Main ----

def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])

    patterns = load_patterns(ns.patterns)
    compiled = compile_patterns(patterns)

    # Check if a specific file is provided
    if ns.file:
        # Validate the file path
        if not os.path.isfile(ns.file):
            print(f"[!] The specified file does not exist: {ns.file}")
            return 1

        # Scan only the specified file
        print(f"[i] Scanning the specified file: {ns.file}")
        findings = scan_paths([ns.file], compiled, patterns)
    else:
        # Identify valid directory to scan
        directory = get_valid_path()

        # Use project helper to expand files under root with extension filter
        file_list = list(find_files(directory, ns.ext))
        findings = scan_paths(file_list, compiled, patterns)

    # JSON report (enriched with risk/tip/laws by reporter.write_report)
    enriched = write_report(findings, out_path=ns.out)

    # Console summary (masked)
    if not ns.no_console:
        generate_console_report(findings)

    # Exit code policy: fail if any High risk present
    has_high = any(f.get("risk") == "High" for f in enriched)
    if has_high:
        print("[!] High-risk data found. Failing scan.")
        return 1

    if enriched:
        print("[i] Findings present. Review the report.")
    else:
        print("[✓] No sensitive data detected.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())