import contractions
import spacy
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token


def tokenize_text(text: str, enable_bert=False) -> Doc:
    """Given input text, return tokenized version used for processing."""

    nlp = spacy.load("en_core_web_md")

    if enable_bert:
        # Best-effort transformer setup; safe to skip if unavailable
        try:
            if "transformer" not in nlp.pipe_names:
                nlp.add_pipe("transformer", config={"model": {"name": "dmis-lab/biobert-v1.1"}})
        except Exception:
            pass

    text = contractions.fix(text)

    # nlp.add_pipe("experimental_coref")
    # nlp.initialize()

    doc = nlp(text)

    # Add custom attribute "noun_chunk" to tokens
    Token.set_extension("noun_chunk", default=None, force=True)

    for noun in doc.noun_chunks:
        noun.root._.noun_chunk = noun

    return doc
