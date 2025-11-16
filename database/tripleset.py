from collections.abc import Callable
from typing import Optional, TypeVar

import attrs

from database.triple import Slot, SlotLike, Triple

T = TypeVar("T")


@attrs.define
class TripleSet:
    triples: list[Triple]

    def __str__(self):
        return f"[{', '.join([triple.__str__() for triple in self.triples])}]"

    def __iter__(self):
        return iter(self.triples)

    @staticmethod
    def _slot_query(
        callable: Callable[["TripleSet", Optional[Slot], Optional[Slot], Optional[Slot]], T],
    ):
        """Allow input of raw values into function, and convert them to slots."""

        def wrapper(
            self,
            subject: Optional[SlotLike] = None,
            predicate: Optional[SlotLike] = None,
            object: Optional[SlotLike] = None,
        ) -> T:
            subject = Slot(subject) if subject is not None else None
            predicate = Slot(predicate) if predicate is not None else None
            object = Slot(object) if object is not None else None

            return callable(self, subject, predicate, object)

        return wrapper

    @_slot_query
    def get_or_none(
        self,
        subject: Optional[Slot] = None,
        predicate: Optional[Slot] = None,
        object: Optional[Slot] = None,
    ) -> Triple | None:
        """Find first matching triple or none."""

        assert (
            subject is not None or predicate is not None or object is not None
        ), "Must provide a subject, predicate, and/or object"

        return next(
            (triple for triple in self.triples if triple == (subject, predicate, object)), None
        )

    @_slot_query
    def filter(
        self,
        subject: Optional[Slot] = None,
        predicate: Optional[Slot] = None,
        object: Optional[Slot] = None,
    ) -> "TripleSet":
        """Return new TripleSet with triples that match query."""

        filtered_triples = [
            triple for triple in self.triples if triple == (subject, predicate, object)
        ]

        return TripleSet(filtered_triples)

    def count(self):
        """Get number of triples in tripleset."""

        return len(self.triples)
