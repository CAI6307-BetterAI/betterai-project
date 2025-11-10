from rdflib.plugins.sparql.sparql import Query


def tokens_to_query(tokens: list | object) -> str | Query:
    """Convert tokens to a simple SPARQL query.

    Minimal baseline that retrieves generic triples. This makes the
    pipeline runnable end-to-end and can be refined later to construct
    domain-specific queries from tokens.
    """

    return (
        """
        SELECT ?s ?p ?o WHERE {
          ?s ?p ?o .
        }
        LIMIT 10
        """
        .strip()
    )
