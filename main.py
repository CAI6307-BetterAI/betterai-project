from database.database import Database
from pipeline_01_processing.pipeline import run_pipeline as run_pipeline_1
from pipeline_02_retrieval.pipeline import run_pipeline as run_pipeline_2


def main():
    db = Database()

    source_text = (
        "High blood pressure is a common condition that affects the body's arteries. "
        "It's also called hypertension. If you have high blood pressure, "
        "the force of the blood pushing against the artery walls is consistently too high. "
        "The heart has to work harder to pump blood."
    )

    query_text = "What is hypertension?"

    # Convert source text to rdf structure
    out_1 = run_pipeline_1(text=source_text)
    print("RDF input structure:", out_1)

    # Apply rdf structure to database
    db.apply_json(out_1)

    # Execute query against database
    out_2 = run_pipeline_2(text=query_text)
    print("Answer output:", out_2)


if __name__ == "__main__":
    main()
