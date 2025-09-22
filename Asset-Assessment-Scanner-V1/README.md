# Redback Ethics Asset Scanner

The **Asset Scanner** is a Python-based tool for detecting sensitive information (PII, secrets, credentials, etc.) in documents and media.  
It is designed for educational use in cybersecurity and ethics modules.

---

## 📂 Project Structure

- `scanner.py` – Main entry point for scanning files and generating reports.
- `scan_media.py` – Scans image/PDF inputs using OCR (`ocr_engine.py`).
- `file_handler.py` – Handles input files and preprocessing.
- `ocr_engine.py` – OCR engine wrapper for text extraction from images.
- `reporter.py` – Builds structured scan results and output reports.
- `patterns.json` – Regex patterns for detecting sensitive items.
- `risk_rules.json` – Maps detected patterns to risk levels, compliance references, and remediation tips.

---

## ⚙️ Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repo>/redback-ethics.git
   cd redback-ethics/asset-scanner
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

To scan a document:
```bash
python scanner.py --file "/path/to/document.docx"
```

To scan an image or PDF (OCR enabled):
```bash
python scan_media.py --file "/path/to/image_or_pdf"
```

To scan a directory:
```bash
python scanner.py --root "/path/to/folder"
```
OR
if you run scanner.py standalone you without and --file or --root arguments you will be prompted
to enter a directory in runtime

Output will include:
- Detected matches with line context
- Risk level (from `risk_rules.json`)
- Mitigation tips and relevant compliance frameworks

---

## ⚡ Command-Line Arguments

The scanner supports several arguments to control input and behaviour:

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--file` | Path | Scan a single file (e.g., `.docx`, `.pdf`, `.png`). | `python scanner.py --file "/path/to/document.docx"` |
| `--root` | Path | Recursively scan all files within a directory. | `python scanner.py --root "/path/to/folder"` |
| `--patterns` | Path | Custom path to `patterns.json`. Useful if you want to override defaults. | `python scanner.py --file test.docx --patterns ./configs/patterns.json` |
| `--out` | Path | File to write structured scan results (JSON or text depending on implementation). | `python scanner.py --root ./docs --out results.json` |
| `--no-console` | Flag | Suppress console output. Results will only be written to the output file. | `python scanner.py --root ./docs --no-console --out results.json` |

### Common Usage Examples

Scan one file:
```bash
python scanner.py --file "/Users/alice/Documents/report.docx"
```

Recursively Scan Directory:
```bash
python scanner.py --root "/Users/alice/Documents/sensitive_documents'
```

---

## 🛡️ Configuration

- **`patterns.json`**: Defines regex patterns for items like emails, API keys, driver’s licence numbers, etc.  
  Each entry specifies:
  - `pattern`: regex string
  - `risk`: risk level
  - `description`: human-readable explanation

- **`risk_rules.json`**: Associates each pattern with:
  - `level`: severity (Low/Medium/High)
  - `tip`: recommended mitigation
  - `compliance`: legal/regulatory references

You can extend these files to detect new types of data.

---

## 📝 Example

Scanning a document containing:

```
Email: alice@example.com
Password: "SuperSecret123"
```

Would output:

```
[Email] -> Medium Risk
Tip: Mask or obfuscate emails in logs/code unless strictly required.
Compliance: Privacy Act 1988 (Cth) — APP 11

[Password] -> High Risk
Tip: Remove hard-coded passwords; rotate immediately; use env vars or a vault.
Compliance: GDPR Art. 32 — Security of processing
```

---

## 🔒 Notes

- Regex-based scanning may produce **false positives**; tune `patterns.json` to your needs.
