#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("Starting import script...", flush=True)

try:
    import psycopg2
    from psycopg2.extras import execute_values
    print("psycopg2 imported", flush=True)
except ImportError as e:
    print(f"Error importing psycopg2: {e}", flush=True)
    sys.exit(1)

def get_connection(db_url: str):
    print(f"Connecting to: {db_url[:50]}...", flush=True)
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        print("Connected", flush=True)
        return conn
    except Exception as e:
        print(f"Connection error: {e}", flush=True)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--clear", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    
    print(f"Args: url={args.url[:50]}..., input={args.input}", flush=True)
    
    conn = get_connection(args.url)
    input_dir = Path(args.input)
    
    tables = ['publishers', 'comics', 'gifts', 'events', 'event_gifts', 'users']
    
    for table in tables:
        print(f"\n--- Processing {table} ---", flush=True)
        input_file = input_dir / f"{table}.json"
        
        if not input_file.exists():
            print(f"  File not found: {input_file}", flush=True)
            continue
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  Loaded {len(data)} rows", flush=True)
        
        if not data:
            continue
        
        cur = conn.cursor()
        
        if args.clear:
            cur.execute(f"DELETE FROM {table} CASCADE")
            print(f"  Cleared {table}", flush=True)
        
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
        valid_columns = {row[0] for row in cur.fetchall()}
        print(f"  Valid columns: {sorted(valid_columns)}", flush=True)
        
        first_row = data[0]
        columns = [col for col in first_row.keys() if col in valid_columns]
        print(f"  Filtered columns: {columns}", flush=True)
        
        if not columns:
            print(f"  No valid columns, skipping", flush=True)
            cur.close()
            continue
        
        column_names = ', '.join(columns)
        batch_size = 500
        imported = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = [[row.get(col) for col in columns] for row in batch]
            
            try:
                execute_values(
                    cur,
                    f"INSERT INTO {table} ({column_names}) VALUES %s",
                    values,
                    page_size=batch_size
                )
                imported += len(batch)
            except Exception as e:
                print(f"  Error batch {i//batch_size}: {e}", flush=True)
        
        print(f"  Imported {imported} rows", flush=True)
        cur.close()
    
    conn.close()
    print("\nImport complete!", flush=True)

if __name__ == "__main__":
    main()
