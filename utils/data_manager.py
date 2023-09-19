import json
from dataclasses import dataclass
import logging
import os

from .pattern_check import phone_check


PATH = "data/database.json"

@dataclass
class User:
    id: str
    name : str
    phone: str
    account_number: str



logging.basicConfig(filename='logs/discord.log', level=logging.DEBUG )
def log_data(func):
    def wrapper(*args, **kwargs):
        logging.debug(f"Function {func.__name__} called. get_data() returned {args[0].get_data()}.")
        return func(*args, **kwargs)
    return wrapper


class DB_Manager:
    def __init__(self, path: str = PATH) -> None:
        self.path = PATH
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.create_database()
          
        with open(self.path, "r") as f:
            if f.read() == "":
                self.create_database()

    def create_database(self):
        data = {
            "users": {}
        }
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def get_data(self):
        with open(self.path, "r") as f:
            return json.load(f)
        
    def check_user(self, uid: int):
        data = self.get_data()
        return str(uid) in data['users'].keys()


    def get_user(self, uid: int=None):
        with open(self.path, "r") as f:
            data = json.load(f)
            if uid:
                return data['users'][str(uid)]
            else:
                return data['users']
    @log_data
    def create_user(self, user: User):
        data = self.get_data()
        with open(self.path, 'w') as f:
            data['users'][str(user.id)] = user.__dict__
            json.dump(data, f, indent=4)


    def update_phone(self, uid, phone: str):
        if not (p:=phone_check(phone)): return False
        data = self.get_data()
        with open(self.path, 'w') as f:
            data['users'][str(uid)]['phone'] = p
            json.dump(data, f, indent=4)
        return p
        
    
  

    
if __name__ == "__main__":
    db = DB_Manager()
    # db.create_user(u)
    u = User(123, "test", "0", "0")
    db.create_user(u)
    db.update_phone(123, "1234567890")
    