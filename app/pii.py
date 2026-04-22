from __future__ import annotations

import hashlib
import re
from typing import Dict, Pattern

# ==============================
# PII REGEX PATTERNS
# ==============================

PII_PATTERNS: Dict[str, Pattern] = {
    "email": re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"),

    # Vietnamese phone numbers
    "phone_vn": re.compile(
        r"\b(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}\b"
    ),

    # CCCD / CMND (12 digits)
    "cccd": re.compile(r"\b\d{12}\b"),

    # Credit card (simple detection)
    "credit_card": re.compile(
        r"\b(?:\d{4}[- ]?){3}\d{4}\b"
    ),

    # Passport (Vietnam - heuristic)
    "passport": re.compile(r"\b[A-Z]\d{7}\b"),

    # API keys / tokens (basic heuristic)
    "api_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),

    # Vietnamese address keywords (simple heuristic)
    "address": re.compile(
        r"\b(số\s?\d+|đường|phường|quận|tỉnh|thành phố)\b",
        re.IGNORECASE
    ),
}

# ==============================
# CORE SCRUB FUNCTION
# ==============================

def scrub_text(text: str) -> str:
    """
    Replace all detected PII with redacted tokens.
    Example: email -> [REDACTED_EMAIL]
    """
    if not text:
        return text

    safe = text

    for name, pattern in PII_PATTERNS.items():
        safe = pattern.sub(f"[REDACTED_{name.upper()}]", safe)

    return safe


# ==============================
# SMART MASKING (OPTIONAL)
# ==============================

def mask_email(email: str) -> str:
    """
    Example: dat@gmail.com -> d***@gmail.com
    """
    parts = email.split("@")
    if len(parts) != 2:
        return "[REDACTED_EMAIL]"

    name, domain = parts
    if len(name) <= 1:
        return f"*@" + domain

    return name[0] + "***@" + domain


def mask_phone(phone: str) -> str:
    """
    Example: 0901234567 -> 090****567
    """
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return "[REDACTED_PHONE]"

    return digits[:3] + "****" + digits[-3:]


def smart_scrub(text: str) -> str:
    """
    More advanced scrubbing with partial masking
    """
    if not text:
        return text

    safe = text

    # Email masking
    safe = re.sub(
        PII_PATTERNS["email"],
        lambda m: mask_email(m.group()),
        safe
    )

    # Phone masking
    safe = re.sub(
        PII_PATTERNS["phone_vn"],
        lambda m: mask_phone(m.group()),
        safe
    )

    # Other PII -> full redact
    for name in ["cccd", "credit_card", "passport", "api_key"]:
        safe = PII_PATTERNS[name].sub(
            f"[REDACTED_{name.upper()}]",
            safe
        )

    return safe


# ==============================
# LOG-SAFE SUMMARY
# ==============================

def summarize_text(text: str, max_len: int = 80) -> str:
    """
    Clean + truncate text for logging
    """
    if not text:
        return ""

    safe = scrub_text(text)
    safe = safe.strip().replace("\n", " ")

    return safe[:max_len] + ("..." if len(safe) > max_len else "")


# ==============================
# USER ID HASHING (GDPR SAFE)
# ==============================

def hash_user_id(user_id: str) -> str:
    """
    Hash user_id to avoid exposing raw identity
    """
    if not user_id:
        return "anonymous"

    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]


# ==============================
# TEST (FOR DEBUG)
# ==============================

if __name__ == "__main__":
    sample = """
    Email: dat@gmail.com
    Phone: 090 123 4567
    CCCD: 123456789012
    Card: 1234-5678-9012-3456
    Passport: B1234567
    API key: sk-abc12345678901234567890
    Address: số 12 đường Láng, Hà Nội
    """

    print("ORIGINAL:\n", sample)
    print("\nSCRUB:\n", scrub_text(sample))
    print("\nSMART SCRUB:\n", smart_scrub(sample))
    print("\nSUMMARY:\n", summarize_text(sample))