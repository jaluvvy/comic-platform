#!/usr/bin/env python3
"""
Import data from JSON files into Supabase database.
Usage: python import_supabase.py --url <target_db_url> --input <input_dir> [--clear] [--force]
"""
import sys
import json
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("Error: psycopg2 is required. Install it with: pip install psycopg2-binary")
    sys.exit(1)


def get_connection(db_url: str):
    """Create database connection."""
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def clear_table(conn, table_name: str):
    """Clear all data from a table."""
    print(f"Clearing {table_name}...")
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM {table_name} CASCADE")
        print(f"  [OK] Cleared {table_name}")
    except Exception as e:
        print(f"  [ERR] Error clearing {table_name}: {e}")
    finally:
        cur.close()


def import_table(conn, table_name: str, input_file: Path, clear: bool = False, force: bool = False) -> dict:
    """Import data from JSON file into table."""
    print(f"Importing {table_name}...")
    
    if not input_file.exists():
        print(f"  [ERR] File not found: {input_file}")
        return {"table": table_name, "count": 0, "error": "File not found"}
    
    cur = conn.cursor()
    
    try:
        # Read data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print(f"  - No data to import")
            return {"table": table_name, "count": 0}
        
        # Clear table if requested
        if clear:
            clear_table(conn, table_name)
        
        # Get existing columns in target table
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position")
        valid_columns = {row[0] for row in cur.fetchall()}
        
        # Filter columns that exist in target table
        first_row = data[0]
        columns = [col for col in first_row.keys() if col in valid_columns]
        
        if not columns:
            print(f"  [ERR] No valid columns found for {table_name}")
            return {"table": table_name, "count": 0, "error": "No valid columns"}
        
        column_names = ', '.join(columns)
        
        # Batch insert using execute_values
        batch_size = 500
        imported = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = [[row.get(col) for col in columns] for row in batch]
            
            try:
                execute_values(
                    cur,
                    f"INSERT INTO {table_name} ({column_names}) VALUES %s",
                    values,
                    page_size=batch_size
                )
                imported += len(batch)
            except Exception as e:
                print(f"  [ERR] Error inserting batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"  [OK] Imported {imported} rows (columns: {', '.join(columns)})")
        return {"table": table_name, "count": imported}
        
    except Exception as e:
        print(f"  [ERR] Error importing {table_name}: {e}")
        return {"table": table_name, "count": 0, "error": str(e)}