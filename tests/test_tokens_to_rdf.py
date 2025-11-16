from common.tokenize import tokenize_text
from database.tripleset import TripleSet
from pipeline_01_processing.tokens_to_rdf import tokens_to_rdf


def test_generate_noun_attributes():
    """Should generate noun chunks."""

    source_text = (
        "High blood pressure is a common condition that affects the body's arteries. "
        "It's also called hypertension. If you have high blood pressure, "
        "the force of the blood pushing against the artery walls is consistently too high. "
        "The heart has to work harder to pump blood."
    )

    doc = tokenize_text(source_text)
    rdf_rep = tokens_to_rdf(doc)
    tripleset = TripleSet(rdf_rep)

    bp = tripleset.filter(subject="high blood pressure")
    assert bp.count() >= 3, bp

    t_condition = bp.get_or_none(predicate="be", object="a common condition")
    assert t_condition is not None

    t_hypertension = bp.get_or_none(predicate="call", object="hypertension")
    assert t_hypertension is not None

    t_affects = bp.get_or_none(predicate="affect", object="the body's artery")
    assert t_affects is not None
