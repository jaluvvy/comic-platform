import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import psycopg2
from psycopg2.extras import execute_values

url = 'postgresql://postgres:%40ThanhVy2323%40@db.kfseqrvwvkjbdyywlobp.supabase.co:5432/postgres'
conn = psycopg2.connect(url)
conn.autocommit = True
cur = conn.cursor()

table = 'publishers'
input_file = Path('G:/My Drive/Work/comic-crawler/web/supabase_export/publishers.json')

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

cur.execute(f'DELETE FROM {table} CASCADE')

cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
valid_columns = {row[0] for row in cur.fetchall()}
print('Valid columns:', valid_columns)

first_row = data[0]
print('JSON columns:', list(first_row.keys()))

columns = [col for col in first_row.keys() if col in valid_columns]
print('Filtered columns:', columns)

column_names = ', '.join(columns)
values = [[row.get(col) for col in columns] for row in data]

execute_values(cur, f'INSERT INTO {table} ({column_names}) VALUES %s', values)
print(f'Inserted {len(values)} rows')

cur.close()
conn.close()
