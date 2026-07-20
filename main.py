import csv
import json
import logging
import re
from datetime import datetime

# 1. Logging Setup (To track validation failures automatically)
logging.basicConfig(
    filename='validation_errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

# 2. Data Validator Class (Object-Oriented Approach)
class MedicalDataValidator:
    def __init__(self):
        self.required_keys = {
            'patient_id', 'age', 'gender', 'diagnosis', 'medications', 'last_visit_id'
        }

    def validate_record(self, record):
        """Validates the business logic and structure of a single patient record."""
        if not isinstance(record, dict):
            return ["Not a valid dictionary object"]

        # Check for missing or extra keys
        if set(record.keys()) != self.required_keys:
            missing = self.required_keys - set(record.keys())
            extra = set(record.keys()) - self.required_keys
            return [f"Missing keys: {missing}, Extra keys: {extra}"]

        errors = []

        # Patient ID Check (Format: Letter 'P' followed by numbers, e.g., P1001)
        if not (isinstance(record['patient_id'], str) and re.fullmatch(r'p\d+', record['patient_id'], re.IGNORECASE)):
            errors.append(f"Invalid patient_id: '{record['patient_id']}'")

        # Age Check (Adult patients only, realistic range)
        if not (isinstance(record['age'], int) and 18 <= record['age'] <= 120):
            errors.append(f"Invalid age: {record['age']}")

        # Gender Check
        if not (isinstance(record['gender'], str) and record['gender'].lower() in ('male', 'female', 'other')):
            errors.append(f"Invalid gender: '{record['gender']}'")

        # Medications Check (Must be a list containing only strings)
        if not (isinstance(record['medications'], list) and all(isinstance(m, str) for m in record['medications'])):
            errors.append("Invalid medications format (Expected a list of strings)")

        # Last Visit ID Check (Format: Letter 'V' followed by numbers, e.g., V2301)
        if not (isinstance(record['last_visit_id'], str) and re.fullmatch(r'v\d+', record['last_visit_id'], re.IGNORECASE)):
            errors.append(f"Invalid last_visit_id: '{record['last_visit_id']}'")

        return errors

# 3. Data Pipeline Processor
def run_data_pipeline(raw_data):
    validator = MedicalDataValidator()
    clean_records = []

    print("🚀 Starting Medical Data Validation Pipeline...\n")

    for index, record in enumerate(raw_data):
        errors = validator.validate_record(record)

        if errors:
            # Catch bad data, log it, and print to console
            p_id = record.get('patient_id', f'UNKNOWN_INDEX_{index}')
            error_msg = f"Patient {p_id} at index {index} failed validation. Reasons: {errors}"
            print(f"❌ {error_msg}")
            logging.warning(error_msg)
        else:
            # Standardize clean data (Capitalize IDs, flatten list into a comma-separated string)
            standardized_record = {
                'patient_id': record['patient_id'].upper(),
                'age': record['age'],
                'gender': record['gender'].capitalize(),
                'diagnosis': record['diagnosis'],
                'medications': ', '.join(record['medications']),
                'last_visit_id': record['last_visit_id'].upper()
            }
            clean_records.append(standardized_record)

    # 4. Save clean data to a CSV File
    if clean_records:
        keys = clean_records[0].keys()
        with open('clean_patients.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(clean_records)

    print(f"\n✅ Pipeline Completed. Clean records saved: {len(clean_records)}. Check validation_errors.log for failures.")

# 5. Mock Dataset (A mix of clean and corrupted data)
if __name__ == '__main__':
    raw_hospital_data = [
        {
            'patient_id': 'P1001',
            'age': 34,
            'gender': 'Female',
            'diagnosis': 'Hypertension',
            'medications': ['Lisinopril'],
            'last_visit_id': 'V2301',
        },
        {
            'patient_id': '1002',
            'age': 15,
            'gender': 'male',
            'diagnosis': 'Diabetes',
            'medications': 'Metformin',
            'last_visit_id': 'v2302',
        },  # Bad ID format, age under 18, medications not a list
        {
            'patient_id': 'P1003',
            'age': 29,
            'gender': 'female',
            'diagnosis': 'Asthma',
            'medications': ['Albuterol'],
            'last_visit_id': 'v2303',
        },
        {
            'patient_id': 'p1004',
            'age': -5,
            'gender': 'Alien',
            'diagnosis': 'Back Pain',
            'medications': [],
            'last_visit_id': 'V2304',
        }   # Negative age, invalid gender string
    ]

    run_data_pipeline(raw_hospital_data)
