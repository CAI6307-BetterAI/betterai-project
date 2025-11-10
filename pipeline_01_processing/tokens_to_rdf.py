from spacy.tokens.doc import Doc


def tokens_to_rdf(doc: Doc) -> list[dict]:
    """Convert a spaCy Doc to a simple list of triples.

    Emits a minimal structure consumable by Database.apply_json:
    [{"s": subject, "p": predicate, "o": object}, ...]
    """

    triples: list[dict] = []

    for sentence in doc.sents:
        verb = sentence.root
        subject = None
        obj = None

        for child in verb.children:
            if child.dep_ == "nsubj":
                subject = child
            elif child.dep_ in {"attr", "dobj", "pobj"}:
                obj = child

        if subject and obj and verb.lemma_:
            triples.append({
                "s": subject.lemma_,
                "p": verb.lemma_,
                "o": obj.lemma_,
            })

    return triples
