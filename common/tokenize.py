import spacy
from spacy.tokens.doc import Doc


def tokenize_text(text: str) -> Doc:
    """Given input text, return tokenized version used for processing."""

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    nlp.add_pipe("transformer", config={"model": {"name": "dmis-lab/biobert-v1.1"}})

    # TODO: ADD BIOBERT TOKENIZATION

    return doc
