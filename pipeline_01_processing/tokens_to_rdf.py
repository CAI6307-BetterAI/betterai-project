import attrs
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token

from database.triple import Triple
from database.tripleset import TripleSet


@attrs.define
class TokenParser:
    """Convert tokens to different structures."""

    doc: Doc

    def _create_noun_chunks(self) -> dict[Token, Span]:
        """Generate a dict of noun chunks with the key as the root."""

        chunks = {}

        for noun in self.doc.noun_chunks:
            chunks[noun.root] = noun

        return chunks

    def get_rdf_triples(self):
        """Return list of objects representing triples."""

        triples: list[Triple] = []

        noun_chunks = self._create_noun_chunks()
        head: Token | Span | None = None

        # Primary iteration through each sentence - O(n)
        for sentence in self.doc.sents:
            subject = None
            verb = sentence.root
            obj = None

            for child in verb.children:
                if child.dep_ == "nsubj":
                    # subject = child
                    subject = noun_chunks.get(child, child)
                    head = subject
                elif child.dep_ in {"attr", "dobj", "pobj", "oprd"}:
                    obj = noun_chunks.get(child, child)
                elif child.dep_ == "nsubjpass":
                    # print("pronoun:", child)
                    subject = head

                if child.pos_ == "NOUN":
                    for inner_child in child.children:
                        if inner_child.pos_ == "VERB":
                            sub_verb = inner_child
                            sub_noun = None

                            for inner_sub_child in sub_verb.children:
                                if inner_sub_child.pos_ == "NOUN":
                                    sub_noun = noun_chunks.get(inner_sub_child, inner_sub_child)

                            if sub_verb and sub_noun and subject:
                                triples.append(
                                    Triple(subject.lemma_, sub_verb.lemma_, sub_noun.lemma_)
                                )
                    #         print("sub children:", list(sub_verb.children))

                    # print(
                    #     "children:",
                    #     " ".join(
                    #         [f"<{c} | pos:{c.pos_}, dep:{c.dep_}>" for c in list(child.children)]
                    #     ),
                    # )

            #     print(f"\nCHILD {child} =========")
            #     print("pos:", child.pos_)
            #     print("dep:", child.dep_)
            #     print("head:", child.head)
            #     # print("children:", list(child.rights))

            # print("subject:", subject)
            # print("verb:", verb)
            # print("obj:", obj)

            if subject and obj and verb.lemma_:
                triples.append(Triple(subject.lemma_, verb.lemma_, obj.lemma_))

        return triples


def tokens_to_rdf(doc: Doc) -> TripleSet:
    """Convert a spaCy Doc to a simple list of triples.

    Emits a minimal structure consumable by Database.apply_json:
    [{"s": subject, "p": predicate, "o": object}, ...]
    """

    parser = TokenParser(doc=doc)
    triples = parser.get_rdf_triples()

    return TripleSet(triples)
