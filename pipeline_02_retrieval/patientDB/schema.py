from .connection import get_connection


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT,
            age INT,
            sex TEXT,
            past_surgeries TEXT[],
            avg_blood_pressure TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_notes (
            id SERIAL PRIMARY KEY,
            patient_id TEXT REFERENCES patients(patient_id) ON DELETE CASCADE,
            note_date TIMESTAMP DEFAULT NOW(),
            note TEXT NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print(" Tables created successfully.")
