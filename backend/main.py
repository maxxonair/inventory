from DataBaseClient import DataBaseClient
import logging
from logging import info


def test_database_client():
  """
  Temporary dummy test function for the database client
  """
  # Create a DatabaseClient instance and connect to the inventory database
  client = DataBaseClient(host='192.168.1.194')

  # For demo: list databases
  info(client.list_db())


def main():
  """ 
  Launch inventory backend application

  """
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  test_database_client()


if __name__ == "__main__":
  main()
