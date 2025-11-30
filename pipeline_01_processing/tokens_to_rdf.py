from typing import Optional

import attrs
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token

from database.rdf.triple import Node, Pred
from database.rdf.tripleset import TripleSet


@attrs.define
class TokenParser:
    """Convert tokens to different structures."""

    doc: Doc = attrs.field()
    source_id: str = attrs.field()
    tripleset = attrs.field(init=False, factory=lambda: TripleSet([]))

    def _repr_token(self, token: Token):
        return f"<{token} | pos:{token.pos_}, dep:{token.dep_}>"

    def _parse_token(self, token: Token, parent: Optional[Token] = None):
        """Process token."""

        parent_node = self.tripleset.get_or_create_node(parent, self.source_id)
        token_node = self.tripleset.get_or_create_node(token, self.source_id)
        alias_pred = self.tripleset.create_predicate("alias")
        alias_for_pred = self.tripleset.create_predicate("alias for")

        if token.dep_ == "appos" and parent is not None:
            parent = parent._.noun_chunk or parent

            if token.text.isupper():
                # Appositional modifier, like "HTN" for Hypertension
                self.tripleset.create_triple(parent_node, alias_pred, token_node)
                self.tripleset.create_triple(
                    token_node, alias_for_pred, parent_node, get_root=False
                )

        if list(token.children):
            for child in token.children:
                self._parse_token(child, parent=token)

    def _parse_span(
        self,
        span: Span,
        head: Optional[Node] = None,
    ):
        """Process groups of words, like sentences or sub groups."""

        subject: Optional[Node] = None
        verb: Optional[Pred] = None
        obj: Optional[Node] = None

        if span.root:
            verb = self.tripleset.create_predicate(span.root)

        for child in span.root.children:
            if child.dep_ == "nsubj":
                subject = self.tripleset.get_or_create_node(child, self.source_id)
                head = subject

            elif child.dep_ in {"attr", "dobj", "pobj", "oprd"}:
                obj = self.tripleset.get_or_create_node(child, self.source_id)

            elif child.dep_ == "nsubjpass":
                subject = head

            self._parse_token(child, parent=span.root)

            if child.pos_ == "NOUN":
                for inner_child in child.children:
                    if inner_child.pos_ == "VERB":
                        sub_verb = inner_child
                        sub_noun: Optional[Node] = None

                        for inner_sub_child in sub_verb.children:
                            if inner_sub_child.pos_ == "NOUN":
                                sub_noun = self.tripleset.get_or_create_node(
                                    inner_sub_child, self.source_id
                                )

                        if sub_verb and sub_noun and subject:
                            sub_verb = self.tripleset.create_predicate(sub_verb)
                            self.tripleset.create_triple(subject, sub_verb, sub_noun)

        if subject and obj and verb:
            self.tripleset.create_triple(subject, verb, obj)

        return head

    def parse_rdf_triples(self):
        """Return list of objects representing triples."""

        head: Node | None = None

        # Primary iteration through each sentence - O(n)
        for sentence in self.doc.sents:
            head = self._parse_span(sentence, head=head)


def tokens_to_rdf(doc: Doc, source_id: str) -> TripleSet:
    """Convert a spaCy Doc to a simple list of triples.

    Emits a minimal structure consumable by Database.apply_json:
    [{"s": subject, "p": predicate, "o": object}, ...]
    """

    parser = TokenParser(doc=doc, source_id=source_id)
    parser.parse_rdf_triples()

    return parser.tripleset
