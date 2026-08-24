#!/usr/bin/env python3
"""
Export data from Supabase database to JSON files.
Usage: python export_supabase.py --url <source_db_url> --output <output_dir>
"""
import sys
import json
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
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


def export_table(conn, table_name: str, output_dir: Path) -> dict:
    """Export a table to JSON file."""
    print(f"Exporting {table_name}...")
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get column names
        cur.execute(f"SELECT * FROM {table_name} LIMIT 0")
        columns = [desc[0] for desc in cur.description]
        
        # Get all data
        cur.execute(f"SELECT * FROM {table_name} ORDER BY id")
        rows = cur.fetchall()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        
        # Write to file
        output_file = output_dir / f"{table_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"  [OK] Exported {len(data)} rows to {output_file}")
        return {"table": table_name, "count": len(data), "file": str(output_file)}
        
    except Exception as e:
        print(f"  [ERR] Error exporting {table_name}: {e}")
        return {"table": table_name, "count": 0, "error": str(e)}
    finally:
        cur.close()


def export_all(conn, output_dir: Path) -> dict:
    """Export all tables."""
    tables = [
        'publishers',
        'comics',
        'gifts',
        'events',
        'event_gifts',
        'users',  # public.users
    ]
    
    results = []
    for table in tables:
        result = export_table(conn, table, output_dir)
        results.append(result)
    
    return {
        "exported_at": str(Path.cwd()),
        "tables": results
    }


def main():
    parser = argparse.ArgumentParser(description="Export Supabase database to JSON")
    parser.add_argument("--url", required=True, help="Database connection URL")
    parser.add_argument("--output", default="supabase_export", help="Output directory")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Connecting to database...")
    conn = get_connection(args.url)
    
    try:
        print("Starting export...")
        summary = export_all(conn, output_dir)
        
        # Write summary
        summary_file = output_dir / "export_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] Export complete!")
        print(f"  Output: {output_dir}")
        print(f"  Summary: {summary_file}")
        
        # Print totals
        total_rows = sum(t.get("count", 0) for t in summary["tables"])
        print(f"  Total rows exported: {total_rows}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
