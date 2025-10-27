from rdflib.plugins.sparql.sparql import Query


def tokens_to_query(tokens: list) -> str | Query:
    """Convert list of tokens to queries that can be executed against RDF database."""

    raise NotImplementedError()
