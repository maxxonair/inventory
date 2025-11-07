"""Installation script for the inventory management application.

This script sets up configuration files, builds podman images, and deploys
the necessary containers for the backend and frontend services.

"""

import sh
from pathlib import Path
import random
import string
from getpass import getpass
from jinja2 import Environment, FileSystemLoader
from logging import info, warning, error, debug
import logging
import socket
from rich.rule import Rule
from rich import print
import os
import sys
import argparse
from shutil import which
import time
from subprocess import call

# Define project root directory path
PROJECT_ROOT = Path(__file__).parent.resolve()

# Define constants for database configuration
DATABASE_NAME = "inventory"
INVENTORY_TABLE_NAME = "inventory"
USER_DATABASE_NAME = "inventory_user"

INVENTORY_SERVER_CONTAINER_NAME = "inventory_server"
INVENTORY_APP_CONTAINER_NAME = "inventory_app"

# Create template environment
environment = Environment(loader=FileSystemLoader("templates/"))


def is_tool(name):
  """Check whether `name` is on PATH and marked as executable.

  Args:
      name (str): Name of the tool to check

  Returns:
      bool: True if tool is found, False otherwise
  """
  return which(name) is not None


def _is_port_open(ip, port):
  """Check if a port is open on a given IP address.
  Args:
      ip (str): IP address
      port (int): Port number
  Returns:
      bool: True if port is open, False otherwise"""
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((ip, port))
  return result != 0


def scan_ports(start_port, end_port) -> int | None:
  """Scan ports on localhost within a specified range.

  Args:
      start_port (int): Starting port number
      end_port (int): Ending port number
  """
  host = "127.0.0.1"
  debug(f"Scanning ports on {host}...")

  for port in range(start_port, end_port + 1):
    if _is_port_open(host, port):
      debug(f"Port {port} is open")
      return port

  return None


def render_template(template_name: str, context: dict, output_file_path: Path):
  """Renders a jinja2 template with the given context and writes it to the output filename.

  Args:
      template_name (str): Template file name
      context (dict): Context for rendering the template
      output_filename (Path): Output file Path
  """

  template = environment.get_template(template_name)
  with open(output_file_path.resolve(), mode="w", encoding="utf-8") as output_file:
    output_file.write(template.render(context))
    info(f"[x] Created: {output_file_path}")


def query_password(pw_context: str) -> str:
  """Prompt user for password input twice and verify they match.

  Args:
      pw_context (str): Context for the password prompt (e.g., "mysql root")

  Returns:
      str: password entered by the user
  """
  pw_invalid = True
  while pw_invalid:
    pw1 = getpass(f"Enter {pw_context} password:")
    pw2 = getpass(f"Repeat {pw_context} password:")

    # Remove whitespaces from both inputs
    pw1 = pw1.strip(" ")
    pw2 = pw2.strip(" ")

    if not pw1 == pw2:
      error("Passwords don't match. Try again")
    else:
      pw_invalid = False
  return pw1


def rand_id_generator(size: int = 12) -> str:
  """Generate a random string of fixed size

  Args:
      size (int, optional): Number of characters. Defaults to 12.

  Returns:
      str: Random string
  """
  chars = string.ascii_uppercase + string.digits
  return str("inv" + "".join(random.choice(chars) for _ in range(size)))


