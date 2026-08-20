"""Quick unit tests for extraction utilities."""
import sys
sys.path.insert(0, ".")

from backend.agents.extraction.utils import (
    sanitize_pan, sanitize_ifsc, mask_aadhaar,
    sanitize_amount, normalize_date, sanitize_phone,
    extract_json_from_response, merge_extraction_dicts,
)

errors = []

def check(name, actual, expected):
    if actual != expected:
        errors.append(f"FAIL [{name}]: got {actual!r}, expected {expected!r}")
    else:
        print(f"  PASS  {name}")

# ── PAN ──────────────────────────────────────────────────────────────────────
check("PAN valid",    sanitize_pan("ABCDE1234F"), "ABCDE1234F")
check("PAN lowercase",sanitize_pan("abcde1234f"), "ABCDE1234F")
check("PAN invalid",  sanitize_pan("invalid"),    None)
check("PAN None",     sanitize_pan(None),         None)

# ── IFSC ─────────────────────────────────────────────────────────────────────
check("IFSC valid",   sanitize_ifsc("SBIN0001234"), "SBIN0001234")
check("IFSC invalid", sanitize_ifsc("XXXX9999999"), None)

# ── Aadhaar masking ───────────────────────────────────────────────────────────
check("Aadhaar spaced",  mask_aadhaar("1234 5678 9012"), "XXXX XXXX 9012")
check("Aadhaar compact", mask_aadhaar("123456789012"),   "XXXX XXXX 9012")
check("Aadhaar None",    mask_aadhaar(None),              None)

# ── Amount sanitization ───────────────────────────────────────────────────────
check("Amount INR",       sanitize_amount("₹1,20,000"),  "120000")
check("Amount decimal",   sanitize_amount("82000.00"),    "82000")
check("Amount plain",     sanitize_amount("50000"),       "50000")
check("Amount None",      sanitize_amount(None),          None)

# ── Date normalization ────────────────────────────────────────────────────────
check("Date DD/MM/YYYY",  normalize_date("25/12/2024"),  "2024-12-25")
check("Date YYYY-MM-DD",  normalize_date("2024-12-25"),  "2024-12-25")
check("Date DD-MM-YYYY",  normalize_date("25-12-2024"),  "2024-12-25")
check("Date None",        normalize_date(None),           None)

# ── Phone ─────────────────────────────────────────────────────────────────────
check("Phone 10-digit",   sanitize_phone("9876543210"),   "9876543210")
check("Phone +91",        sanitize_phone("+919876543210"), "9876543210")
check("Phone short",      sanitize_phone("12345"),         None)

# ── JSON extraction ───────────────────────────────────────────────────────────
raw_plain = '{"name": "John", "pan": "ABCDE1234F"}'
check("JSON plain", extract_json_from_response(raw_plain), {"name": "John", "pan": "ABCDE1234F"})

raw_md = '```json\n{"name": "Jane"}\n```'
check("JSON markdown", extract_json_from_response(raw_md), {"name": "Jane"})

raw_md2 = '```\n{"name": "Bob"}\n```'
check("JSON markdown no lang", extract_json_from_response(raw_md2), {"name": "Bob"})

# ── Merge ─────────────────────────────────────────────────────────────────────
e1 = {"personal": {"name": "John", "pan": None}, "confidence_score": 0.8}
e2 = {"personal": {"name": None,  "pan": "ABCDE1234F"}, "confidence_score": 0.6}
merged = merge_extraction_dicts([e1, e2])
check("Merge name from e1",  merged["personal"]["name"], "John")
check("Merge pan from e2",   merged["personal"]["pan"],  "ABCDE1234F")
check("Merge confidence avg",merged["confidence_score"], 0.7)

# ── Summary ───────────────────────────────────────────────────────────────────
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(" ", e)
    sys.exit(1)
else:
    print(f"\nOK All {20} tests passed!")
