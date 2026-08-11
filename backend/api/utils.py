import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not found in environment variables.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_table_as_df(table_name: str) -> pd.DataFrame:
    try:
        client = get_supabase_client()
        response = client.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        # Fallback to local CSV if supabase is not reachable or configured
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', f'{table_name}.csv')
        return pd.read_csv(csv_path)
