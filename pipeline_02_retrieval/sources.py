from types import NotImplementedType

from rdflib.query import Result

from .schemas.doc import DocSource


def result_to_sources(res: Result) -> list[DocSource]:
    """Convert RDF query result to a list of document sources."""

    raise NotImplementedType()
