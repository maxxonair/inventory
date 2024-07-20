from datetime import datetime


class InventoryItem():

  def __init__(self,
               item_id: int,
               item_name: str,
               item_description: str = None,
               manufacturer: str = None,
               manufacturer_contact: str = None,
               is_checked_out: bool = None,
               check_out_date: datetime = None):

    if check_out_date is None:
      check_out_date_str = ''
    else:
      check_out_date_str = check_out_date.strftime("%m/%d/%Y, %H:%M:%S")

    date_time_now = datetime.now()

    #  Create dictonary from item data
    self.inventoryItemDict = {
        "item_id": item_id,
        "item_name": item_name,
        "item_description": item_description,
        "manufacturer": manufacturer,
        "manufacturer_contact": manufacturer_contact,
        "is_checked_out": is_checked_out,
        "check_out_date": check_out_date_str,
        "date_added": date_time_now.strftime("%m/%d/%Y, %H:%M:%S"),
    }
    data_point = {
        "measurement": measurement,
        "tags": {
            "item_id": inventory_item["item_id"],
            "manufacturer": inventory_item["manufacturer"],
        },
        "fields": {
            "item_name": inventory_item["item_name"],
            "item_description": inventory_item["item_description"],
            "manufacturer_contact": inventory_item["manufacturer_contact"],
            "is_checked_out": inventory_item["is_checked_out"],
            "check_out_date": inventory_item["check_out_date"],
            "date_added": inventory_item["date_added"],
        },
        "time": datetime.utcnow().isoformat() + 'Z'  # Current time in UTC
    }

  def get_item_dict(self):
    return self.inventoryItemDict
