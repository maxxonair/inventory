#!/usr/bin/env python3
"""migrate_db_schema.py

Standalone migration tool for the inventory SQLite database.

Every table in the running database is compared against the canonical
definitions in `server/database_schema.py` (column set, SQL type, NOT NULL,
PRIMARY KEY, AUTOINCREMENT, UNIQUE). Any table that has drifted from that
schema -- most notably a legacy table created before the declarative
TableSchema system existed, where `CREATE TABLE IF NOT EXISTS` silently left
an old, untyped table in place -- is rebuilt to match, with existing data
copied across column-by-column.

This fixes the "new inventory item gets id = NULL" bug at its root: it
rebuilds any table whose `id` column isn't a real `INTEGER PRIMARY KEY
AUTOINCREMENT`, so new inserts get real, auto-generated ids going forward.

Usage:
    python migrate_db_schema.py [--db PATH] [--dry-run] [--drop-legacy] [--yes]

Safe by default:
    - Makes a full file-level backup of the .db file before touching anything.
    - Renames any drifted table to `<name>_legacy_backup_<timestamp>` instead
      of dropping it, unless --drop-legacy is passed.
    - --dry-run reports what would change without writing anything.

Run this from the project's backend directory (the same place you'd run
`uv run -m src.InventoryServer`), so that `server.database_schema` resolves.
"""

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from server.database_schema import ALL_TABLE_SCHEMAS, TableSchema


# ---------------------------------------------------------------------------
#                        [INTROSPECTION HELPERS]
# ---------------------------------------------------------------------------


def get_actual_columns(conn: sqlite3.Connection, table_name: str) -> dict:
  """Return {column_name: {"type", "notnull", "pk"}} for a live table.

  Returns an empty dict if the table doesn't exist.
  """
  rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
  return {
    row[1]: {"type": row[2] or "", "notnull": bool(row[3]), "pk": bool(row[5])}
    for row in rows
  }


def get_unique_columns(conn: sqlite3.Connection, table_name: str) -> set:
  """Return column names covered by a single-column UNIQUE index."""
  unique_cols = set()
  for _, index_name, is_unique, *_rest in conn.execute(
    f"PRAGMA index_list({table_name})"
  ).fetchall():
    if not is_unique:
      continue
    cols = conn.execute(f"PRAGMA index_info({index_name})").fetchall()
    if len(cols) == 1:
      unique_cols.add(cols[0][2])
  return unique_cols


def get_create_sql(conn: sqlite3.Connection, table_name: str) -> str:
  row = conn.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
  ).fetchone()
  return row[0] if row else ""


def table_matches_schema(conn: sqlite3.Connection, schema: TableSchema):
  """Compare a live table against its declarative schema.

  Returns (matches: bool, reasons: list[str]).
  """
  reasons = []
  actual = get_actual_columns(conn, schema.name)

  if not actual:
    return False, ["table does not exist"]

  expected_names = [c.name for c in schema.columns]
  actual_names = list(actual.keys())

  if set(expected_names) != set(actual_names):
    missing = set(expected_names) - set(actual_names)
    extra = set(actual_names) - set(expected_names)
    if missing:
      reasons.append(f"missing columns: {sorted(missing)}")
    if extra:
      reasons.append(f"unexpected columns: {sorted(extra)}")

  unique_cols = get_unique_columns(conn, schema.name)
  create_sql_upper = get_create_sql(conn, schema.name).upper()

  for col in schema.columns:
    if col.name not in actual:
      continue  # already reported as a missing column above
    info = actual[col.name]

    if info["type"].strip().upper() != col.sql_type.strip().upper():
      reasons.append(
        f"column '{col.name}' type is '{info['type']}', expected '{col.sql_type}'"
      )
    if info["pk"] != col.primary_key:
      reasons.append(
        f"column '{col.name}' primary_key is {info['pk']}, expected {col.primary_key}"
      )
    if col.not_null and not info["notnull"]:
      reasons.append(f"column '{col.name}' should be NOT NULL")
    if col.unique and col.name not in unique_cols:
      reasons.append(f"column '{col.name}' should be UNIQUE")
    if (
      col.primary_key and col.autoincrement and "AUTOINCREMENT" not in create_sql_upper
    ):
      # AUTOINCREMENT isn't reported by PRAGMA table_info, so check the raw SQL.
      reasons.append(f"column '{col.name}' should be AUTOINCREMENT")

  return (len(reasons) == 0), reasons


# ---------------------------------------------------------------------------
#                        [MIGRATION]
# ---------------------------------------------------------------------------


