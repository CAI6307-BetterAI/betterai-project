import os
from typing import Optional

from rdflib import Graph


class Database:

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

    def apply_json(self, payload: object):
        """Given a payload in JSON-LD format, apply it to the RDF database."""

        raise NotImplementedError()
