import sqlite3
import argparse
from pathlib import Path


def display_db_schema_and_content(db_path):

  if not (Path(db_path)).exists():
    print(f"Database file not found: {db_path}")
    return

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # Get a list of all user-created tables
  cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
  )
  tables = cursor.fetchall()

  if not tables:
    print("No tables found in the database.")
    conn.close()
    return

  for table in tables:
    table_name = table[0]
    print(f"\n{'=' * 60}")
    print(f" TABLE: {table_name}")
    print(f"{'=' * 60}")

    # 1. Fetch and print table schema
    cursor.execute(f"PRAGMA table_info('{table_name}');")
    columns_info = cursor.fetchall()

    print("\n--- Schema ---")
    column_names = []
    for col in columns_info:
      cid, name, col_type, notnull, default_val, pk = col
      column_names.append(name)
      pk_str = " (PRIMARY KEY)" if pk else ""
      null_str = " NOT NULL" if notnull else ""
      print(f" • {name} ({col_type}){pk_str}{null_str}")

    # 2. Fetch and print table content
    cursor.execute(f"SELECT * FROM '{table_name}';")
    rows = cursor.fetchall()

    print("\n--- Content ---")
    if not rows:
      print("(Table is empty)")
    else:
      # Print column headers
      header = " | ".join(column_names)
      print(header)
      print("-" * len(header))

      # Print each row
      for row in rows:
        print(" | ".join(str(val) if val is not None else "NULL" for val in row))

  conn.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Inspect inventory database schema and content."
  )
  parser.add_argument(
    "--db",
    default="./inventory_db/inventory.db",
    help="Path to the sqlite database file",
  )
  args = parser.parse_args()
  display_db_schema_and_content(args.db)
