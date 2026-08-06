import pandas as pd
import math

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
        # special case for primary keys based on table name
        if table_name == 'employees' and col == 'employee_id':
            col_type += ' PRIMARY KEY'
        elif table_name == 'onboarding' and col == 'employee_id':
            col_type += ' PRIMARY KEY' # assuming 1:1
        elif table_name == 'support_tickets' and col == 'ticket_id':
            col_type += ' PRIMARY KEY'
        elif table_name == 'tool_usage' and col == 'usage_id':
            col_type += ' PRIMARY KEY'
            
        columns.append(f'"{col}" {col_type}')
    
    create_stmt = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(columns) + '\n);\n'
    return create_stmt

def generate_insert_sql(df, table_name):
    columns = '", "'.join(df.columns)
    columns = f'"{columns}"'
    
    # Handle NaN/NaT
    df = df.fillna('NULL_MARKER')
    
    values_list = []
    for _, row in df.iterrows():
        row_vals = []
        for val in row:
            if val == 'NULL_MARKER':
                row_vals.append('NULL')
            elif isinstance(val, (int, float)):
                row_vals.append(str(val))
            else:
                # Escape quotes
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

files = [
    'employees.csv',
    'onboarding.csv',
    'support_tickets.csv',
    'tool_usage.csv'
]

for f in files:
    table_name = f.replace('.csv', '')
    df = pd.read_csv(f'd:/Coding/Projects/VibeCheck/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/{f}')
    
    create_sql = generate_table_sql(df, table_name)
    insert_sqls = generate_insert_sql(df, table_name)
    
    with open(f'd:/Coding/Projects/VibeCheck/S72-0726-Team04-PySQLStreamlit-VibeCheck/{table_name}.sql', 'w', encoding='utf-8') as out:
        out.write(create_sql + '\n')
        for ins in insert_sqls:
            out.write(ins + '\n')

print("SQL files generated.")
