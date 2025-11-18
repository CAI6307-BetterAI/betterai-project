from typing import Optional

import attrs
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token

from database.tripleset import TripleSet


@attrs.define
class TokenParser:
    """Convert tokens to different structures."""

    doc: Doc = attrs.field()
    tripleset = attrs.field(init=False, factory=lambda: TripleSet([]))

    def _repr_token(self, token: Token):
        return f"<{token} | pos:{token.pos_}, dep:{token.dep_}>"

    def _create_noun_chunks(self) -> dict[Token, Span]:
        """Generate a dict of noun chunks with the key as the root."""

        chunks = {}

        for noun in self.doc.noun_chunks:
            chunks[noun.root] = noun

        return chunks

    def _parse_token(self, token: Token, parent: Optional[Token] = None):
        """Process token."""

        if token.dep_ == "appos":
            # Appositional modifier, like "HTN" for Hypertension
            self.tripleset.create(parent, "alias", token)
            self.tripleset.create(token, "alias for", parent, get_root=False)

        if list(token.children):
            for child in token.children:
                self._parse_token(child, parent=token)

    def _parse_span(
        self,
        span: Span,
        head: Optional[Token] = None,
        noun_chunks: Optional[dict[Token, Span]] = None,
    ):
        """Process groups of words, like sentences or sub groups."""

        noun_chunks = noun_chunks or {}
        # triples: list[Triple] = []

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

            self._parse_token(child, parent=verb)

            if child.pos_ == "NOUN":
                for inner_child in child.children:
                    if inner_child.pos_ == "VERB":
                        sub_verb = inner_child
                        sub_noun = None

                        for inner_sub_child in sub_verb.children:
                            if inner_sub_child.pos_ == "NOUN":
                                sub_noun = noun_chunks.get(inner_sub_child, inner_sub_child)

                        if sub_verb and sub_noun and subject:
                            self.tripleset.create(subject, sub_verb, sub_noun)

        if subject and obj and verb.lemma_:
            self.tripleset.create(subject, verb, obj)

        return head

    def parse_rdf_triples(self):
        """Return list of objects representing triples."""

        noun_chunks = self._create_noun_chunks()
        head: Token | Span | None = None

        # Primary iteration through each sentence - O(n)
        for sentence in self.doc.sents:
            head = self._parse_span(sentence, head=head, noun_chunks=noun_chunks)


def tokens_to_rdf(doc: Doc) -> TripleSet:
    """Convert a spaCy Doc to a simple list of triples.

    Emits a minimal structure consumable by Database.apply_json:
    [{"s": subject, "p": predicate, "o": object}, ...]
    """

    parser = TokenParser(doc=doc)
    parser.parse_rdf_triples()

    return parser.tripleset
