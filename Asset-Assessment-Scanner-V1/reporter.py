# reporter.py — Stream 4: Reporting & Redaction (Belle Mattioli)
# Responsibilities:
# - JSON output: includes raw snippet, risk, remediation tip, and exact law references.
# - Console output: grouped by risk (High/Low), columns: Risk | File:Line | Pattern | Tip,
#   with the matched text always redacted as ****SECRET****.

from __future__ import annotations
import json
from collections import Counter
from typing import Dict, Any, Iterable, List, Optional

DEFAULT_RISK_RULES_PATH = "risk_rules.json"
REDACTION_TOKEN = "****SECRET****"

# ---------- Helpers ----------

def _load_risk_rules(path: str = DEFAULT_RISK_RULES_PATH) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _primary_law(compliance: Optional[List[str]]) -> str:
    """Return a single primary law label (first in list) or a sensible default."""
    if isinstance(compliance, list) and compliance:
        return str(compliance[0])
    return "General Best Practice"

def _as_list(v) -> List[str]:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def _enrich_findings(findings: Iterable[Dict[str, Any]],
                     risk_rules: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge upstream scanner findings with Stream 4 risk rules.
    Expected incoming fields (best effort): pattern, file, line, match or raw, description (optional).
    Returns enriched records with: risk, tip, compliance (array), law (primary), raw (unredacted).
    """
    enriched: List[Dict[str, Any]] = []
    for f in findings:
        pid = f.get("pattern")
        rr = risk_rules.get(pid, {})
        level = (rr.get("level") or "Low").title()            # "High" / "Low"
        tip = rr.get("tip") or "Follow secure handling and removal procedures."
        comp_list = _as_list(rr.get("compliance"))
        law = _primary_law(comp_list)

        enriched.append({
            "pattern": pid,
            "description": f.get("description"),
            "file": f.get("file"),
            "line": f.get("line"),
            "risk": level,
            "tip": tip,
            "law": law,                  # primary law for convenience
            "compliance": comp_list,     # full list of exact law references
            "raw": f.get("raw") or f.get("match") or ""  # keep unredacted in JSON
        })
    return enriched

# ---------- Public APIs ----------

def write_report(findings: Iterable[Dict[str, Any]],
                 out_path: str = "scan_report.json",
                 risk_rules_path: str = DEFAULT_RISK_RULES_PATH) -> List[Dict[str, Any]]:
    """
    Write enriched JSON report to disk.
    Includes fields: pattern, file, line, risk, tip, law, compliance[], raw (unredacted).
    Returns the enriched list (handy if the caller also wants to print console).
    """
    risk_rules = _load_risk_rules(risk_rules_path)
    enriched = _enrich_findings(findings, risk_rules)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)
    print(f"[+] Report saved to {out_path}")
    return enriched

def generate_json_report(findings: Iterable[Dict[str, Any]],
                         risk_rules_path: str = DEFAULT_RISK_RULES_PATH) -> str:
    """
    Return the enriched JSON as a string (does not write to disk).
    """
    risk_rules = _load_risk_rules(risk_rules_path)
    enriched = _enrich_findings(findings, risk_rules)
    return json.dumps(enriched, indent=2)

def generate_console_report(findings: Iterable[Dict[str, Any]],
                            risk_rules_path: str = DEFAULT_RISK_RULES_PATH) -> None:
    """
    Console summary grouped by risk bucket with masked snippets.
    Columns per item: Risk | File:Line | Pattern | Tip
    """
    risk_rules = _load_risk_rules(risk_rules_path)
    enriched = _enrich_findings(findings, risk_rules)

    # Overall counts (for header summaries)
    totals = Counter(e["risk"] for e in enriched)

    for bucket in ("High", "Low"):  # deterministic order
        items = [e for e in enriched if e["risk"] == bucket]
        if not items:
            continue
        print(f"\n=== {bucket} Risk ({len(items)} findings) ===")
        print(f"Summary: High: {totals.get('High',0)}, Low: {totals.get('Low',0)}")

        # sort by file then line then pattern for stable output
        def _key(x: Dict[str, Any]):
            return (str(x.get("file") or ""), int(x.get("line") or 0), str(x.get("pattern") or ""))
        for e in sorted(items, key=_key):
            file_line = f"{e.get('file') or '<stdin>'}:{e.get('line') or '?'}"
            pattern = e.get("pattern") or "unknown"
            tip = e.get("tip") or ""
            print(f"\n• Risk {bucket.upper()} | {file_line} | {pattern} | Tip: {tip}")
            print(f"  → {REDACTION_TOKEN}")  # ALWAYS mask in console