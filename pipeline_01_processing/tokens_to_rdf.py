from typing import Optional

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

    def _repr_token(self, token: Token):
        return f"<{token} | pos:{token.pos_}, dep:{token.dep_}>"

    def _create_noun_chunks(self) -> dict[Token, Span]:
        """Generate a dict of noun chunks with the key as the root."""

        chunks = {}

        for noun in self.doc.noun_chunks:
            chunks[noun.root] = noun

        return chunks

    def _parse_span(
        self,
        span: Span,
        head: Optional[Token] = None,
        noun_chunks: Optional[dict[Token, Span]] = None,
    ):
        """Process groups of words, like sentences or sub groups."""

        noun_chunks = noun_chunks or {}
        triples: list[Triple] = []

        subject = None
        verb = span.root
        obj = None

        for child in verb.children:
            if child.dep_ == "nsubj":
                subject = noun_chunks.get(child, child)
                head = subject
            elif child.dep_ in {"attr", "dobj", "pobj", "oprd"}:
                obj = noun_chunks.get(child, child)
            elif child.dep_ == "nsubjpass":
                subject = head
            elif child.dep_ == "appos":
                print('appos:', child)

            if child.pos_ == "NOUN":
                for inner_child in child.children:
                    if inner_child.pos_ == "VERB":
                        sub_verb = inner_child
                        sub_noun = None

                        for inner_sub_child in sub_verb.children:
                            if inner_sub_child.pos_ == "NOUN":
                                sub_noun = noun_chunks.get(inner_sub_child, inner_sub_child)

                        if sub_verb and sub_noun and subject:
                            triples.append(Triple(subject.lemma_, sub_verb.lemma_, sub_noun.lemma_))

        if subject and obj and verb.lemma_:
            triples.append(Triple(subject.lemma_, verb.lemma_, obj.lemma_))

        return triples, head

    def get_rdf_triples(self):
        """Return list of objects representing triples."""

        triples: list[Triple] = []

        noun_chunks = self._create_noun_chunks()
        head: Token | Span | None = None

        # Primary iteration through each sentence - O(n)
        for sentence in self.doc.sents:
            res_triples, head = self._parse_span(sentence, head=head, noun_chunks=noun_chunks)
            triples = [*triples, *res_triples]

        return triples


def tokens_to_rdf(doc: Doc) -> TripleSet:
    """Convert a spaCy Doc to a simple list of triples.

    Emits a minimal structure consumable by Database.apply_json:
    [{"s": subject, "p": predicate, "o": object}, ...]
    """

    parser = TokenParser(doc=doc)
    triples = parser.get_rdf_triples()

    return TripleSet(triples)
