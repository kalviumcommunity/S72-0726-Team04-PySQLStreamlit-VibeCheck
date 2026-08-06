import urllib.request
import json
import pandas as pd
import math

url = "https://etxlyrvthapqkybcvobl.supabase.co"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV0eGx5cnZ0aGFwcWt5YmN2b2JsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYwMDk1OTgsImV4cCI6MjEwMTU4NTU5OH0.kBzlztrWDta2BsfxNjaSJHDvUvl3txvzXrVgQYG2WUo"

def upload_table(csv_file, table_name):
    print(f"Uploading {table_name}...")
    df = pd.read_csv(csv_file)
    # Convert all to object dtype first so None doesn't get coerced to NaN
    df = df.astype(object).where(pd.notnull(df), None)
    records = df.to_dict(orient='records')
    
    chunk_size = 1000
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        
        req = urllib.request.Request(f"{url}/rest/v1/{table_name}", method="POST")
        req.add_header("apikey", anon_key)
        req.add_header("Authorization", f"Bearer {anon_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")
        
        data = json.dumps(chunk).encode('utf-8')
        try:
            with urllib.request.urlopen(req, data=data) as response:
                if response.status not in (200, 201):
                    print(f"Error {response.status} for chunk {i}: {response.read()}")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code} for chunk {i}: {e.read().decode()}")

files = [
    ('d:/Coding/Projects/VibeCheck/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/onboarding.csv', 'onboarding'),
    ('d:/Coding/Projects/VibeCheck/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/support_tickets.csv', 'support_tickets')
]

for f, t in files:
    upload_table(f, t)
print("All done!")
