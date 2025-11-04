import os
from typing import Optional

from rdflib import Graph


class Database:
    """Utility class to manage RDF graph."""

    instance: Optional["Database"] = None
    graph: Graph

    def __new__(cls) -> "Database":
        if not cls.instance:
            cls.instance = super().__new__(cls)

            graph = Graph()

            if os.path.exists("./graph.json"):
                graph.parse("./graph.json")

            graph.serialize(destination="./graph.json", format="json-ld")

            cls.instance.graph = graph

        return cls.instance

    def apply_json(self, payload: list[dict]):
        """Given a payload in JSON-LD format, apply it to the RDF database."""

        raise NotImplementedError()
