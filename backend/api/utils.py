import logging
import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Supabase (PostgREST) caps a single select at 1000 rows by default, so larger
# tables such as tool_usage (~7,800 rows) must be read page by page.
PAGE_SIZE = 1000


def supabase_configured() -> bool:
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"))


def get_supabase_client():
    if not supabase_configured():
        raise ValueError("Supabase credentials not found in environment variables.")
    # Imported lazily: supabase is optional, and a missing package must not take the API down.
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])


def _fetch_all_rows(table_name: str) -> list:
    table = get_supabase_client().table(table_name)
    rows, start = [], 0
    while True:
        page = table.select("*").range(start, start + PAGE_SIZE - 1).execute().data or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        start += PAGE_SIZE


def _read_local_csv(table_name: str) -> pd.DataFrame:
    csv_path = os.path.join(DATA_DIR, f'{table_name}.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No data for '{table_name}': Supabase is unavailable and {csv_path} is missing. "
            f"Restore it with `git checkout -- data/{table_name}.csv`."
        )
    return pd.read_csv(csv_path)


def fetch_table_as_df(table_name: str) -> pd.DataFrame:
    """Read a table from Supabase when configured, otherwise from data/<table>.csv."""
    if not supabase_configured():
        return _read_local_csv(table_name)
    try:
        rows = _fetch_all_rows(table_name)
        if not rows:
            raise ValueError(f"Supabase returned no rows for '{table_name}'")
        return pd.DataFrame(rows)
    except Exception:
        # Network, auth, missing table or missing package: fall back to the CSVs, but loudly,
        # so a misconfigured deployment does not look like a working one.
        logger.warning("Supabase fetch for %r failed; using the local CSV fallback", table_name, exc_info=True)
        return _read_local_csv(table_name)
