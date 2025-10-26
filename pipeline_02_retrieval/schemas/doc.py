"""
Schemas related to documents and positions within documents.
"""

import attr


@attr.s
class DocPosition:
    """Represents a single location inside of a large document."""

    line: int = attr.ib()
    """Line number, 0 indexed."""

    word: int = attr.ib()
    """Word number inside of line, 0 indexed."""


@attr.s
class DocSource:
    """Used to reference a specific area of a document."""

    pdf_url: str = attr.ib()
    """Full url to external pdf."""

    start: DocPosition = attr.ib()
    """Starting position of highlighed region in document."""

    end: DocPosition = attr.ib()
    """Ending position of highlighed region in document."""
