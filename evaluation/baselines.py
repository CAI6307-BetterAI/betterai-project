from typing import Dict


def always_yes(_: Dict) -> str:
    return "yes"


NEG_CUES = {" not ", " no ", " without ", " lack ", " none ", " absent "}


def heuristic_yesno(sample: Dict) -> str:
    """Very simple heuristic for yes/no.

    - If question contains explicit negation cues → 'no'
    - Else default to 'yes'
    """
    q = f" {sample.get('question', '').lower()} "
    if any(c in q for c in NEG_CUES):
        return "no"
    return "yes"

