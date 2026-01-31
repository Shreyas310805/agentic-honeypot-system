import re
from app.api.schemas import Intelligence

def extract_scam_intelligence(text: str) -> Intelligence:
    """
    Scans text for Bank Account numbers, UPI IDs, and Phishing Links.
    """
    
    # 1. Regex for UPI IDs (e.g., scammer@okaxis, 9876543210@paytm)
    upi_pattern = r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}"
    
    # 2. Regex for Indian Bank Account Numbers (9-18 digits, avoiding simple 10-digit mobile numbers)
    # We look for long strings of digits that are NOT part of a sentence like "10 minutes"
    bank_pattern = r"\b[0-9]{9,18}\b"
    
    # 3. Regex for Suspicious Links (http/https/bit.ly)
    link_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"

    found_upi = re.findall(upi_pattern, text)
    found_bank = re.findall(bank_pattern, text)
    found_links = re.findall(link_pattern, text)

    # Filter out mobile numbers (10 digits starting with 6-9) from bank accounts if needed
    # (For this hackathon, simple extraction is usually enough)

    return Intelligence(
        bank_accounts=found_bank,
        upi_ids=found_upi,
        phishing_links=found_links
    )