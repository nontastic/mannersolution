

import re
import unicodedata
from typing import Set


def normalize_text(text: str) -> str:
    if text is None:
        return ""

    text = str(text).strip().lower()

    # Umlaute / Sonderzeichen vereinheitlichen
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    replacements = {
        "\n": " ",
        "\t": " ",
        ",": ".",
        ";": " ",
        ":": " ",
        "/": " ",
        "\\": " ",
        "_": " ",
        "°": " grad ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # DIN/ISO normalisieren
    text = re.sub(r"\bdin[\s\-]?(\d+)\b", r"din \1", text)
    text = re.sub(r"\biso[\s\-]?(\d+)\b", r"iso \1", text)
    text = re.sub(r"\ben[\s\-]?iso[\s\-]?(\d+)\b", r"en iso \1", text)

    # Maße vereinheitlichen
    text = re.sub(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*mm", r"\1x\2x\3 mm", text)
    text = re.sub(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*mm", r"\1x\2 mm", text)
    text = re.sub(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)", r"\1x\2", text)

    # Bindestriche innerhalb von Wörtern vereinheitlichen
    text = re.sub(r"([a-z])\-([a-z])", r"\1 \2", text)

    # Sonderzeichen raus
    text = re.sub(r"[^a-z0-9\.\-\s]", " ", text)

    # Mehrfachspaces raus
    text = re.sub(r"\s+", " ", text).strip()

    return text


def combine_erp_text(kurztext: str, bestelltext: str) -> str:
    kurz = "" if kurztext is None else str(kurztext)
    bestell = "" if bestelltext is None else str(bestelltext)
    return f"{kurz} {bestell}".strip()


def tokenize(text: str) -> Set[str]:
    tokens = set(re.findall(r"\b[a-z0-9\.\-]+\b", text))
    return {t for t in tokens if len(t) > 1}


def extract_dimensions(text: str):
    return re.findall(r"\b\d+(?:\.\d+)?x\d+(?:\.\d+)?(?:x\d+(?:\.\d+)?)?(?:\s*mm)?\b", text)


def extract_standards(text: str):
    return re.findall(r"\b(?:din|iso|en iso)\s?\d+\b", text)


def extract_material_hints(text: str):
    material_keywords = [
        "kunststoff", "gummi", "elastomer", "stahl", "edelstahl",
        "messing", "aluminium", "kupfer", "nbr", "epdm", "fkm", "fpm",
        "viton", "silikon", "ptfe", "pvc", "pu", "pa", "pe", "pp"
    ]
    return [m for m in material_keywords if m in text]