def migrate_table(
  conn: sqlite3.Connection,
  schema: TableSchema,
  drop_legacy: bool,
  dry_run: bool,
  log,
):
  """Rebuild a single table to match its schema, preserving existing data."""
  actual_cols = set(get_actual_columns(conn, schema.name).keys())
  table_exists = bool(actual_cols)

  if not table_exists:
    log(f"  -> table doesn't exist yet -> create '{schema.name}' from current schema")
    if dry_run:
      return
    conn.execute(schema.create_table_query())
    conn.commit()
    return

  expected_cols = [c.name for c in schema.columns]
  shared_cols = [c for c in expected_cols if c in actual_cols]
  dropped_cols = sorted(actual_cols - set(expected_cols))

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  legacy_name = f"{schema.name}_legacy_backup_{timestamp}"

  log(f"  -> rename '{schema.name}' -> '{legacy_name}'")
  log(f"  -> create new '{schema.name}' from current schema")
  if shared_cols:
    log(f"  -> copy {len(shared_cols)} shared column(s): {shared_cols}")
  if dropped_cols:
    log(f"  -> WARNING: dropping data in old-only column(s): {dropped_cols}")

  if dry_run:
    if drop_legacy:
      log(f"  -> (dry-run) would drop '{legacy_name}' after copying data")
    else:
      log(f"  -> (dry-run) would keep '{legacy_name}' for manual review")
    return

  conn.execute(f"ALTER TABLE {schema.name} RENAME TO {legacy_name}")
  conn.execute(schema.create_table_query())

  if shared_cols:
    cols_sql = ", ".join(shared_cols)
    conn.execute(
      f"INSERT INTO {schema.name} ( {cols_sql} ) SELECT {cols_sql} FROM {legacy_name}"
    )
    # Rows that had a NULL primary key in the old table are re-inserted with
    # an explicit NULL id above, which SQLite auto-assigns a fresh rowid for
    # -- so previously-broken rows get a real id without any special-casing.

  if drop_legacy:
    conn.execute(f"DROP TABLE {legacy_name}")
    log(f"  -> dropped '{legacy_name}'")
  else:
    log(f"  -> kept '{legacy_name}' (pass --drop-legacy to remove automatically)")

  conn.commit()


def backup_db_file(db_path: Path, log) -> Path:
  backup_path = db_path.with_suffix(
    db_path.suffix + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  )
  shutil.copy2(db_path, backup_path)
  log(f"Backed up '{db_path}' -> '{backup_path}'")
  return backup_path


# ---------------------------------------------------------------------------
#                        [ENTRY POINT]
# ---------------------------------------------------------------------------


def main():
  parser = argparse.ArgumentParser(
    description="Rebuild any inventory.db table that has drifted from database_schema.py"
  )
  parser.add_argument(
    "--db",
    default="../inventory_db/inventory.db",
    help="Path to the sqlite database file",
  )
  parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Report what would change without writing anything",
  )
  parser.add_argument(
    "--drop-legacy",
    action="store_true",
    help="Drop renamed legacy tables after migrating (default: keep them for review)",
  )
  parser.add_argument(
    "--yes", action="store_true", help="Don't prompt for confirmation before writing"
  )
  args = parser.parse_args()

  def log(msg):
    print(msg)

  db_path = Path(args.db)
  if not db_path.exists():
    print(f"Database file not found: {db_path}")
    sys.exit(1)

  conn = sqlite3.connect(str(db_path))

  log(
    f"Checking {len(ALL_TABLE_SCHEMAS)} table(s) in '{db_path}' against database_schema.py...\n"
  )

  drifted = []
  for schema in ALL_TABLE_SCHEMAS:
    matches, reasons = table_matches_schema(conn, schema)
    log(f"[{'OK' if matches else 'DRIFTED'}] {schema.name}")
    for reason in reasons:
      log(f"    - {reason}")
    if not matches:
      drifted.append(schema)

  if not drifted:
    log("\nAll tables match the schema. Nothing to do.")
    conn.close()
    return

  log(f"\n{len(drifted)} table(s) need migration: {[s.name for s in drifted]}")

  if args.dry_run:
    log("\n--dry-run: showing planned actions, no changes will be made.\n")
    for schema in drifted:
      log(f"Table '{schema.name}':")
      migrate_table(conn, schema, args.drop_legacy, dry_run=True, log=log)
    conn.close()
    return

  if not args.yes:
    answer = (
      input(f"\nProceed with migrating {len(drifted)} table(s)? [y/N] ").strip().lower()
    )
    if answer != "y":
      log("Aborted. No changes made.")
      conn.close()
      return

  backup_db_file(db_path, log)

  try:
    for schema in drifted:
      log(f"\nMigrating '{schema.name}':")
      migrate_table(conn, schema, args.drop_legacy, dry_run=False, log=log)
    log("\nMigration complete.")
  except Exception as e:
    log(f"\nMigration stopped due to an error: {e}")
    log("Any tables migrated before this point were already committed.")
    log("The pre-migration file backup above can be used to restore if needed.")
    raise
  finally:
    conn.close()


if __name__ == "__main__":
  main()