def run_config_setup() -> bool:
  """Run installation and setup process for the inventory application.

  Returns:
      bool: True if setup is successful, False otherwise
  """
  print(Rule(title="COMPILING CONFIG", style="bold blue"))
  # ---------------------------------------------------------------------------#
  #                         > BACKEND SETUP <
  # ---------------------------------------------------------------------------#
  print(Rule(title="BACKEND CONFIG SETUP", style="bold green"))
  # -- Create backend/.env
  info("Creating mysql database configuration:")

  # MYSQL access credentials are solely for communidation between the backend
  # and the database. Hence, the following is randomly generated and kept hidden
  # at the backend.
  mysql_root_password = rand_id_generator()
  mysql_database = DATABASE_NAME

  render_template(
    "backend.env.jinja",
    {
      "mysql_root_password": mysql_root_password,
      "mysql_database": mysql_database,
    },
    PROJECT_ROOT / ".env",
  )

  render_template(
    "mysql.py.jinja",
    {
      "mysql_user": "root",
      "mysql_user_password": mysql_root_password,
    },
    PROJECT_ROOT / "backend" / "src" / "server" / "mysql.py",
  )

  render_template(
    "database_config.py.jinja",
    {
      "database_name": DATABASE_NAME,
      "inventory_table_name": INVENTORY_TABLE_NAME,
      "user_database_name": USER_DATABASE_NAME,
    },
    PROJECT_ROOT / "backend" / "src" / "server" / "database_config.py",
  )

  # -- Scan for open port for database server
  database_server_port = scan_ports(3307, 3400)
  if database_server_port is None:
    print(
      "[red][!] No open port found for database server in the range 3306-3400[/red]"
    )
    return False
  info(f"[!] Selected database server port: {database_server_port}")

  # -- Scan for open port for inventory server
  inventory_server_port = scan_ports(5001, 5400)
  if inventory_server_port is None:
    print(
      "[red][!] No open port found for inventory server in the range 5000-5400[/red]"
    )
    return False
  info(f"[!] Selected inventory server port: {inventory_server_port}")

  render_template(
    "admin.py.jinja",
    {
      "database_port": database_server_port,
    },
    PROJECT_ROOT / "backend" / "src" / "server" / "admin.py",
  )

  # ---------------------------------------------------------------------------#
  #                        > FRONTEND SETUP <
  # ---------------------------------------------------------------------------#
  print(Rule(title="FRONTEND CONFIG SETUP", style="bold red"))

  # -- Scan for open port for inventory application server
  inventoryapp_server_port = scan_ports(3000, 3330)
  if inventoryapp_server_port is None:
    print(
      "[red][!] No open port found for the inventory application server in the range 3000-3250[/red]"
    )
    return False
  info(f"[!] Selected inventory application server port: {inventoryapp_server_port}")
  host_ip_address = socket.gethostbyname(socket.gethostname())
  # TODO this search does not seem to work. Find a better way to determine host IP
  if str(host_ip_address) == "127.0.1.1" or str(host_ip_address) == "127.0.0.1":
    warning(
      "IP address of current host could not be determined. Please enter a valid host address manually."
    )
    host_ip_address = input("Enter host address :  ")
  info(f"    Host IP address: {host_ip_address}")

  # -- Create docker-compose.yml for all containers --
  render_template(
    "docker-compose.yml.jinja",
    {
      "database_port": database_server_port,
      "inventory_server_port": inventory_server_port,
      "host_ip_address": host_ip_address,
      "inventoryapp_port": inventoryapp_server_port,
    },
    PROJECT_ROOT / "docker-compose.yml",
  )

  render_template(
    "frontend.env.jinja",
    {
      "host_address": INVENTORY_SERVER_CONTAINER_NAME,
      "inventory_server_port": 5000,
    },
    PROJECT_ROOT / "app" / ".env",
  )
  print("[green]  ---> Configuration setup completed successfully[/green]\n")
  print(
    f"[green]  The inventory application will be accessbile via:[/green] [orange]http://{host_ip_address}:{inventoryapp_server_port}[/orange]\n"
  )
  return True


def build_podman_images():
  """Build podman images for backend and frontend services."""
  print(Rule(title="BUILDING PODMAN IMAGES", style="bold blue"))
  print(Rule(title="BUILDING BACKEND", style="bold green"))

  os.chdir(PROJECT_ROOT / "backend" / "src" / "server")

  sh.podman(
    "build",
    "--no-cache",
    "-t",
    "inventoryserver:latest",
    ".",
    _out=sys.stdout.write,
    _err=sys.stderr.write,
    _tty_out=True,
  )

  print(Rule(title="BUILDING FRONTEND", style="bold red"))

  os.chdir(PROJECT_ROOT / "app")

  # Build frontend image
  sh.podman(
    "build",
    "--no-cache",
    "-t",
    "inventoryapp:latest",
    ".",
    _out=sys.stdout.write,
    _err=sys.stderr.write,
    _tty_out=True,
  )


def compose_containers():
  """Compose and run the podman containers for backend and frontend services."""
  print(Rule(title="DEPLOY CONTAINERS", style="bold blue"))

  os.chdir(PROJECT_ROOT)

  info("[ COMPOSE INVENTORY DATABASE CONTAINER ]")
  info("[ COMPOSE INVENTORY SERVER CONTAINER ]")
  info("[ COMPOSE INVENTORY APP CONTAINER ]")

  call("./scripts/compose_containers.sh", shell=True)


if __name__ == "__main__":
  logger = logging.getLogger(__name__)
  logging.basicConfig(
    encoding="utf-8", level=logging.INFO, format="[%(levelname)s]  %(message)s"
  )

  parser = argparse.ArgumentParser(
    prog="Inventory Installer",
    description="Create Configuration and Build Podman Images for Inventory Application",
  )

  parser.add_argument(
    "-c",
    "--config-only",
    help="Only run configuration setup, skip build and compose steps",
    action="store_true",
  )

  parser.add_argument(
    "-r",
    "--compose-only",
    help="Only compose and run podman containers, skip configuration and build steps",
    action="store_true",
  )

  parser.add_argument(
    "-b",
    "--build-only",
    help="Only build podman container images, skip configuration and build steps",
    action="store_true",
  )

  args = parser.parse_args()

  if not args.compose_only and not args.build_only:
    # --- SETUP ---
    if not run_config_setup():
      error("Installation process failed at the configuration stage.")
      exit(1)

    if args.config_only:
      exit(0)

  # --- BUILD ---
  build_podman_images()

  if args.config_only:
    exit(0)

  # --- DEPLOY ---
  time.sleep(2.0)
  compose_containers()
