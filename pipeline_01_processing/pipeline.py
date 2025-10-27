"""
Data Processing Pipline Entrypoint
"""

from common.tokenize import tokenize_text

from .tokens_to_rdf import tokens_to_rdf


def run_pipeline(text: str) -> object:
    """
    Main function for data processing pipeline.

    This pipeline takes in a long-form string of text and converts it to
    an RDF graph reprensentation.

    Parameters
    ----------
    text (str) : String of text used for processing.

    Returns
    -------
    Object in JSON-LD format representing the nodes created in the RDF database.
    """

    # Step 1: Convert text to tokens using NER, POS, etc
    tokens = tokenize_text(text)

    # Step 2: Convert tokens to RDF graph form
    graph = tokens_to_rdf(tokens)

    return graph
