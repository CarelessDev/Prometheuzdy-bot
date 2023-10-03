import re 
import libscrc
import qrcode
import io

ID_PAYLOAD_FORMAT = "00"
ID_POI_METHOD = "01"
ID_MERCHANT_INFORMATION_BOT = "29"
ID_TRANSACTION_CURRENCY = "53"
ID_TRANSACTION_AMOUNT = "54"
ID_COUNTRY_CODE = "58"
ID_CRC = "63"

PAYLOAD_FORMAT_EMV_QRCPS_MERCHANT_PRESENTED_MODE = "01"
POI_METHOD_STATIC = "11"
POI_METHOD_DYNAMIC = "12"
MERCHANT_INFORMATION_TEMPLATE_ID_GUID = "00"
BOT_ID_MERCHANT_PHONE_NUMBER = "01"
BOT_ID_MERCHANT_TAX_ID = "02"
BOT_ID_MERCHANT_EWALLET_ID = "03"
GUID_PROMPTPAY = "A000000677010111"
TRANSACTION_CURRENCY_THB = "764"
COUNTRY_CODE_TH = "TH"

class PromptPay:
    def __init__(self, phone_number):
        self._phone_number = phone_number
    
    @property
    def phone_number(self):
        return re.sub(r'\D', '', self._phone_number)
    

    @property
    def type(self):
        length = len(self.phone_number) 
        if length >= 15:
            return BOT_ID_MERCHANT_EWALLET_ID
        elif length >= 13:
            return BOT_ID_MERCHANT_TAX_ID
        else:
            return BOT_ID_MERCHANT_PHONE_NUMBER
        
    def pp_format(self, id: str, value: str) -> str:
        """format string"""
        return id + format(len(value), "02") + value
    
    def generate_id_merchant_information(self) -> str:
        """generate id merchant information string"""
        if len(self.phone_number) < 13:
            formatted_phone_number = re.sub("^0", "66", self.phone_number)
            formatted_phone_number = ("0000000000000" + self.phone_number)[-13:]  # last 13 digits
        id_merchant_information = self.pp_format(MERCHANT_INFORMATION_TEMPLATE_ID_GUID, GUID_PROMPTPAY)
        id_merchant_information += self.pp_format(self.type, formatted_phone_number)
        return id_merchant_information
    
    def checksum(self, target: str) -> str:
        """
        :param target:
        :return:
        """
        byte_str = target.encode("ascii")  # convert to bytes
        hex_str = hex(libscrc.xmodem(byte_str, 0xFFFF))
        code = hex_str.replace("0x", "").upper()
        result = ("0000" + code)[-4:]  # only last 4 digits

        return result
    
    def generate_crc(self, payload: str) -> str:
        """generate crc string"""
        crc = payload + ID_CRC + "04"
        return self.pp_format(ID_CRC, self.checksum(crc))
    
    def generate_payload(self, amount: float = 0.00) -> str:
        """generate promptpay payload string"""

        payload = self.pp_format(ID_PAYLOAD_FORMAT, PAYLOAD_FORMAT_EMV_QRCPS_MERCHANT_PRESENTED_MODE)       # payload format
        payload += self.pp_format(ID_POI_METHOD, POI_METHOD_DYNAMIC if amount else POI_METHOD_STATIC)       # poi method
        payload += self.pp_format(ID_MERCHANT_INFORMATION_BOT, self.generate_id_merchant_information())     # merchant information
        payload += self.pp_format(ID_COUNTRY_CODE, COUNTRY_CODE_TH)                                         # country code
        payload += self.pp_format(ID_TRANSACTION_CURRENCY, TRANSACTION_CURRENCY_THB)                        # transaction currency
        if amount:
            payload += self.pp_format(ID_TRANSACTION_AMOUNT, "{0:.2f}".format(amount))                      # transaction amount
        payload += self.generate_crc(payload)                                                               # crc                  
        return payload
    

    def __str__(self) -> str:
        """return promptpay payload string"""
        return self.generate_payload()


    def __to_byte_QR(self, amount: float = 0) -> io.BytesIO:
        file = qrcode.make(self.generate_payload(amount))
        byte_io = io.BytesIO()
        file.save(byte_io)
        byte_io.seek(0)
        return byte_io
    
    
    def __to_QR(self, path: str, amount: float= 0) -> None:
        """save QR code to path"""
        file = qrcode.make(self.generate_payload(amount))
        file.save(path)
        


    @classmethod
    def to_byte_QR(cls, phone_number: str, amount: float = 0) -> io.BytesIO:
        """Generate QR code as byte from phone number and amount
        
        Parameters
        ----------
        phone_number : str
            phone number
        amount : float, optional
            amount, by default 0
        
        Returns
        -------
        io.BytesIO
            QR code as byte
        """
        return cls(phone_number).__to_byte_QR(amount)
    
    @classmethod
    def to_QR(cls, phone_number: str, path: str, amount: float = 0) -> None:
        """save QR code to path"""
        cls(phone_number).__to_QR(path, amount)

    @staticmethod
    def token2QR(token: str, path: str) -> None:
        """save QR code to path"""
        file = qrcode.make(token)
        file.save(path)

    @staticmethod
    def token2byte_QR(token: str) -> io.BytesIO:
        """return QR code as byte"""
        file = qrcode.make(token)
        byte_io = io.BytesIO()
        file.save(byte_io)
        byte_io.seek(0)
        return byte_io