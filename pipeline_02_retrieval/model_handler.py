# jamba/model_handler.py
import os
from pathlib import Path

from ai21 import AI21Client
from ai21.models.chat import ChatMessage
from dotenv import load_dotenv

# Load .env file from the jamba directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class JambaHandler:
    def __init__(self, model_name="jamba-large"):
        print(f"[*] Loading JAMBA model: {model_name} ...")
        api_key = os.getenv("AI21_API_KEY")
        if not api_key:
            raise ValueError("AI21_API_KEY environment variable not set. Check your .env file.")
        self.client = AI21Client(api_key=api_key)
        self.model_name = model_name
        print("[+] Model ready.")

    def analyze_patient(self, patient_info):
        """
        Takes structured patient_info from DB and generates a recovery summary.
        """
        context = (
            f"Patient: {patient_info['name']} | "
            f"Age: {patient_info['age']} | Sex: {patient_info['sex']} | "
            f"BP: {patient_info['avg_blood_pressure']} | "
            f"Past Surgeries: {', '.join(patient_info['past_surgeries'] or [])} | "
            f"Notes Timeline: {patient_info['notes']}"
        )

        prompt = f"""You are a medical summarizer.
        Analyze the progression of this patient based on their latest notes.
        Focus on recovery trends, stability, and any risk patterns.

        {context}
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[ChatMessage(role="user", content=prompt)],
            max_tokens=500, #this can be lowered to a shorter response if needed
            temperature=0.7
        )
        
        return response.choices[0].message.content
