"""
Data Retrieval Pipline Entrypoint
"""

from typing import Optional

from pipeline_02_retrieval.schemas.output import Pipeline2Output


def run_pipeline(text: str, patient_id: Optional[str] = None) -> Pipeline2Output:
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

    raise NotImplementedError()
