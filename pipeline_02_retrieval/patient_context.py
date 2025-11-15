import os
from typing import Union

from ai21 import AI21Client
from ai21.models.chat import ChatMessage
from rdflib.plugins.sparql.sparql import Query

from database.database import Database
from pipeline_02_retrieval.patientDB.operations import get_patient_history


def apply_patient_context(db: Database, query: str | Query, patient_id: str) -> str | Query:
    """Apply patient context to query using Jamba AI model.

    This function retrieves patient information from the patient database and uses
    the Jamba AI model to enhance the query with relevant patient context.

    Args:
        db: RDF Database instance (not used for patient data, but kept for compatibility)
        query: The original query (string or Query object)
        patient_id: Patient ID to fetch context for

    Returns:
        Enhanced query with patient context applied (same type as input)
    """
    # Fetch patient data from PostgreSQL patient database
    try:
        patient_data = get_patient_history(patient_id)
        
        if not patient_data:
            # If no patient data found, use default values
            print(f"Patient {patient_id} not found. Using default patient context.")
            patient_data = _get_default_patient_data(patient_id)
        
        # Build patient context string
        context_info = _build_patient_context_string(patient_data)
        
    except Exception as e:
        print(f"Warning: Could not fetch patient data: {e}")
        print(f"Using default patient context for {patient_id}")
        # Use default patient data if we can't connect to patient DB
        patient_data = _get_default_patient_data(patient_id)
        context_info = _build_patient_context_string(patient_data)

    # Get API key from environment or use default
    api_key = os.getenv("AI21_API_KEY", "07309e04-89f4-49b1-9ffa-8e9667e67038")
    if not api_key:
        print("Warning: AI21_API_KEY is not set. Returning query without AI enhancement.")
        print(f"Patient context that would be applied:\n{context_info}\n")
        return query

    # Initialize Jamba client
    model = "jamba-large"
    client = AI21Client(api_key=api_key)

    # Convert Query object to string if necessary
    is_query_object = isinstance(query, Query)
    query_str = str(query) if is_query_object else query

    # Build prompt for Jamba AI model
    prompt = f"""You are a medical AI assistant helping to enhance database queries with patient context.

{context_info}

Original Query:
{query_str}

Task: Enhance this query to incorporate relevant patient context. Consider the patient's medical history, 
past surgeries, and clinical notes when refining the query. Return ONLY the enhanced query without 
additional explanation.

Enhanced Query:"""

    # Create chat message
    messages = [ChatMessage(role="user", content=prompt)]

    # Call Jamba AI model
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=0.95,
        )

        # Extract enhanced query from response
        enhanced_query = response.choices[0].message.content.strip()

        # If input was a Query object, try to parse the enhanced query back to Query
        if is_query_object:
            try:
                # Return enhanced query as Query object
                # Note: This may require additional parsing logic depending on your Query class
                return Query.parseString(enhanced_query)
            except Exception:
                # If parsing fails, return as string
                return enhanced_query
        else:
            return enhanced_query

    except Exception as e:
        print(f"Warning: Jamba AI enhancement failed: {e}")
        # Return original query if AI enhancement fails
        return query


def _get_default_patient_data(patient_id: str) -> dict:
    """Return default patient data when patient is not found in database.
    
    Args:
        patient_id: Patient ID to use in default data
    
    Returns:
        Dictionary with default patient information
    """
    return {
        "patient_id": patient_id,
        "name": "Unknown Patient",
        "age": 45,
        "sex": "Unknown",
        "past_surgeries": ["None recorded"],
        "avg_blood_pressure": "120/80",
        "notes": ["No medical history available for this patient."]
    }


def _build_patient_context_string(patient_data: dict) -> str:
    """Build a formatted patient context string from database results.

    Args:
        patient_data: Dictionary containing patient information from database

    Returns:
        Formatted patient context string
    """
    context_parts = ["=== PATIENT CONTEXT ===\n"]

    # Add basic patient information
    if "patient_id" in patient_data:
        context_parts.append(f"Patient ID: {patient_data['patient_id']}")
    if "name" in patient_data:
        context_parts.append(f"Name: {patient_data['name']}")
    if "age" in patient_data:
        context_parts.append(f"Age: {patient_data['age']}")
    if "sex" in patient_data:
        context_parts.append(f"Sex: {patient_data['sex']}")
    if "past_surgeries" in patient_data:
        surgeries = patient_data['past_surgeries']
        if isinstance(surgeries, list):
            surgeries = ", ".join(surgeries)
        context_parts.append(f"Past Surgeries: {surgeries}")
    if "avg_blood_pressure" in patient_data:
        context_parts.append(f"Average Blood Pressure: {patient_data['avg_blood_pressure']}")

    # Add clinical notes if available
    if "notes" in patient_data and patient_data["notes"]:
        context_parts.append("\n=== CLINICAL NOTES ===")
        notes = patient_data["notes"]
        if isinstance(notes, list):
            for i, note in enumerate(notes, 1):
                if note:  # Skip None/empty notes
                    context_parts.append(f"\n[Note {i}]")
                    context_parts.append(str(note))

    return "\n".join(context_parts)


def enhance_query_with_jamba(query: str, context: str, api_key: str = None) -> str:
    """Standalone function to enhance any query with custom context using Jamba.

    Args:
        query: The original query string
        context: Custom context information to apply
        api_key: Optional API key (uses environment variable if not provided)

    Returns:
        Enhanced query string
    """
    if api_key is None:
        api_key = os.getenv("AI21_API_KEY", "07309e04-89f4-49b1-9ffa-8e9667e67038")
    
    if not api_key:
        raise RuntimeError("AI21_API_KEY is not set.")

    model = "jamba-large"
    client = AI21Client(api_key=api_key)

    prompt = f"""Context Information:
{context}

Original Query:
{query}

Task: Enhance this query using the provided context. Return ONLY the enhanced query.

Enhanced Query:"""

    messages = [ChatMessage(role="user", content=prompt)]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=500,
        temperature=0.7,
        top_p=0.95,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # Example usage
    print("Patient Context Module - Jamba AI Integration")
    print("=" * 50)
    
    # Example: Test the context builder
    sample_patient_data = {
        "patient_id": "P001",
        "name": "John Doe",
        "age": 45,
        "sex": "M",
        "past_surgeries": "Appendectomy (2015)",
        "avg_blood_pressure": 120.5,
        "notes": [
            "Patient presents with mild chest pain. ECG normal.",
            "Follow-up: Chest pain resolved. Prescribed rest."
        ]
    }
    
    context_str = _build_patient_context_string(sample_patient_data)
    print(context_str)
    print("\n" + "=" * 50 + "\n")
    
    # Example: Test query enhancement
    sample_query = "SELECT * FROM medical_records WHERE condition = 'chest_pain'"
    print(f"Original Query:\n{sample_query}\n")
    
    try:
        enhanced = enhance_query_with_jamba(sample_query, context_str)
        print(f"Enhanced Query:\n{enhanced}")
    except Exception as e:
        print(f"Enhancement failed: {e}")

