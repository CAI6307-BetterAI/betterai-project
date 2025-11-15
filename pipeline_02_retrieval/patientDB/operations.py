from .connection import get_connection


def add_patient(patient_id, name, age, sex, past_surgeries, avg_bp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (patient_id, name, age, sex, past_surgeries, avg_blood_pressure)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (patient_id) DO NOTHING
        RETURNING *;
    """, (patient_id, name, age, sex, past_surgeries, avg_bp))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result

def add_note(patient_id, note):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patient_notes (patient_id, note)
        VALUES (%s, %s)
        RETURNING *;
    """, (patient_id, note))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result

def get_patient_history(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, array_agg(n.note ORDER BY n.note_date) AS notes
        FROM patients p
        LEFT JOIN patient_notes n ON p.patient_id = n.patient_id
        WHERE p.patient_id = %s
        GROUP BY p.id;
    """, (patient_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def compare_notes(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT note, note_date
        FROM patient_notes
        WHERE patient_id = %s
        ORDER BY note_date ASC;
    """, (patient_id,))
    notes = cur.fetchall()
    cur.close()
    conn.close()

    if len(notes) < 2:
        return "Not enough notes to compare yet."

    old, new = notes[-2]["note"], notes[-1]["note"]
    return f"[PREVIOUS] Previous note:\n{old}\n\n[NEW] New note:\n{new}"
