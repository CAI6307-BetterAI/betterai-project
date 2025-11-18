import contractions
import spacy
from spacy.tokens.doc import Doc


# Load the spaCy model once at import time and reuse it.
_NLP = spacy.load("en_core_web_sm")


def tokenize_text(text: str, enable_bert: bool = False) -> Doc:
    """Given input text, return tokenized version used for processing."""

    nlp = _NLP

    if enable_bert:
        # Best-effort transformer setup; safe to skip if unavailable
        try:
            if "transformer" not in nlp.pipe_names:
                nlp.add_pipe(
                    "transformer",
                    config={"model": {"name": "dmis-lab/biobert-v1.1"}},
                )
        except Exception:
            # If transformers or the specific model isn't available, fall back gracefully.
            pass

    text = contractions.fix(text)
    return nlp(text)
