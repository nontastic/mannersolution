# src/matcher.py

from difflib import SequenceMatcher
from typing import Dict, List
from config import GENERIC_WORDS, IMPORTANT_KEYWORDS


def sequence_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def token_overlap_score(tokens_a: set, tokens_b: set) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union) if union else 0.0


def keyword_bonus(erp_tokens: set, cn_tokens: set) -> float:
    common_important = (erp_tokens & cn_tokens) & IMPORTANT_KEYWORDS
    return min(len(common_important) * 0.08, 0.30)


def material_bonus(erp_text: str, cn_text: str) -> float:
    material_words = [
        "kunststoff", "gummi", "elastomer", "stahl", "edelstahl",
        "messing", "aluminium", "kupfer", "nbr", "epdm", "fkm", "fpm",
        "viton", "silikon", "ptfe", "pvc", "pu", "pa", "pe", "pp"
    ]
    bonus = 0.0
    for word in material_words:
        if word in erp_text and word in cn_text:
            bonus += 0.05
    return min(bonus, 0.20)


def generic_penalty(cn_tokens: set) -> float:
    # Sehr generische Texte etwas abwerten
    non_generic = [t for t in cn_tokens if t not in GENERIC_WORDS]
    if len(non_generic) <= 2:
        return 0.10
    return 0.0


def calculate_match_score(erp_text: str, erp_tokens: set, cn_text: str, cn_tokens: set) -> Dict[str, float]:
    seq_score = sequence_similarity(erp_text, cn_text)
    overlap = token_overlap_score(erp_tokens, cn_tokens)
    kw_bonus = keyword_bonus(erp_tokens, cn_tokens)
    mat_bonus = material_bonus(erp_text, cn_text)
    penalty = generic_penalty(cn_tokens)

    final_score = (
        0.45 * seq_score +
        0.45 * overlap +
        kw_bonus +
        mat_bonus -
        penalty
    )

    final_score = max(0.0, min(1.0, final_score))

    return {
        "seq_score": seq_score,
        "overlap_score": overlap,
        "keyword_bonus": kw_bonus,
        "material_bonus": mat_bonus,
        "penalty": penalty,
        "final_score": final_score,
    }


def score_all_candidates(erp_text: str, erp_tokens: set, cn_df) -> List[dict]:
    results = []

    for _, row in cn_df.iterrows():
        scores = calculate_match_score(
            erp_text=erp_text,
            erp_tokens=erp_tokens,
            cn_text=row["norm_text"],
            cn_tokens=row["tokens"]
        )

        results.append({
            "CN_CODE": row["CN_CODE"],
            "SelfText_DE": row["SelfText_DE"],
            "chapter_2": row["chapter_2"],
            "heading_4": row["heading_4"],
            "subheading_6": row["subheading_6"],
            **scores
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results