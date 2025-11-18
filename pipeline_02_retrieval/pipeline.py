"""
Data Retrieval Pipline Entrypoint
"""

from typing import Optional

from common.tokenize import tokenize_text
from database.database import Database
# from pipeline_02_retrieval.patient_context import apply_patient_context
from pipeline_02_retrieval.sources import result_to_sources
from pipeline_02_retrieval.summarize import result_to_summary

from .schemas.output import Pipeline2Output
from .tokens_to_query import tokens_to_query


def run_pipeline(db: Database, text: str, patient_id: Optional[str] = None) -> Pipeline2Output:
    """
    Main function for data retrieval pipeline.

    Parameters
    ----------
    text (str) : String of text used for to create query.
    patient_id (str | None) : If provided, will apply query against patient context.

    Returns
    -------
    Output containing the answer summary and list of sources used to obtain summary.
    """

    # Step 1: Convert text to list of tokens using NER, POS, etc
    tokens = tokenize_text(text=text)

    # Step 2: Convert tokens to a structured query for database
    query = tokens_to_query(tokens=tokens)

    # Step 2.5: Optionally, apply patient context (disabled for now)
    # if patient_id:
    #     query = apply_patient_context(db, query=query, patient_id=patient_id)

    # Step 3: Execute query against the database
    try:
        res = db.graph.query(query)
    except Exception as e:
        # If the SPARQL query is malformed or execution fails, fall back to an empty result.
        # Log the offending query (truncated) to help with debugging.
        snippet = (query or "").replace("\n", " ")[:200]
        print(f"[Retrieval] SPARQL query failed; returning empty result. Error: {e}. Query snippet: {snippet!r}")
        res = None

    # Step 4: Get text summary from query result
    summary = result_to_summary(res)

    # Step 5: Get document sources from query result
    sources = result_to_sources(res)

    # Step 5: Combine everything, return
    output = Pipeline2Output(summary=summary, sources=sources)

    return output
