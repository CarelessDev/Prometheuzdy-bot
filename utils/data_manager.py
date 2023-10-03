import json
from dataclasses import dataclass
import logging
import os

from .pattern_check import phone_check
from .promptpay import PromptPay


PATH = "data/database.json"
QR_PATH = "data/qr_codes"


@dataclass
class User:
    id: str
    name: str
    phone: str
    account_number: str


logging.basicConfig(filename='logs/discord.log', level=logging.DEBUG)


def log_data(func):
    def wrapper(*args, **kwargs):
        logging.debug(
            f"Function {func.__name__} called. get_data() returned {args[0].get_data()}.")
        return func(*args, **kwargs)
    return wrapper


class DB_Manager:
    def __init__(self, path: str = PATH) -> None:
        self.path = path
        self.ensure_database()
        self.ensure_promptpay()

        

    def check_user(self, uid: int):
        data = self.get_data()
        return str(uid) in data['users'].keys()

    
    def ensure_database(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.create_database()
            logging.debug("Created database.")

        if not os.path.exists(QR_PATH):
            os.mkdir(QR_PATH)
            logging.debug("Created QR code directory.")

        with open(self.path, "r") as f:
            if f.read() == "":
                self.create_database()

    def ensure_promptpay(self):
        data = self.get_data()
        for uid in data['users'].keys():                                                                                #   for each user in database
            if not data['users'][str(uid)].get('promptpay_token') and phone_check(data['users'][str(uid)]['phone']):        #   if promptpay_token not exist and phone is valid 
                self.set_phone(uid, data['users'][str(uid)]['phone'])                                                       #   set phone number to generate promptpay_token
                
            
    
    # create functions ====================================================================================================

    def create_database(self):
        data = {
            "users": {}
        }
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    @log_data
    def create_user(self, user: User):
        data = self.get_data()
        with open(self.path, 'w') as f:
            data['users'][str(user.id)] = user.__dict__
            json.dump(data, f, indent=4)
    
    # get functions ====================================================================================================

    def get_data(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def get_user(self, uid: int = None):
        with open(self.path, "r") as f:
            data = json.load(f)
            if uid:
                return data['users'][str(uid)]
            else:
                return data['users']

    # update functions ====================================================================================================

    def set_phone(self, uid, phone: str):
        if not (p := phone_check(phone)):
            return False
        data = self.get_data()
        with open(self.path, 'w') as f:
            data['users'][str(uid)]['phone'] = p
            data['users'][str(uid)]['promptpay_token'] = str(PromptPay(p))
            json.dump(data, f, indent=4)
        return p
    
    def set_qr(self, uid):
        data = self.get_data()
        with open(self.path, 'w') as f:
            data['users'][str(uid)]['qr'] = os.path.join(QR_PATH, f"{uid}.png")
            json.dump(data, f, indent=4)
  



if __name__ == "__main__":
    db = DB_Manager()
    # db.create_user(u)
    u = User(123, "test", "0", "0")
    db.create_user(u)
    db.update_phone(123, "1234567890")
