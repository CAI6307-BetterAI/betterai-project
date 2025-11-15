# Patient Context Integration

This document explains how the patient context feature works in the BetterAI project.

## Overview

The system integrates **two separate databases**:

1. **RDF Knowledge Graph** (`database/database.py`) - Stores general medical knowledge as subject-predicate-object triples
2. **PostgreSQL Patient Database** (`pipeline_02_retrieval/patientDB/`) - Stores specific patient records and clinical notes

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline 2 - Retrieval                   │
│                                                             │
│  Query Text ──► Tokenize ──► Build Query ──► (Optional)    │
│                                              Patient Context │
│                                                    │         │
│                                                    ▼         │
│                                          ┌─────────────────┐│
│                                          │ PostgreSQL DB   ││
│                                          │ - Patient Info  ││
│                                          │ - Notes         ││
│                                          └─────────────────┘│
│                                                    │         │
│                                                    ▼         │
│                              Enhanced Query with Patient     │
│                                        Context               │
│                                                    │         │
│                                                    ▼         │
│                              ┌─────────────────────────────┐│
│                              │    RDF Knowledge Graph      ││
│                              │  - Medical Facts            ││
│                              │  - Relationships            ││
│                              └─────────────────────────────┘│
│                                          │                   │
│                                          ▼                   │
│                                    Query Results            │
│                                          │                   │
│                                          ▼                   │
│                            Summary + Sources                │
└─────────────────────────────────────────────────────────────┘
```

## Files Modified/Created

### Modified Files

1. **`pipeline_02_retrieval/patient_context.py`**
   - Now fetches patient data from PostgreSQL database
   - Uses default patient values if database is unavailable
   - Optionally enhances queries with AI21's Jamba AI model

2. **`main.py`**
   - Updated to demonstrate both standard and patient-context queries
   - Shows before/after comparison

3. **`pyproject.toml`**
   - Added dependencies: `ai21`, `psycopg2-binary`, `python-dotenv`

### New Files

1. **`main_patients.py`**
   - Interactive patient management system
   - Add/view patients and clinical notes
   - Setup database tables

2. **`env_template.txt`**
   - Template for environment variables
   - Database credentials and API keys

## Patient Database Schema

### Table: `patients`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| patient_id | TEXT | Unique patient identifier (e.g., "P001") |
| name | TEXT | Patient name |
| age | INT | Patient age |
| sex | TEXT | Patient sex (M/F/Other) |
| past_surgeries | TEXT[] | Array of past surgeries |
| avg_blood_pressure | TEXT | Average BP (e.g., "120/80") |
| created_at | TIMESTAMP | Record creation time |

### Table: `patient_notes`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| patient_id | TEXT | Foreign key to patients |
| note_date | TIMESTAMP | Note creation time |
| note | TEXT | Clinical note content |

## Setup Instructions

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment Variables

Create a `.env` file (use `env_template.txt` as reference):

```env
# PostgreSQL Database (Required for patient context)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASS=your_database_password
DB_HOST=localhost
DB_PORT=5432

# AI21 API Key (Optional - for AI-enhanced queries)
AI21_API_KEY=your_ai21_api_key_here
```

### 3. Setup Patient Database

```bash
uv run python main_patients.py
```

Choose option 1 to initialize tables, then option 2 to add sample patients.

## Usage

### Running the Main Demo

```bash
uv run python main.py
```

This will:
1. Add medical knowledge to RDF graph
2. Query without patient context
3. Query with patient context (using patient P001)

### Managing Patients

```bash
uv run python main_patients.py
```

Menu options:
- **1**: Setup/Initialize Database
- **2**: Add Sample Patients (P001, P002, P003)
- **3**: View Patient History
- **4**: Add New Patient (Interactive)
- **5**: Add Note to Existing Patient
- **6**: Exit

### Programmatic Usage

```python
from database.database import Database
from pipeline_02_retrieval.pipeline import run_pipeline as run_pipeline_2

# Initialize databases
db = Database()

# Query WITHOUT patient context
result = run_pipeline_2(db=db, text="What is hypertension?")

# Query WITH patient context
result_with_context = run_pipeline_2(
    db=db, 
    text="What is hypertension?",
    patient_id="P001"
)
```

## How Patient Context Works

### 1. Query Without Patient Context

```python
run_pipeline_2(db=db, text="What is hypertension?")
```

- Queries only the RDF knowledge graph
- Returns general medical information

### 2. Query With Patient Context

```python
run_pipeline_2(db=db, text="What is hypertension?", patient_id="P001")
```

**Step 1**: Fetch patient data from PostgreSQL
```
Patient ID: P001
Name: John Doe
Age: 45
Sex: M
Past Surgeries: Appendectomy (2015), Hernia repair (2018)
Avg Blood Pressure: 120/80
Clinical Notes:
  [1] Patient presents with mild chest pain. ECG normal.
  [2] Follow-up: Chest pain resolved. Continue monitoring BP.
```

**Step 2**: Enhance query with patient context (if AI21 API key available)
- Sends patient context + query to Jamba AI model
- AI enhances query to be patient-specific

**Step 3**: Execute enhanced query against RDF knowledge graph

**Step 4**: Return results with patient-specific insights

## Default Patient Values

If a patient is not found OR the patient database is unavailable, the system uses these defaults:

```python
{
    "patient_id": "P001",  # or whatever ID was requested
    "name": "Unknown Patient",
    "age": 45,
    "sex": "Unknown",
    "past_surgeries": ["None recorded"],
    "avg_blood_pressure": "120/80",
    "notes": ["No medical history available for this patient."]
}
```

This ensures the pipeline **always works** even without patient database setup.

## AI Enhancement (Optional)

If `AI21_API_KEY` is set, the system uses AI21's Jamba model to enhance queries with patient context.

**Without AI21**: Patient context is printed but query runs unchanged
**With AI21**: Query is intelligently enhanced with relevant patient information

## Sample Patients

When you add sample patients, you get:

### P001 - John Doe
- Age: 45, Male
- Past Surgeries: Appendectomy (2015), Hernia repair (2018)
- Avg BP: 120/80
- 2 clinical notes about chest pain

### P002 - Jane Smith
- Age: 62, Female
- Past Surgeries: Knee replacement (2020)
- Avg BP: 135/85
- 3 clinical notes about joint pain and BP

### P003 - Robert Johnson
- Age: 38, Male
- No past surgeries
- Avg BP: 118/75
- 1 clinical note from annual checkup

## Troubleshooting

### PostgreSQL Connection Issues

**Error**: `Could not fetch patient data: ...`

**Solution**: 
- Check `.env` file has correct database credentials
- Ensure PostgreSQL is running
- Verify database exists and user has permissions
- System will use default patient values if connection fails

### Missing AI21 API Key

**Error**: `AI21_API_KEY is not set`

**Solution**:
- This is optional - system works without it
- Patient context will be displayed but not used for query enhancement
- Get API key from https://studio.ai21.com/ if you want AI enhancement

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'ai21'` or `'psycopg2'`

**Solution**:
```bash
uv sync
```

## Future Enhancements

Potential improvements:
- [ ] Add more sophisticated patient context filtering
- [ ] Implement patient consent/privacy controls
- [ ] Add patient medical history timeline
- [ ] Support for multi-patient queries
- [ ] Cache patient data for faster queries
- [ ] Add patient data validation

## Notes

- Patient database connection is attempted but failures are handled gracefully
- System always provides default values as fallback
- RDF database and Patient database are completely independent
- Patient context is optional - core functionality works without it

---

For questions or issues, check the main README.md or open an issue.

