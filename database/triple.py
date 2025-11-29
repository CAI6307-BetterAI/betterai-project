from typing import Union

import attrs

# Slot = Union[str | "Triple"]

SlotPrimitive = Union[str, int, "Triple"]


@attrs.define
class Slot:
    """Represents a single value in a triple."""

    value: SlotPrimitive

    def __repr__(self):
        if isinstance(self.value, str):
            return f'"{self.value}"'
        elif isinstance(self.value, int):
            return self.value
        else:
            return f"({self.value})"

    def __eq__(self, value):
        if value is None:
            return True
        elif isinstance(value, Slot):
            return value.value == self.value
        else:
            return value == self.value


SlotLike = Union[Slot, SlotPrimitive]


@attrs.define
class Triple:
    """
    Represents an RDF triple of the for <subject, predicate, object>
    """

    subject: Slot
    """Position 1 of triple, primary party of the triple statement."""

    predicate: Slot
    """Position 2 of triple, usually a verb, connects the subject and object."""

    object: Slot
    """Position 3 of triple, entity that is related to the subject."""

    def as_tuple(self):
        return (self.subject, self.predicate, self.object)

    def __repr__(self):
        return (
            f'<subject: {self.subject}, predicate: {self.predicate}, object: {self.object}>'
        )

    def __eq__(self, value):
        subject = None
        predicate = None
        object_ = None

        if isinstance(value, tuple):
            if not len(value) == 3:
                return False

            subject, predicate, object_ = value
        elif isinstance(value, Triple):
            subject, predicate, object_ = value.as_tuple()
        else:
            return False

        s_match = subject == self.subject if subject is not None else True
        p_match = predicate == self.predicate if predicate is not None else True
        o_match = object_ == self.object if object_ is not None else True

        return s_match and p_match and o_match
