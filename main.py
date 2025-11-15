from database.database import Database
from pipeline_01_processing.pipeline import run_pipeline as run_pipeline_1
from pipeline_02_retrieval.pipeline import run_pipeline as run_pipeline_2


def main():
    """
    Main demo showing:
    1. Adding medical knowledge to RDF graph
    2. Querying without patient context
    3. Querying with patient context
    """
    
    print("="*70)
    print("BETTERAI PROJECT - MAIN DEMO")
    print("="*70)
    
    # Initialize RDF knowledge graph database
    db = Database()

    # Source text: Medical knowledge to add to the graph
    source_text = (
        "High blood pressure is a common condition that affects the body's arteries. "
        "It's also called hypertension. If you have high blood pressure, "
        "the force of the blood pushing against the artery walls is consistently too high. "
        "The heart has to work harder to pump blood."
    )

    print("\n[STEP 1] Converting source text to RDF structure...")
    print(f"Source text: {source_text[:80]}...")
    
    # Convert source text to rdf structure
    out_1 = run_pipeline_1(text=source_text)
    print(f"✓ Created {len(out_1)} RDF triples")
    print(f"Sample triples: {out_1[:2] if len(out_1) >= 2 else out_1}")

    print("\n[STEP 2] Adding RDF triples to knowledge graph database...")
    # Apply rdf structure to database
    db.apply_json(out_1)
    print("✓ Knowledge added to database")

    # Query without patient context
    query_text = "What is hypertension?"
    
    print("\n[STEP 3] Querying WITHOUT patient context...")
    print(f"Query: {query_text}")
    out_2 = run_pipeline_2(db=db, text=query_text)
    print(f"✓ Answer: {out_2}")

    # Query with patient context (will use default patient if DB not available)
    print("\n[STEP 4] Querying WITH patient context...")
    print(f"Query: {query_text}")
    print(f"Patient ID: P001 (will use default values if patient DB not configured)")
    out_3 = run_pipeline_2(db=db, text=query_text, patient_id="P001")
    print(f"✓ Answer with patient context: {out_3}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run 'uv run python main_patients.py' to manage patient records")
    print("  2. Configure .env file for PostgreSQL patient database (see env_template.txt)")
    print("  3. Add AI21_API_KEY to .env for AI-enhanced query context")
    print("="*70)


if __name__ == "__main__":
    main()
