from DataBaseClient import DataBaseClient


client = DataBaseClient(host='192.168.1.194')

# For demo: list databases
print(client.list_db())
