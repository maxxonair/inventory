"""Service script to prune the media file storage. 

Due to the way the media storage is used, it will accumulate files that are 
not referenced in the database and hence no longer required. 
This script is to identify these files and remove them from the storage.

"""
from logging import info, warning
import logging
from pathlib import Path
import sys
from rich.prompt import Confirm
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.DataBaseClient import DataBaseClient
from backend import media_directory

def is_in_db(item_hash: str, db_list: list):
  for item in db_list:
    if item["image"] == item_hash:
      return True
  return False

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
  db = DataBaseClient()

  item_list = db.get_all_inventory_items_as_dict_list()
  file_list = Path(media_directory).glob("*.png")

  unused_list = []
  num_pruned = 0
  total_num_files = 0

  for png in file_list:
    total_num_files += 1
    file_hash = (png.name).strip(".png")
    if not is_in_db(file_hash, item_list):
      unused_list.append(png)
      num_pruned += 1
      
    
  if num_pruned:
    info(f"{num_pruned} out of {total_num_files} files found to remove:")
  else:
    info('No files found to prune.')
    
  for delfile in unused_list:
    info(f" >  {delfile.name}")
    
  if Confirm.ask(f"Do you want to remove the {num_pruned} identified files?"):
    for delfile in unused_list:
      delfile.unlink()
      info(f"{delfile.name} deleted.")
    
if __name__=="__main__":
  main()
  