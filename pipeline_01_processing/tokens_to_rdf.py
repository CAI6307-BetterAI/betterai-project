from spacy.tokens.doc import Doc


def tokens_to_rdf(doc: Doc) -> list[dict]:
    """Convert list of tokens to an rdf graph structure."""

    nodes = {}

    for noun in doc.noun_chunks:
        node = {
            "@id": noun.lemma_,
        }

        nodes[noun] = node

    for sentence in doc.sents:
        verb = sentence.root
        subject = None
        attribute = None

        for child in verb.children:
            if child.dep_ == "nsubj":
                subject = child
            elif child.dep_ == "attr":
                attribute = child

        if not (subject and attribute):
            continue

        if subject not in nodes.keys():
            # print('larger group:', list(subject.children))
            nodes[subject] = {"@id": subject}
            # print('subject vect:', subject.vector)

        subject_node = nodes.get(subject)
        # attribute_node = nodes.get(attribute)
        # print("verb lemma:", verb.lemma_)
        # print("subject node:", subject_node)

        subject_node[verb.lemma_] = attribute

    print("nodes:", nodes)

    return nodes.values()
