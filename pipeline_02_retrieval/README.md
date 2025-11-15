# Pipeline 02 - Retrieval with Patient Context

This directory contains the retrieval pipeline for the BetterAI project, including **patient context integration** that enhances medical queries with patient-specific information.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Patient Management](#patient-management)
- [Usage](#usage)
- [Patient Database Schema](#patient-database-schema)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## 🔍 Overview

This pipeline retrieves medical information from an RDF knowledge graph and optionally enhances queries with **patient-specific context** stored in a PostgreSQL database. The system uses AI21's Jamba AI model to intelligently incorporate patient history, clinical notes, and medical background into queries.

### Key Components

```
pipeline_02_retrieval/
├── patient_context.py      # Patient context enhancement with Jamba AI
├── patientDB/              # PostgreSQL patient database management
│   ├── connection.py       # Database connection
│   ├── schema.py           # Table definitions
│   └── operations.py       # CRUD operations
├── pipeline.py             # Main retrieval pipeline
├── model_handler.py        # LLM model management
├── sources.py              # Source document handling
├── summarize.py            # Response summarization
└── tokens_to_query.py      # Query building from tokens
```

---

## ✨ Features

- **Patient Context Integration**: Automatically fetch and apply patient history to queries
- **AI-Enhanced Queries**: Uses Jamba AI to intelligently incorporate patient context
- **Dual Database System**: 
  - RDF Knowledge Graph for medical knowledge
  - PostgreSQL for patient records and clinical notes
- **Graceful Fallbacks**: Works with default values if patient database is unavailable
- **Interactive Patient Management**: CLI tool for managing patients and notes
- **Privacy-Focused**: Patient data kept separate from general knowledge base

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                   User Query + Patient ID                     │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              Pipeline 02 - Retrieval & Enhancement            │
│                                                               │
│  1. Tokenize Query                                            │
│  2. Fetch Patient Context ──► PostgreSQL Patient Database    │
│     │                           - Demographics                │
│     │                           - Past Surgeries              │
│     │                           - Clinical Notes              │
│     │                                                          │
│     ▼                                                          │
│  3. Enhance Query with Jamba AI (Optional)                   │
│     │                                                          │
│     ▼                                                          │
│  4. Execute Query ──► RDF Knowledge Graph                    │
│     │                 - Medical Facts                          │
│     │                 - Relationships                          │
│     │                                                          │
│     ▼                                                          │
│  5. Generate Summary with Patient Context                    │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ Contextualized   │
              │ Medical Response │
              └──────────────────┘
```

---

## 📦 Installation

### 1. Install Dependencies

Make sure you have Python 3.10+ installed, then:

```bash
# Using uv (recommended)
uv sync

# OR using pip
pip install -r requirements.txt
```

### Required Packages

The system requires:
- `psycopg2-binary` - PostgreSQL database adapter
- `ai21` - Jamba AI model integration
- `python-dotenv` - Environment variable management
- `torch`, `transformers` - For local LLM models
- Additional packages in `requirements.txt`

### 2. Setup PostgreSQL

Install PostgreSQL if you haven't already:

**Windows:**
```bash
# Download from: https://www.postgresql.org/download/windows/
# Or using Chocolatey:
choco install postgresql
```

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE betterai_patients;

# Create user (optional)
CREATE USER betterai_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE betterai_patients TO betterai_user;

# Exit
\q
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (use `env_template.txt` as reference):

```env
# PostgreSQL Database Configuration
DB_NAME=betterai_patients
DB_USER=betterai_user
DB_PASS=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# AI21 API Key (Optional - for AI-enhanced queries)
# Get your key from: https://studio.ai21.com/
AI21_API_KEY=your_ai21_api_key_here
```

**Note:** The AI21 API key is optional. Without it, patient context will still be displayed but queries won't be AI-enhanced.

**IMPORTANT:** Never commit your actual credentials to the README or any file in version control. Keep them only in your `.env` file!

---

## 🗄️ Database Setup

### Initialize Patient Database Schema

The patient database uses two tables: `patients` and `patient_notes`.

**Option 1: Using main_patients.py (Recommended)**

```bash
python main_patients.py
```

Then select:
- `1` - Setup/Initialize Database

**Option 2: Programmatically**

```python
from pipeline_02_retrieval.patientDB.schema import create_tables

create_tables()
print("✓ Database tables created!")
```

**Option 3: Manual SQL**

```sql
-- Create patients table
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

-- Create patient_notes table
CREATE TABLE IF NOT EXISTS patient_notes (
    id SERIAL PRIMARY KEY,
    patient_id TEXT REFERENCES patients(patient_id) ON DELETE CASCADE,
    note_date TIMESTAMP DEFAULT NOW(),
    note TEXT NOT NULL
);
```

---

## 👥 Patient Management

### Using the Interactive CLI

Run the patient management system:

```bash
python main_patients.py
```

### Menu Options

```
1. Setup/Initialize Database
   - Creates patients and patient_notes tables

2. Add Sample Patients
   - Adds 3 test patients (P001, P002, P003) with clinical notes

3. View Patient History
   - Display complete patient record including all notes

4. Add New Patient (Interactive)
   - Step-by-step patient creation

5. Add Note to Existing Patient
   - Add clinical notes to patient records

6. Exit
```

### Sample Patients

When you select option 2, these patients are created:

#### P001 - John Doe
- **Age:** 45, Male
- **Past Surgeries:** Appendectomy (2015), Hernia repair (2018)
- **Avg BP:** 120/80
- **Notes:** 
  - Patient presents with mild chest pain. ECG normal. Advised rest.
  - Follow-up visit: Chest pain resolved. Continue monitoring blood pressure.

#### P002 - Jane Smith
- **Age:** 62, Female
- **Past Surgeries:** Knee replacement (2020)
- **Avg BP:** 135/85
- **Notes:**
  - Patient reports joint pain in right knee. Post-surgery follow-up.
  - Physical therapy showing good progress. Pain levels decreasing.
  - Routine checkup: Blood pressure slightly elevated. Prescribed medication.

#### P003 - Robert Johnson
- **Age:** 38, Male
- **Past Surgeries:** None
- **Avg BP:** 118/75
- **Notes:**
  - Annual checkup: All vitals normal. No concerns.

### Programmatic Patient Management

```python
from pipeline_02_retrieval.patientDB.operations import (
    add_patient,
    add_note,
    get_patient_history
)

# Add a new patient
result = add_patient(
    patient_id="P004",
    name="Alice Williams",
    age=55,
    sex="F",
    past_surgeries=["Gallbladder removal (2019)"],
    avg_bp="125/82"
)

# Add clinical note
add_note("P004", "Patient presents with mild fatigue. Ordered blood work.")

# Retrieve patient history
patient = get_patient_history("P004")
print(f"Patient: {patient['name']}")
print(f"Age: {patient['age']}")
print(f"Notes: {patient['notes']}")
```

---

## 🚀 Usage

### Basic Pipeline Usage (No Patient Context)

```python
from database.database import Database
from pipeline_02_retrieval.pipeline import run_pipeline as run_pipeline_2

# Initialize RDF database
db = Database()

# Run query without patient context
result = run_pipeline_2(
    db=db,
    text="What is hypertension?"
)

print(result['summary'])
```

### Pipeline with Patient Context

```python
from database.database import Database
from pipeline_02_retrieval.pipeline import run_pipeline as run_pipeline_2

# Initialize RDF database
db = Database()

# Run query WITH patient context
result = run_pipeline_2(
    db=db,
    text="What are the treatment options for high blood pressure?",
    patient_id="P001"  # John Doe
)

print(result['summary'])
# Summary will be enhanced with John's medical history
```

### Using main.py Demo

```bash
python main.py
```

This will demonstrate:
1. Adding medical knowledge to RDF graph
2. Running a query without patient context
3. Running the same query with patient context (P001)
4. Showing the difference in results

### How Patient Context Enhancement Works

1. **Fetch Patient Data**: Retrieves patient record from PostgreSQL
   ```
   Patient ID: P001
   Name: John Doe
   Age: 45
   Sex: M
   Past Surgeries: Appendectomy (2015), Hernia repair (2018)
   Avg Blood Pressure: 120/80
   Clinical Notes: [2 notes about chest pain and BP monitoring]
   ```

2. **Build Context String**: Formats patient data into a structured prompt

3. **AI Enhancement** (if AI21_API_KEY is set):
   - Sends query + patient context to Jamba AI
   - AI intelligently incorporates relevant patient information
   - Returns enhanced query

4. **Execute Query**: Runs enhanced query against RDF knowledge graph

5. **Generate Response**: Returns results with patient-specific insights

### Direct Patient Context Function

```python
from database.database import Database
from pipeline_02_retrieval.patient_context import apply_patient_context

db = Database()
query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"

# Apply patient context to any query
enhanced_query = apply_patient_context(
    db=db,
    query=query,
    patient_id="P001"
)

print(f"Original: {query}")
print(f"Enhanced: {enhanced_query}")
```

---

## 🗃️ Patient Database Schema

### Table: `patients`

| Column              | Type        | Description                           |
|---------------------|-------------|---------------------------------------|
| id                  | SERIAL      | Primary key (auto-increment)          |
| patient_id          | TEXT        | Unique patient identifier (e.g. P001) |
| name                | TEXT        | Patient full name                     |
| age                 | INT         | Patient age in years                  |
| sex                 | TEXT        | Patient sex (M/F/Other)               |
| past_surgeries      | TEXT[]      | Array of past surgical procedures     |
| avg_blood_pressure  | TEXT        | Average BP reading (e.g. "120/80")    |
| created_at          | TIMESTAMP   | Record creation timestamp             |

**Constraints:**
- `patient_id` must be unique
- Foreign key referenced by `patient_notes`

### Table: `patient_notes`

| Column      | Type        | Description                        |
|-------------|-------------|------------------------------------|
| id          | SERIAL      | Primary key (auto-increment)       |
| patient_id  | TEXT        | Foreign key to patients table      |
| note_date   | TIMESTAMP   | Note creation timestamp            |
| note        | TEXT        | Clinical note content              |

**Constraints:**
- `patient_id` references `patients(patient_id)` with CASCADE delete
- Each note is timestamped automatically

---

## 📚 API Reference

### `patient_context.py`

#### `apply_patient_context(db, query, patient_id)`

Applies patient context to a query using Jamba AI.

**Parameters:**
- `db` (Database): RDF Database instance
- `query` (str | Query): Original query
- `patient_id` (str): Patient ID to fetch context for

**Returns:**
- Enhanced query (same type as input)

**Example:**
```python
enhanced = apply_patient_context(db, "What is diabetes?", "P001")
```

#### `enhance_query_with_jamba(query, context, api_key)`

Standalone function to enhance any query with custom context.

**Parameters:**
- `query` (str): Original query string
- `context` (str): Custom context information
- `api_key` (str, optional): AI21 API key

**Returns:**
- Enhanced query string

**Example:**
```python
context = "Patient has family history of diabetes"
enhanced = enhance_query_with_jamba("diabetes treatment", context)
```

### `patientDB/operations.py`

#### `add_patient(patient_id, name, age, sex, past_surgeries, avg_bp)`

Adds a new patient to the database.

**Parameters:**
- `patient_id` (str): Unique patient identifier
- `name` (str): Patient name
- `age` (int): Patient age
- `sex` (str): Patient sex
- `past_surgeries` (list): List of past surgeries
- `avg_bp` (str): Average blood pressure

**Returns:**
- Database record or None if patient exists

#### `add_note(patient_id, note)`

Adds a clinical note for a patient.

**Parameters:**
- `patient_id` (str): Patient ID
- `note` (str): Clinical note text

**Returns:**
- Database record of created note

#### `get_patient_history(patient_id)`

Retrieves complete patient record with all notes.

**Parameters:**
- `patient_id` (str): Patient ID

**Returns:**
- Dictionary with patient data and notes array

**Example:**
```python
patient = get_patient_history("P001")
print(f"Name: {patient['name']}")
print(f"Notes: {len(patient['notes'])} notes found")
```

### `patientDB/schema.py`

#### `create_tables()`

Creates the `patients` and `patient_notes` tables if they don't exist.

**Example:**
```python
from pipeline_02_retrieval.patientDB.schema import create_tables
create_tables()
```

---

## 🔧 Troubleshooting

### Database Connection Issues

**Problem:** `Could not fetch patient data: connection refused`

**Solutions:**
- ✅ Check if PostgreSQL is running: `sudo systemctl status postgresql`
- ✅ Verify `.env` file has correct credentials
- ✅ Ensure database exists: `psql -U postgres -c "\l"`
- ✅ Check firewall settings (port 5432)
- ✅ System will use default patient values if connection fails

### Missing Environment Variables

**Problem:** `KeyError: 'DB_NAME'` or similar

**Solutions:**
- ✅ Create `.env` file in project root
- ✅ Copy from `env_template.txt`
- ✅ Fill in your actual database credentials
- ✅ Restart your Python process

### AI21 API Key Issues

**Problem:** `AI21_API_KEY is not set`

**Solutions:**
- ⚠️ This is **optional** - system works without it
- ✅ Get API key from [AI21 Studio](https://studio.ai21.com/)
- ✅ Add to `.env`: `AI21_API_KEY=your_key_here`
- ℹ️ Without API key, patient context is displayed but not used for AI enhancement

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'psycopg2'` or `'ai21'`

**Solutions:**
```bash
# Reinstall dependencies
uv sync

# Or with pip
pip install -r requirements.txt

# Check installations
python -c "import psycopg2; import ai21; print('✓ All imports OK')"
```

### Patient Not Found

**Problem:** Query returns default patient values

**Solutions:**
- ✅ Check patient exists: Run `main_patients.py` → Option 3
- ✅ Verify patient_id spelling (case-sensitive)
- ✅ Add patient if needed: `main_patients.py` → Option 4
- ℹ️ Default values are used as graceful fallback

### Permission Errors

**Problem:** `permission denied for table patients`

**Solutions:**
```sql
-- Connect to database as superuser
psql -U postgres -d betterai_patients

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO betterai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO betterai_user;
```

---

## 🎯 Best Practices

### Patient ID Conventions

Use consistent patient ID formats:
- ✅ `P001`, `P002`, `P003` (Recommended)
- ✅ `PATIENT-001`, `PAT_123`
- ❌ Avoid special characters that might break queries

### Clinical Notes

Write clear, structured notes:
```python
# Good
add_note("P001", "Patient presents with headache. Duration: 3 days. Severity: 6/10. Prescribed ibuprofen.")

# Avoid
add_note("P001", "HA 3d 6/10 ibu")
```

### Security

- 🔒 Never commit `.env` file to version control
- 🔒 Use strong database passwords
- 🔒 Keep API keys secret
- 🔒 Consider encryption for patient data in production

---

## 📝 Examples

### Complete Workflow Example

```python
from database.database import Database
from pipeline_02_retrieval.patientDB.operations import add_patient, add_note
from pipeline_02_retrieval.pipeline import run_pipeline as run_pipeline_2

# 1. Add a new patient
add_patient(
    patient_id="P005",
    name="Maria Garcia",
    age=50,
    sex="F",
    past_surgeries=["Thyroidectomy (2020)"],
    avg_bp="130/85"
)

# 2. Add clinical notes
add_note("P005", "Initial consultation: Patient reports fatigue and weight gain.")
add_note("P005", "Lab results: TSH elevated. Diagnosed with hypothyroidism.")

# 3. Initialize database
db = Database()

# 4. Run patient-specific query
result = run_pipeline_2(
    db=db,
    text="What are the symptoms and treatment for thyroid disorders?",
    patient_id="P005"
)

# 5. Display results
print(f"Summary: {result['summary']}")
print(f"Sources: {result['sources']}")
```

---

## 🚀 What's Next?

After setting up patient context:

1. **Explore the Pipeline**: Try different medical queries with various patients
2. **Add Real Patients**: Use the interactive CLI to add your test patients
3. **Integrate with Frontend**: Build a UI that calls these functions
4. **Enhance Context**: Add more patient fields (medications, allergies, etc.)
5. **Implement Privacy Controls**: Add consent management for patient data usage

---

## 📞 Support

For issues or questions:
- Check the main [README.md](../README.md) in the project root
- Review [PATIENT_CONTEXT_README.md](../PATIENT_CONTEXT_README.md) for detailed architecture
- Open an issue on GitHub

---

## 📄 License

This project is part of the BetterAI system. See main repository for license information.

---

**Happy Coding! 🎉**

