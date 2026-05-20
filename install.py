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
from rich.prompt import Prompt
from rich import print
import os
import sys
import argparse
from shutil import which
import time
from subprocess import call
import requests

# Define project root directory path
PROJECT_ROOT = Path(__file__).parent.resolve()

# Define constants for database configuration
DATABASE_NAME = "inventory"
INVENTORY_TABLE_NAME = "inventory"
USER_DATABASE_NAME = "inventory_user"

INVENTORY_SERVER_CONTAINER_NAME = "inventory_server"
INVENTORY_APP_CONTAINER_NAME = "inventory_app"

PODMAN_DEFAULT_SOCKET_PATH = "/run/user/1000/podman/podman.sock"

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


def get_container_port(container_name: str = "inventory-server") -> int | None:
  """Get the inventory server container port

  Args:
      container_name (str, optional): Inventory server container name.
          Defaults to "inventory-server".

  Returns:
      int | None: Port number if found, None otherwise
  """
  url = f"http+unix://{PODMAN_DEFAULT_SOCKET_PATH.replace('/', '%2F')}/v4.5.1/containers/json"

  session = requests.Session()
  session.mount("http+unix://", requests.adapters.HTTPAdapter())

  resp = session.get(url)
  resp.raise_for_status()
  containers = resp.json()

  for c in containers:
    if container_name in (c.get("Names") or []):
      ports = c.get("Ports", [])
      if ports:
        # Return host → container mapping
        return int(ports[0].get("PublicPort"))
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


def run_config_setup(use_traefik: bool = False) -> bool:
  """Run installation and setup process for the inventory application.

  Returns:
      bool: True if setup is successful, False otherwise
  """
  print(Rule(title="COMPILING CONFIG", style="bold blue"))
  # ---------------------------------------------------------------------------#
  #                         > BACKEND SETUP <
  # ---------------------------------------------------------------------------#
  print(Rule(title="BACKEND CONFIG SETUP", style="bold green"))

  if (PROJECT_ROOT / "backend" / "src" / "server" / "database_config.py").exists():
    warning("Skip regenerating database_config.py. File already set up.")
  else:
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
    host_ip_address = Prompt.ask("Enter host address", default="127.0.0.1")
  info(f"    Host IP address: {host_ip_address}")

  # -- Create compose.yml for all containers --
  if use_traefik:
    info(
      "Configure compose.yml to using Traefik reverse proxy for inventory application."
    )
    inventory_server_url = "https://devmachine.lan"
  else:
    info("Configure compose.yml without reverse proxy for inventory application.")
    inventory_server_url = "http://inventory-server:5000"

  render_template(
    "compose.yml.jinja",
    {
      "database_port": database_server_port,
      "inventory_server_port": inventory_server_port,
      "host_ip_address": host_ip_address,
      "inventoryapp_port": inventoryapp_server_port,
      "inventory_server_url": inventory_server_url,
    },
    PROJECT_ROOT / "compose.yml",
  )

  # NOTE: This file won't be used by the frontend server and will only be
  # created to allow running the frontend manually in development mode.
  if (PROJECT_ROOT / "app" / ".env").exists():
    warning("Skip regenerating app/.env. File already set up.")
  else:
    render_template(
      "frontend.env.jinja",
      {
        "host_address": host_ip_address,
        "inventory_server_port": inventory_server_port,
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

  # TODO check if user is logged in to dockerhub registry

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


def compose_containers(use_traefik: bool = False):
  """Compose and run the podman containers for backend and frontend services."""
  print(Rule(title="DEPLOY CONTAINERS", style="bold blue"))

  os.chdir(PROJECT_ROOT)

  info("[ COMPOSE INVENTORY DATABASE CONTAINER ]")
  info("[ COMPOSE INVENTORY SERVER CONTAINER ]")
  info("[ COMPOSE INVENTORY APP CONTAINER ]")

  call("./scripts/compose_containers.sh", shell=True)

  if use_traefik:
    info("[ COMPOSE TRAEFIK REVERSE PROXY CONTAINER ]")
    call("./scripts/start_traefik.sh", shell=True)


def clean_config_files():
  """Clean up generated configuration files."""
  files_to_remove = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "backend" / "src" / "server" / "mysql.py",
    PROJECT_ROOT / "backend" / "src" / "server" / "database_config.py",
    PROJECT_ROOT / "backend" / "src" / "server" / "admin.py",
    PROJECT_ROOT / "compose.yml",
    PROJECT_ROOT / "app" / ".env",
  ]

  for file_path in files_to_remove:
    if file_path.exists():
      file_path.unlink()
      info(f"Removed: {file_path}")
    else:
      warning(f"File not found, skipping: {file_path}")


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

  parser.add_argument(
    "-p",
    "--purge-config",
    help=(
      "Clean up generated configuration files. Use with caution! This will "
      "remove all generated config files and render the database unusable."
    ),
    action="store_true",
  )

  parser.add_argument(
    "-t",
    "--use-traefik",
    help=("Flag to use Traefik as a reverse proxy for the inventory application. "),
    action="store_true",
  )

  args = parser.parse_args()

  if args.purge_config:
    confirm = input(
      "Are you sure you want to delete all generated configuration files? (y/n): "
    )
    if confirm.lower() == "y":
      clean_config_files()
      print("Configuration files cleaned up successfully.")
    else:
      print("Purge operation cancelled.")
    exit(0)

  if not args.compose_only and not args.build_only:
    # --- SETUP ---
    if not run_config_setup(args.use_traefik):
      error("Installation process failed at the configuration stage.")
      exit(1)

    if args.config_only:
      exit(0)

  # --- BUILD ---
  if not args.compose_only:
    build_podman_images()

  if args.config_only:
    exit(0)

  # --- DEPLOY ---
  time.sleep(2.0)
  compose_containers(args.use_traefik)
