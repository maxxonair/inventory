

import mariadb

# Configuration
config = {
    'user': 'inventory_user',
    'password': 'inventory24',
    'host': '192.168.1.194',  # or use the container name 'mariadb'
    'port': 3306,
    'database': 'inventory'
}

try:
  # Establishing the connection
  conn = mariadb.connect(**config)
  print("Connected to the database")
except mariadb.Error as e:
  print()
  print(f"Error connecting to MariaDB: {e}")
  exit(0)

# Perform database operations
cursor = conn.cursor()

# Example query
cursor.execute("SELECT DATABASE()")

# Fetch result
database_name = cursor.fetchone()
print(f"Connected to database: {database_name}")

# Close the connection
cursor.close()
conn.close()
