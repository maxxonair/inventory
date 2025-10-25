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

# Define project root directory path
PROJECT_ROOT = Path(__file__).parent.resolve()

# Define constants for database configuration
DATABASE_NAME = "inventory"
INVENTORY_TABLE_NAME = "inventory"
USER_DATABASE_NAME = "inventory_user"

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
  return "".join(random.choice(chars) for _ in range(size))


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
  mysql_user = rand_id_generator()
  mysql_user_password = rand_id_generator()
  mysql_root_password = rand_id_generator()
  mysql_database = DATABASE_NAME

  render_template(
    "backend.env.jinja",
    {
      "mysql_root_password": mysql_root_password,
      "mysql_user": mysql_user,
      "mysql_user_password": mysql_user_password,
      "mysql_database": mysql_database,
    },
    PROJECT_ROOT / "backend" / ".env",
  )

  render_template(
    "mysql.py.jinja",
    {
      "mysql_user": mysql_user,
      "mysql_user_password": mysql_user_password,
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
    PROJECT_ROOT / "backend" / "src" / "server" / "mysql.py",
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
    "backend.docker-compose.yml.jinja",
    {
      "database_port": database_server_port,
      "inventory_server_port": inventory_server_port,
    },
    PROJECT_ROOT / "backend" / "docker-compose.yml",
  )

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
  skip_webdev_install = is_tool("bun") and is_tool("npm")
  if skip_webdev_install:
    info(
      "[!] Found bun and npm. Assuming all required tools are installed to proceed."
      "Skipping web development environment setup."
    )
  else:
    # - Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
    # TODO

    # -- Install [bun]
    sh.curl(
      "-fsSL",
      "https://bun.sh/install",
      "|",
      "bash",
      _out=sys.stdout.write,
      _err=sys.stderr.write,
      _text=True,
    )

    # :warning: Ensure the follow the instructions at the end of the installation and update your ```PATH```
    sh.export("PATH=$HOME/.bun/bin:$PATH", _bg=True)

    # - Install [svelte-kit](https://svelte.dev/docs/kit/introduction)

    # -- Install [vite]
    sh.bun(
      "install", "-D", "vite", _out=sys.stdout.write, _err=sys.stderr.write, _text=True
    )

  # -- Scan for open port for inventory application server
  inventoryapp_server_port = scan_ports(3000, 3330)
  if inventoryapp_server_port is None:
    print(
      "[red][!] No open port found for the inventory application server in the range 3000-3250[/red]"
    )
    return False
  info(f"[!] Selected inventory application server port: {inventoryapp_server_port}")
  host_ip_address = socket.gethostbyname(socket.gethostname())
  if str(host_ip_address) == "127.0.1.1":
    warning(
      "IP address of current host could not be determined. Please enter a valid host address manually."
    )
    host_ip_address = input("Enter host address :")
  info(f"    Host IP address: {host_ip_address}")

  render_template(
    "frontend.docker-compose.yml.jinja",
    {
      "host_ip_address": host_ip_address,
      "inventoryapp_port": inventoryapp_server_port,
    },
    PROJECT_ROOT / "app" / "docker-compose.yml",
  )

  # TODO add camera and printer server ports
  render_template(
    "frontend.env.jinja",
    {
      "host_address": host_ip_address,
      "inventory_server_port": inventory_server_port,
      "camera_server_port": None,
      "printer_server_port": None,
    },
    PROJECT_ROOT / "app" / ".env",
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
  )

  print(Rule(title="BUILDING FRONTEND", style="bold red"))

  os.chdir(PROJECT_ROOT / "app")

  sh.bun("install", _out=sys.stdout.write, _err=sys.stderr.write, _text=True)

  sh.bun("run", "build", _out=sys.stdout.write, _err=sys.stderr.write)

  # Build frontend image
  sh.podman(
    "build",
    "--no-cache",
    "-t",
    "inventoryapp:latest",
    ".",
    _out=sys.stdout.write,
    _err=sys.stderr.write,
  )


def compose_containers():
  """Compose and run the podman containers for backend and frontend services."""
  print(Rule(title="COMPOSING PODMAN CONTAINERS", style="bold blue"))

  # Remove existing containers if any
  try:
    sh.podman("rm", "inventory_db")
  except:
    pass
  try:
    sh.podman("rm", "inventory-server")
  except:
    pass
  try:
    sh.podman("rm", "inventory-app")
  except:
    pass

  os.chdir(PROJECT_ROOT / "backend")

  info("[ COMPOSE INVENTORY DATABASE CONTAINER ]")
  sh.podman_compose(
    "up",
    "-d",
    "inventory_db",
    _out=sys.stdout.write,
    _err=sys.stderr.write,
  )

  info("[ COMPOSE INVENTORY SERVER CONTAINER ]")
  sh.podman_compose(
    "up",
    "-d",
    "inventory_server",
    _out=sys.stdout.write,
    _err=sys.stderr.write,
  )

  os.chdir(PROJECT_ROOT / "app")

  info("[ COMPOSE INVENTORY APP CONTAINER ]")
  sh.podman_compose(
    "up",
    "-d",
    "inventory_app",
    _out=sys.stdout.write,
    _err=sys.stderr.write,
  )

  info("[ RUNNING CONTAINERS ]")
  sh.podman("ps", _out=sys.stdout.write, _err=sys.stderr.write)


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

  args = parser.parse_args()

  if not args.compose_only:
    # --- SETUP ---
    if not run_config_setup():
      error("Installation process failed at the configuration stage.")
      exit(1)
    else:
      print("[green]  ---> Configuration setup completed successfully[/green]\n")

    if parser.parse_args().config_only:
      exit(0)

    # --- BUILD ---
    build_podman_images()

  # --- RUN ---
  time.sleep(2.0)
  compose_containers()
