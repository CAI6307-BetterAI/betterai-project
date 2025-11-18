from __future__ import annotations

from textwrap import dedent
import re

from spacy.tokens import Doc

EX = "http://example.org/med#"

PRED_MAP = {
    "mechanism_of_action": f"<{EX}hasMechanismOfAction>",
    "indication":          f"<{EX}indicatedFor>",
    "contraindication":    f"<{EX}contraindicatedIn>",
    "adverse_effect":      f"<{EX}hasAdverseEffect>",
    "dose":                f"<{EX}recommendedDose>",
    "drug_target":         f"<{EX}targets>",
}

# Mentions we never want to treat as the subject
_STOP_MENTIONS = {
    "which enzyme",
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "enzyme",
    "drug",
    "medicine",
    # Additional generic/question words we never want as subject mentions
    "do",
    "does",
    "did",
    "is",
    "are",
    "was",
    "were",
    "can",
    "could",
    "would",
    "should",
    "may",
    "might",
    "will",
    "shall",
}

# --- Intent detection patterns (your logic) -----------------------------------

_INTENT_PATTERNS = [
    (
        "mechanism_of_action",
        re.compile(
            r"\bmechanism of action\b|\bacts by\b|\binhibit(s|ing)?\b|\bstimulate(s|ing)?\b",
            re.I,
        ),
    ),
    (
        "indication",
        re.compile(
            r"\bindication(s)?\b|\bused for\b|\btreat(s|ment)? of\b",
            re.I,
        ),
    ),
    (
        "contraindication",
        re.compile(
            r"\bcontraindication(s)?\b|\bcontraindicated\b|\bavoid in\b",
            re.I,
        ),
    ),
    (
        "adverse_effect",
        re.compile(
            r"\bside effect(s)?\b|\badverse\b|\btoxicit(y|ies)\b",
            re.I,
        ),
    ),
    (
        "dose",
        re.compile(
            r"\bdose|dosage|dosing\b",
            re.I,
        ),
    ),
    (
        "drug_target",
        re.compile(
            r"\btarget(s)?\b|\bbinds?\b|\breceptor\b|\benzyme\b",
            re.I,
        ),
    ),
]


def _detect_intent(text: str) -> str | None:
    """Infer high-level intent (what relation is being asked about) from raw text."""
    for name, pat in _INTENT_PATTERNS:
        if pat.search(text):
            return name
    # Very rough fallback: "what ..." questions → assume mechanism_of_action
    if re.match(r"^\s*what\b", text.strip(), re.I):
        return "mechanism_of_action"
    return None


# --- Mention extraction (your improved heuristic) -----------------------------


def _extract_mentions(doc: Doc) -> list[str]:
    """
    Extract candidate 'mentions' (drug names, enzymes, etc.) from a Doc.

    Strategy:
      1. Prefer named entities (doc.ents) if available.
      2. Add noun chunks.
      3. Add capitalized / chemical-ish single tokens.
      4. De-duplicate (case-insensitive), keep track of first-seen position.
      5. Sort: longer first, tie-break by original position.
    """
    cands_with_pos: list[tuple[str, int]] = []
    seen_lower: set[str] = set()

    def _add(s: str, pos: int):
        s = s.strip()
        # Ignore very short fragments; they tend to be auxiliaries like "Do", "Is".
        if not (3 <= len(s) <= 80):
            return
        k = s.lower()
        if k in seen_lower:
            return
        seen_lower.add(k)
        cands_with_pos.append((s, pos))

    pos = 0

    # 1) named entities, if available
    if getattr(doc, "ents", None):
        for ent in doc.ents:
            _add(ent.text, pos)
            pos += 1

    # 2) noun chunks
    for span in getattr(doc, "noun_chunks", []):
        _add(span.text, pos)
        pos += 1

    # 3) capitalized / chemical-ish single tokens
    for t in doc:
        if re.search(r"[A-Za-z0-9α-ωΑ-Ω\-]+", t.text) and (
            t.shape_ in {"Xxxx", "XX", "XXX", "Xx"} or "-" in t.text
        ):
            _add(t.text, pos)
            pos += 1

    # 4) sort: longer first, tie-break by original position
    cands_with_pos.sort(key=lambda p: (-len(p[0]), p[1]))

    # 5) return just the strings
    return [s for s, _ in cands_with_pos]


