"""Schema definitions for every table in the inventory database.

This module is the single source of truth for table structure. Each table
is described declaratively as a `TableSchema` made up of `Column` objects,
and `TableSchema.create_table_query()` generates the corresponding
`CREATE TABLE IF NOT EXISTS` statement.

DataBaseClient uses `ALL_TABLE_SCHEMAS` to initialise the database and
`INVENTORY_USER_SCHEMA` (etc.) directly where a specific table is needed,
instead of each table's CREATE TABLE statement being hand-built out of
string concatenation scattered across the codebase.
"""

from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
#                        [TABLE NAMES]
# ---------------------------------------------------------------------------

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_REGISTRY_TABLE_NAME = "inventory"

# [!SENSITIVE!] Name of the table in INVENTORY_DB_NAME database to store the
#               Inventory users
INVENTORY_USER_TABLE_NAME = "inventory_user"

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_STORAGE_LOCATIONS_TABLE_NAME = "storage_locations"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the inventory
#           item checkout history
INVENTORY_CHECKOUT_TABLE_NAME = "checkout_history"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the inventory
#            log-in history
INVENTORY_LOGIN_TABLE_NAME = "login_history"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the list of
#            valid/selectable item_type values offered by the client
INVENTORY_ITEM_TYPES_TABLE_NAME = "item_types"

# ---------------------------------------------------------------------------
#                        [STATE ENUMS]
# ---------------------------------------------------------------------------


# [ENUM] defining thw two possible checkout types: borrow and return
class CheckoutType(Enum):
  BORROW = 1
  RETURN = 2


# [ENUM] defining the possible login statuses
class LoginStatus(Enum):
  SUCCESS = 1
  USER_NOT_FOUND = 2
  PASSWORD_INVALID = 3


# [ENUM] defining the possible inventory user privilege levels
# (Moved here from the now-removed InventoryUser.py so that a privilege
# level can be referenced without needing an InventoryUser instance)
class UserPrivileges(Enum):
  GUEST = 0
  REPORTER = 1
  DEVELOPPER = 2
  MAINTAINER = 3
  OWNER = 4


@dataclass
class Column:
  """A single column definition within a table schema"""

  name: str
  sql_type: str
  primary_key: bool = False
  autoincrement: bool = False
  not_null: bool = False
  unique: bool = False

  def to_sql(self) -> str:
    """Render this column as a fragment of a CREATE TABLE statement"""
    parts = [self.name, self.sql_type]
    if self.primary_key:
      parts.append("PRIMARY KEY")
    if self.autoincrement:
      parts.append("AUTOINCREMENT")
    if self.unique:
      parts.append("UNIQUE")
    if self.not_null:
      parts.append("NOT NULL")
    return " ".join(parts)


@dataclass
class TableSchema:
  """Full schema (name + columns) for a single database table"""

  name: str
  columns: list[Column] = field(default_factory=list)

  def create_table_query(self) -> str:
    """Compile the CREATE TABLE IF NOT EXISTS statement for this table"""
    columns_sql = ", ".join(column.to_sql() for column in self.columns)
    return f"CREATE TABLE IF NOT EXISTS {self.name} ( {columns_sql} )"

  @property
  def column_names(self) -> list[str]:
    """Names of all non-primary-key columns in this table"""
    return [column.name for column in self.columns if not column.primary_key]


# ---------------------------------------------------------------------------
#                        [TABLE SCHEMAS]
# ---------------------------------------------------------------------------

