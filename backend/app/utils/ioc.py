import re

IOC_PATTERNS = {
    "ipv4": re.compile(r"\b(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b"),
    "email": re.compile(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b"),
    "domain": re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"),
    "sha256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "bitcoin": re.compile(r"\b(?:bc1[a-z0-9]{25,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b"),
    "ethereum": re.compile(r"\b0x[a-fA-F0-9]{40}\b"),
}


def extract_iocs(text: str) -> dict[str, list[str]]:
    return {name: sorted(set(pattern.findall(text))) for name, pattern in IOC_PATTERNS.items()}
