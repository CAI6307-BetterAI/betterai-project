from collections.abc import Callable
from typing import Optional, TypeVar

import attrs
from spacy.tokens.span import Span
from spacy.tokens.token import Token

from database.triple import Slot, SlotLike, SlotPrimitive, Triple

T = TypeVar("T")


@attrs.define
class TripleSet:
    triples: list[Triple]

    def __str__(self):
        return f"[{', '.join([triple.__str__() for triple in self.triples])}]"

    def __iter__(self):
        return iter(self.triples)

    # ------------------------------------
    # Private Utility Methods
    # ------------------------------------

    @staticmethod
    def _slot_query(
        callable: Callable[["TripleSet", Optional[Slot], Optional[Slot], Optional[Slot], bool], T],
    ):
        """Allow input of raw values into function, and convert them to slots."""

        def wrapper(
            self,
            subject: Optional[SlotLike] = None,
            predicate: Optional[SlotLike] = None,
            object: Optional[SlotLike] = None,
            get_root: bool = False,
        ) -> T:

            if not isinstance(subject, Slot) and subject is not None:
                subject = Slot(subject)

            if not isinstance(predicate, Slot) and predicate is not None:
                predicate = Slot(predicate)

            if not isinstance(object, Slot) and object is not None:
                object = Slot(object)

            # subject = Slot(subject) if subject is not None else None
            # predicate = Slot(predicate) if predicate is not None else None
            # object = Slot(object) if object is not None else None

            return callable(self, subject, predicate, object, get_root=get_root)

        return wrapper

    def _get_root_subject(self, subject: Slot) -> Slot:
        """Get the root triple for a subject."""

        alias = self.get_or_none(predicate="alias", object=subject)

        if not alias:
            return subject

        while True:
            new_alias = self.get_or_none(predicate="alias", object=alias)
            if not new_alias:
                break
            else:
                alias = new_alias

        return alias.subject

    # ------------------------------------
    # Query Methods
    # ------------------------------------

    @_slot_query
    def get_or_none(
        self,
        subject: Optional[Slot] = None,
        predicate: Optional[Slot] = None,
        object: Optional[Slot] = None,
        get_root=False,
    ) -> Triple | None:
        """
        Find first matching triple or none.

        If root=True, will swap out subject for the top most parent node
        if applicable. Ex: "HTN" would be replaced with "hypertension".
        """

        assert (
            subject is not None or predicate is not None or object is not None
        ), "Must provide a subject, predicate, and/or object"

        if get_root is True and subject is not None:
            subject = self._get_root_subject(subject)

        return next(
            (triple for triple in self.triples if triple == (subject, predicate, object)), None
        )

    @_slot_query
    def filter(
        self,
        subject: Optional[Slot] = None,
        predicate: Optional[Slot] = None,
        object: Optional[Slot] = None,
        get_root=False,
    ) -> "TripleSet":
        """Return new TripleSet with triples that match query."""

        if get_root is True:
            subject = self._get_root_subject(subject)

        filtered_triples = [
            triple for triple in self.triples if triple == (subject, predicate, object)
        ]

        return TripleSet(filtered_triples)

    def count(self):
        """Get number of triples in tripleset."""

        return len(self.triples)

    # ------------------------------------
    # Management Methods
    # ------------------------------------

    def get_or_create(
        self,
        subject: Token | SlotPrimitive,
        predicate: Token | SlotPrimitive,
        object: Token | SlotPrimitive,
        get_root=True,
    ):
        """Get one or create a new triple."""

        if isinstance(subject, Token) or isinstance(subject, Span):
            subject = subject.lemma_

        if isinstance(predicate, Token or isinstance(predicate, Span)):
            predicate = predicate.lemma_

        if isinstance(object, Token) or isinstance(object, Span):
            object = object.lemma_

        if get_root:
            subject = self._get_root_subject(Slot(subject))

        triple = self.get_or_none(subject, predicate, object)

        if not triple:
            triple = Triple(subject, predicate, object)
            self.triples.append(triple)

        return triple

    def create(
        self,
        subject: Token | SlotPrimitive,
        predicate: Token | SlotPrimitive,
        object: Token | SlotPrimitive,
        get_root=True,
    ):
        """Create new triple and add to TripleSet."""

        return self.get_or_create(subject, predicate, object, get_root=get_root)
