import pandas as pd
import numpy as np
import math
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

def generate_table_sql(df, table_name):
    # Map pandas dtypes to postgres dtypes
    mapping = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'object': 'TEXT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP'
    }
    
    columns = []
    for col, dtype in zip(df.columns, df.dtypes):
        col_type = mapping.get(str(dtype), 'TEXT')
        # Special case for primary keys based on table name
        if table_name == 'employees' and col == 'employee_id':
            col_type += ' PRIMARY KEY'
        elif table_name == 'onboarding' and col == 'employee_id':
            col_type += ' PRIMARY KEY REFERENCES "employees"("employee_id")'
        elif table_name == 'support_tickets' and col == 'ticket_id':
            col_type += ' PRIMARY KEY'
        elif table_name == 'tool_usage' and col == 'usage_id':
            col_type += ' PRIMARY KEY'
            
        columns.append(f'"{col}" {col_type}')
    
    if table_name in ['support_tickets', 'tool_usage']:
        columns.append('FOREIGN KEY ("employee_id") REFERENCES "employees"("employee_id")')

    create_stmt = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(columns) + '\n);\n'
    return create_stmt

def generate_insert_sql(df, table_name):
    columns = '", "'.join(df.columns)
    columns = f'"{columns}"'
    
    values_list = []
    for _, row in df.iterrows():
        row_vals = []
        for val in row:
            if pd.isna(val) or val is None or val == '':
                row_vals.append('NULL')
            elif isinstance(val, (int, np.integer)):
                row_vals.append(str(val))
            elif isinstance(val, (float, np.floating)):
                if math.isnan(val):
                    row_vals.append('NULL')
                else:
                    row_vals.append(str(val))
            else:
                val_str = str(val).replace("'", "''")
                row_vals.append(f"'{val_str}'")
        values_list.append("(" + ", ".join(row_vals) + ")")
    
    inserts = []
    chunk_size = 1000
    for i in range(0, len(values_list), chunk_size):
        chunk = values_list[i:i+chunk_size]
        insert_stmt = f'INSERT INTO "{table_name}" ({columns}) VALUES\n' + ',\n'.join(chunk) + ';\n'
        inserts.append(insert_stmt)
    
    return inserts

def main():
    files = [
        'employees.csv',
        'onboarding.csv',
        'support_tickets.csv',
        'tool_usage.csv'
    ]

    for f in files:
        table_name = f.replace('.csv', '')
        csv_path = DATA_DIR / f
        if not csv_path.exists():
            print(f"Warning: {csv_path} does not exist. Skipping.")
            continue

        df = pd.read_csv(csv_path)
        create_sql = generate_table_sql(df, table_name)
        insert_sqls = generate_insert_sql(df, table_name)
        
        out_path = BASE_DIR / f'{table_name}.sql'
        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(create_sql + '\n')
            for ins in insert_sqls:
                out.write(ins + '\n')
        print(f"Generated {out_path.name} ({len(df)} records)")

    print("SQL files generation complete.")

if __name__ == '__main__':
    main()
