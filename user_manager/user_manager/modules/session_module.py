import json
import base64
from datetime import datetime, timezone, timedelta

class SessionModule:
    def __init__(self, application_id):
        self.application_id = application_id
        timezone_offset = -8.0 # Pacific Standard Time (UTC−08:00)
        tzinfo = timezone(timedelta(hours=timezone_offset))
        self.creation_date = datetime.now(tzinfo)
        self.ttl = timedelta(hours=1)  # Example: 1 hour TTL

    def serialize_data(self):
        """ Serialize header and payload into JSON """
        header = {
            "Creation Date": self.creation_date.isoformat(),
            "TTL": str(self.ttl)
        }
        payload = {
            "Application ID": self.application_id
        }
        header_json = json.dumps(header, sort_keys=True)
        payload_json = json.dumps(payload, sort_keys=True)
        return header_json, payload_json

    def encode_token(self):
        """ Encode the header, payload and signature into a Base64 string """
        header_json, payload_json = self.serialize_data()
        cryptoModule = CryptoModule()
        signature = cryptoModule.calculate_hmac((header_json + payload_json).encode())
        token = f"{header_json}.{payload_json}.{signature}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()
        return encoded_token

    def create_token(self):
        """ Generate a complete token """
        return self.encode_token()

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac, hashes
import base64
import os
#from ..settings import VARS

class CryptoModule:
    def __init__(self):
        """ Initialize the module with AES key, HMAC key, and IV from environment variables """
        try:
            #self.aes_key = base64.urlsafe_b64decode(VARS["AES_KEY"])
            #self.hmac_key = base64.urlsafe_b64decode(VARS["HMAC_KEY"])
            #self.iv = base64.urlsafe_b64decode(VARS["IV"])
            self.aes_key = base64.urlsafe_b64decode(os.getenv("AES_KEY"))
            self.hmac_key = base64.urlsafe_b64decode(os.getenv("HMAC_KEY"))
            self.iv = base64.urlsafe_b64decode(os.getenv("IV"))
        except TypeError as e:
            raise ValueError("Environment variables for keys and IV are not properly set.") from e

    def encrypt_data(self, data):
        """ Encrypt data using AES CBC mode with PKCS7 padding """
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decrypt_data(self, encrypted_data):
        """ Decrypt data using AES CBC mode with PKCS7 padding """
        encrypted_data = base64.urlsafe_b64decode(encrypted_data)
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.iv), backend=backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data.decode('utf-8')

    def calculate_hmac(self, data):
        """ Calculate HMAC for the provided data """
        h = hmac.HMAC(self.hmac_key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return base64.urlsafe_b64encode(h.finalize()).decode('utf-8')

# Example usage within a Django view or a model
def generate_token():
    application_id = 'your_application_id_here'  # This should be dynamically determined based on context
    token_generator = SessionModule(application_id)
    token = token_generator.create_token()
    return token

print(generate_token())