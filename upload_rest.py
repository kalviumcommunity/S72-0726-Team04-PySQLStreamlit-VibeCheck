import urllib.request
import urllib.error
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

url = "https://etxlyrvthapqkybcvobl.supabase.co"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV0eGx5cnZ0aGFwcWt5YmN2b2JsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYwMDk1OTgsImV4cCI6MjEwMTU4NTU5OH0.kBzlztrWDta2BsfxNjaSJHDvUvl3txvzXrVgQYG2WUo"

def upload_table(csv_file, table_name):
    print(f"Uploading {table_name} from {csv_file.name}...")
    if not csv_file.exists():
        print(f"File {csv_file} does not exist. Skipping.")
        return

    df = pd.read_csv(csv_file)
    # Convert all to object dtype first so None doesn't get coerced to NaN
    df = df.astype(object).where(pd.notnull(df), None)
    records = df.to_dict(orient='records')
    
    chunk_size = 1000
    uploaded_chunks = 0
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        
        req = urllib.request.Request(f"{url}/rest/v1/{table_name}", method="POST")
        req.add_header("apikey", anon_key)
        req.add_header("Authorization", f"Bearer {anon_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "resolution=merge-duplicates")
        
        data = json.dumps(chunk).encode('utf-8')
        try:
            with urllib.request.urlopen(req, data=data) as response:
                if response.status in (200, 201, 204):
                    uploaded_chunks += 1
                else:
                    print(f"Response {response.status} for chunk {i}: {response.read()}")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code} for chunk {i}: {e.read().decode()}")
        except Exception as e:
            print(f"Failed to upload chunk {i}: {e}")
            break

    print(f"Finished {table_name}: {uploaded_chunks} chunks successfully processed.")

def main():
    tables = [
        ('employees.csv', 'employees'),
        ('onboarding.csv', 'onboarding'),
        ('support_tickets.csv', 'support_tickets'),
        ('tool_usage.csv', 'tool_usage'),
    ]

    for fname, tname in tables:
        upload_table(DATA_DIR / fname, tname)

    print("Supabase upload workflow complete!")

if __name__ == '__main__':
    main()
