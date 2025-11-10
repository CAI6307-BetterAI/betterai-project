import spacy
from spacy.tokens.doc import Doc


def tokenize_text(text: str) -> Doc:
    """Given input text, return tokenized version used for processing."""

    nlp = spacy.load("en_core_web_sm")

    # Best-effort transformer setup; safe to skip if unavailable
    try:
        if "transformer" not in nlp.pipe_names:
            nlp.add_pipe("transformer", config={"model": {"name": "dmis-lab/biobert-v1.1"}})
    except Exception:
        pass

    doc = nlp(text)

    return doc