# --- Subject / label binding helpers -----------------------------------------


def _sanitize_mention(m: str) -> str:
    # Keep only harmless chars inside a quoted string
    m = re.sub(r'["\\]', " ", m)
    return " ".join(m.split()).strip()


def _pick_best_mention(mentions: list[str]) -> str | None:
    """
    From a list of mention strings, pick the best candidate for the subject.
    """
    # 1) prefer good-looking biomedical strings with uppercase/digits/hyphens
    for m in mentions:
        m_clean = m.strip()
        if not m_clean:
            continue
        low = m_clean.lower()
        if low in _STOP_MENTIONS:
            continue
        if re.search(r"[A-Z0-9\-]", m_clean):
            return m_clean

    # 2) fallback: first non-stop mention
    for m in mentions:
        if m.strip().lower() not in _STOP_MENTIONS:
            return m.strip()

    return None


def _wrap_prefixes(q: str) -> str:
    return dedent(
        f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        {q.strip()}
        """
    ).strip()


def _subject_binding_inline_filter(mention: str) -> str:
    """
    Bind ?subj by label using inline FILTER (no sub-SELECT).
    Uses a simple case-insensitive CONTAINS to avoid regex-related parse issues.
    """
    m = _sanitize_mention(mention)
    return dedent(
        f"""
          ?subj rdfs:label ?lbl .
          FILTER( CONTAINS(LCASE(STR(?lbl)), LCASE("{m}")) )
        """
    ).strip()


# --- Main: Doc → SPARQL query -------------------------------------------------


def tokens_to_query(tokens: Doc) -> str:
    """
    Convert a spaCy Doc (tokenized question) into a SPARQL query string.

    This uses:
      - intent detection (mechanism_of_action, indication, etc.)
      - mention extraction (drug/target/etc. names)
      - label-based subject binding in the RDF graph
    """

    text = tokens.text

    # 1) Extract candidate mentions from the Doc
    mentions = _extract_mentions(tokens)

    # 2) Expand mentions using abbreviations, if SciSpaCy abbreviation detector is present
    abbrev_map: dict[str, str] = {}
    if hasattr(tokens._, "abbreviations"):
        for ab in getattr(tokens._, "abbreviations", []):
            abbrev_map[str(ab)] = str(ab._.long_form)

    expanded = [abbrev_map.get(m, m) for m in mentions]
    # deduplicate while preserving order
    mentions = list(dict.fromkeys(expanded))

    # 3) Detect intent from the raw text
    intent = _detect_intent(text)

    # 4) Choose the best subject mention
    chosen = _pick_best_mention(mentions)
    if not chosen:
        # Harmless always-empty query if we couldn't find a subject
        return _wrap_prefixes("SELECT ?answer WHERE { VALUES ?answer { } }")

    subj_bind = _subject_binding_inline_filter(chosen)

    # 5) If we know the intent, map it to a predicate and query for answers
    if intent in PRED_MAP:
        pred = PRED_MAP[intent]
        body = dedent(
            f"""
            SELECT ?answer ?answerLabel WHERE {{
              {subj_bind}
              ?subj {pred} ?answer .
              OPTIONAL {{ ?answer rdfs:label ?answerLabel . }}
            }}
            LIMIT 50
            """
        )
        return _wrap_prefixes(body)

    # 6) Fallback: explore outgoing edges from the subject
    body = dedent(
        f"""
        SELECT ?predicate ?object ?objectLabel WHERE {{
          {subj_bind}
          ?subj ?predicate ?object .
          OPTIONAL {{ ?object rdfs:label ?objectLabel . }}
        }}
        LIMIT 100
        """
    )
    return _wrap_prefixes(body)
