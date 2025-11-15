"""
Patient Management Main File

This file provides functionality to:
- Add new patients to the database
- Add clinical notes for patients
- View patient history
- Test the patient context integration
"""

from pipeline_02_retrieval.patientDB.operations import (
    add_note,
    add_patient,
    compare_notes,
    get_patient_history,
)
from pipeline_02_retrieval.patientDB.schema import create_tables


def setup_database():
    """Initialize the patient database tables."""
    print("Setting up patient database tables...")
    try:
        create_tables()
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")


def add_sample_patients():
    """Add some sample patients for testing."""
    print("\nAdding sample patients...")
    
    # Patient 1: John Doe
    try:
        result = add_patient(
            patient_id="P001",
            name="John Doe",
            age=45,
            sex="M",
            past_surgeries=["Appendectomy (2015)", "Hernia repair (2018)"],
            avg_bp="120/80"
        )
        if result:
            print(f"✓ Added patient: {result['name']} (ID: {result['patient_id']})")
            
            # Add notes for John
            add_note("P001", "Patient presents with mild chest pain. ECG normal. Advised rest.")
            add_note("P001", "Follow-up visit: Chest pain resolved. Continue monitoring blood pressure.")
            print(f"  Added 2 clinical notes for {result['name']}")
        else:
            print("✓ Patient P001 already exists")
    except Exception as e:
        print(f"✗ Error adding patient P001: {e}")
    
    # Patient 2: Jane Smith
    try:
        result = add_patient(
            patient_id="P002",
            name="Jane Smith",
            age=62,
            sex="F",
            past_surgeries=["Knee replacement (2020)"],
            avg_bp="135/85"
        )
        if result:
            print(f"✓ Added patient: {result['name']} (ID: {result['patient_id']})")
            
            # Add notes for Jane
            add_note("P002", "Patient reports joint pain in right knee. Post-surgery follow-up.")
            add_note("P002", "Physical therapy showing good progress. Pain levels decreasing.")
            add_note("P002", "Routine checkup: Blood pressure slightly elevated. Prescribed medication.")
            print(f"  Added 3 clinical notes for {result['name']}")
        else:
            print("✓ Patient P002 already exists")
    except Exception as e:
        print(f"✗ Error adding patient P002: {e}")
    
    # Patient 3: Robert Johnson
    try:
        result = add_patient(
            patient_id="P003",
            name="Robert Johnson",
            age=38,
            sex="M",
            past_surgeries=[],
            avg_bp="118/75"
        )
        if result:
            print(f"✓ Added patient: {result['name']} (ID: {result['patient_id']})")
            
            # Add notes for Robert
            add_note("P003", "Annual checkup: All vitals normal. No concerns.")
            print(f"  Added 1 clinical note for {result['name']}")
        else:
            print("✓ Patient P003 already exists")
    except Exception as e:
        print(f"✗ Error adding patient P003: {e}")


def view_patient(patient_id: str):
    """View a patient's complete history."""
    print(f"\n{'='*60}")
    print(f"PATIENT HISTORY: {patient_id}")
    print(f"{'='*60}")
    
    try:
        patient = get_patient_history(patient_id)
        
        if not patient:
            print(f"✗ Patient {patient_id} not found")
            return
        
        print(f"\nBasic Information:")
        print(f"  Name: {patient.get('name', 'N/A')}")
        print(f"  Age: {patient.get('age', 'N/A')}")
        print(f"  Sex: {patient.get('sex', 'N/A')}")
        print(f"  Past Surgeries: {patient.get('past_surgeries', [])}")
        print(f"  Avg Blood Pressure: {patient.get('avg_blood_pressure', 'N/A')}")
        
        if patient.get('notes'):
            print(f"\nClinical Notes:")
            notes = patient['notes']
            if isinstance(notes, list):
                for i, note in enumerate(notes, 1):
                    if note:
                        print(f"  [{i}] {note}")
            else:
                print(f"  {notes}")
        else:
            print(f"\nNo clinical notes available.")
            
    except Exception as e:
        print(f"✗ Error retrieving patient: {e}")


def add_new_patient_interactive():
    """Interactive prompt to add a new patient."""
    print(f"\n{'='*60}")
    print("ADD NEW PATIENT")
    print(f"{'='*60}")
    
    patient_id = input("Patient ID (e.g., P004): ").strip()
    name = input("Name: ").strip()
    age = input("Age: ").strip()
    sex = input("Sex (M/F/Other): ").strip()
    surgeries_input = input("Past surgeries (comma-separated, or 'none'): ").strip()
    
    if surgeries_input.lower() == 'none':
        past_surgeries = []
    else:
        past_surgeries = [s.strip() for s in surgeries_input.split(',')]
    
    avg_bp = input("Average blood pressure (e.g., 120/80): ").strip()
    
    try:
        result = add_patient(
            patient_id=patient_id,
            name=name,
            age=int(age) if age else None,
            sex=sex,
            past_surgeries=past_surgeries,
            avg_bp=avg_bp
        )
        
        if result:
            print(f"\n✓ Patient added successfully: {result['name']} (ID: {result['patient_id']})")
            
            # Optional: Add a note
            add_note_choice = input("\nAdd a clinical note? (y/n): ").strip().lower()
            if add_note_choice == 'y':
                note = input("Enter note: ").strip()
                add_note(patient_id, note)
                print("✓ Note added successfully")
        else:
            print(f"\n✗ Patient {patient_id} already exists")
            
    except Exception as e:
        print(f"\n✗ Error adding patient: {e}")


def main_menu():
    """Display main menu and handle user choices."""
    while True:
        print(f"\n{'='*60}")
        print("PATIENT MANAGEMENT SYSTEM")
        print(f"{'='*60}")
        print("1. Setup/Initialize Database")
        print("2. Add Sample Patients")
        print("3. View Patient History")
        print("4. Add New Patient (Interactive)")
        print("5. Add Note to Existing Patient")
        print("6. Exit")
        print(f"{'='*60}")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            setup_database()
        
        elif choice == '2':
            add_sample_patients()
        
        elif choice == '3':
            patient_id = input("Enter patient ID (e.g., P001): ").strip()
            view_patient(patient_id)
        
        elif choice == '4':
            add_new_patient_interactive()
        
        elif choice == '5':
            patient_id = input("Enter patient ID: ").strip()
            note = input("Enter clinical note: ").strip()
            try:
                result = add_note(patient_id, note)
                if result:
                    print(f"✓ Note added successfully for patient {patient_id}")
                else:
                    print(f"✗ Failed to add note")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == '6':
            print("\nExiting patient management system. Goodbye!")
            break
        
        else:
            print("\n✗ Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BETTERAI PATIENT MANAGEMENT SYSTEM")
    print("="*60)
    print("\nNote: Make sure your .env file is configured with database credentials:")
    print("  - DB_NAME")
    print("  - DB_USER")
    print("  - DB_PASS")
    print("  - DB_HOST")
    print("  - DB_PORT")
    print("\nIf patient database is not available, the system will use default values.")
    
    main_menu()