INVENTORY_REGISTRY_SCHEMA = TableSchema(
  name=INVENTORY_REGISTRY_TABLE_NAME,
  columns=[
    Column("id", "INTEGER", primary_key=True, autoincrement=True),
    Column("name", "VARCHAR(255)", not_null=True),
    Column("image", "VARCHAR(1055)"),
    Column("description", "VARCHAR(1055)"),
    Column("manufacturer", "VARCHAR(255)"),
    Column("details", "VARCHAR(1055)"),
    Column("is_checked_out", "INTEGER"),
    Column("check_out_date", "VARCHAR(255)"),
    Column("check_out_poc", "VARCHAR(1055)"),
    Column("date_added", "VARCHAR(255)"),
    Column("tags", "VARCHAR(1055)"),
    Column("location", "INTEGER"),
    Column("item_type", "VARCHAR(1055)"),
    Column("manufacturer_link", "VARCHAR(255)"),
    Column("project", "VARCHAR(255)"),
    Column("manufacturer_location", "VARCHAR(255)"),
    Column("color", "VARCHAR(255)"),
    Column("material", "VARCHAR(255)"),
    Column("product_use", "VARCHAR(255)"),
    Column("number_items", "INTEGER"),
  ],
)

INVENTORY_STORAGE_LOCATIONS_SCHEMA = TableSchema(
  name=INVENTORY_STORAGE_LOCATIONS_TABLE_NAME,
  columns=[
    Column("id", "INTEGER", primary_key=True, autoincrement=True),
    Column("name", "VARCHAR(255)", not_null=True),
    Column("description", "VARCHAR(1055)"),
    Column("date_added", "VARCHAR(255)"),
    Column("tags", "VARCHAR(1055)"),
  ],
)

# checkout - Status (direction) of the checkout.
#            checkout = 1 means item was checked out,
#            checkout = 0 means item was returned
INVENTORY_CHECKOUT_SCHEMA = TableSchema(
  name=INVENTORY_CHECKOUT_TABLE_NAME,
  columns=[
    Column("id", "INTEGER", primary_key=True, autoincrement=True),
    Column("user", "VARCHAR(255)", not_null=True),
    Column("item_id", "INTEGER"),
    Column("checkout", "INTEGER"),
    Column("date", "VARCHAR(255)"),
  ],
)

INVENTORY_LOGIN_SCHEMA = TableSchema(
  name=INVENTORY_LOGIN_TABLE_NAME,
  columns=[
    Column("id", "INTEGER", primary_key=True, autoincrement=True),
    Column("user", "VARCHAR(255)", not_null=True),
    Column("status", "INTEGER"),
    Column("date", "VARCHAR(255)"),
  ],
)

# [!SENSITIVE!] Stores inventory user credentials (hashed passwords) and
#               privilege levels. Formerly built by
#               InventoryUser.get_sql_query_table_for_user().
INVENTORY_USER_SCHEMA = TableSchema(
  name=INVENTORY_USER_TABLE_NAME,
  columns=[
    Column("id", "INTEGER", primary_key=True, autoincrement=True),
    Column("user_name", "VARCHAR(50)", not_null=True, unique=True),
    Column("user_password", "VARCHAR(50)"),
    Column("user_privileges", "INT"),
  ],
)

# Stores the list of item_type values the client application allows an
# inventory item to be tagged with (populates the item_type dropdown, etc).
# NOTE: this is a plain reference/lookup list — the inventory table's
# item_type column is not constrained by a foreign key against it, so
# existing free-text values already stored on items keep working unchanged.
INVENTORY_ITEM_TYPES_SCHEMA = TableSchema(
  name=INVENTORY_ITEM_TYPES_TABLE_NAME,
  columns=[
    Column("id", "INTEGER", primary_key=True, autoincrement=True),
    Column("name", "VARCHAR(255)", not_null=True, unique=True),
  ],
)

# Single source of truth listing every table schema in the database. Used by
# DataBaseClient to initialise and verify the database on connect.
ALL_TABLE_SCHEMAS: list[TableSchema] = [
  INVENTORY_REGISTRY_SCHEMA,
  INVENTORY_STORAGE_LOCATIONS_SCHEMA,
  INVENTORY_LOGIN_SCHEMA,
  INVENTORY_CHECKOUT_SCHEMA,
  INVENTORY_USER_SCHEMA,
  INVENTORY_ITEM_TYPES_SCHEMA,
]
