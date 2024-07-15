from influxdb import InfluxDBClient


class DataBaseClient():

  def __init__(self, host: str, port: int = 8086):
    self.host = host
    self.port = port
    self.client = InfluxDBClient(port=port, host=host)

  # ------------------------------------------------------------------------
  #                        [LIST]
  # ------------------------------------------------------------------------
  def list_db(self):
    """
    Return a list of all databases
    """
    return self.client.get_list_database()

  # ------------------------------------------------------------------------
  #                        [MODIFY]
  # ------------------------------------------------------------------------
  def create_db(self, data_base_name: str):
    """
    Create database
    """
    TODO = True
