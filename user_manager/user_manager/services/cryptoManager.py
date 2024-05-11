import os
import base64
from google.cloud import kms
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac, hashes

class CryptoManager:
    def __init__(self):
        self.client = kms.KeyManagementServiceClient()
        self.project_id = os.getenv("PROJECT_ID")
        self.location_id = os.getenv("LOCATION_ID")
        self.key_ring_id = os.getenv("KEY_RING_ID")
        self.crypto_key_id = os.getenv("KEY_AES_ID")
        self.hmac_key_id = os.getenv("KEY_HMAC_ID")
        self.iv = base64.urlsafe_b64decode(os.getenv("IV"))
        self.crypto_key_path = self.client.crypto_key_path(self.project_id, self.location_id, self.key_ring_id, self.crypto_key_id)
        self.hmac_key_path = self.client.crypto_key_path(self.project_id, self.location_id, self.key_ring_id, self.hmac_key_id)

    def get_key_from_kms(self, key_path):
        """ Retrieve the key material from Google Cloud KMS """
        # Access the key version's resource name
        key_version = self.client.crypto_key_versions.list(parent=key_path).next()
        response = self.client.crypto_key_versions.get(name=key_version.name)
        return response.name, response.state

    def encrypt_data_aes(self, data):
        key, key_status = self.get_key_from_kms(self.crypto_key_path)
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_data

    def decrypt_data_aes(self, encrypted_data):
        key, key_status = self.get_key_from_kms(self.crypto_key_path)
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv), backend=backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    def calculate_hmac(self, data):
        key, key_status = self.get_key_from_kms(self.hmac_key_path)
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return h.finalize()

# Usage Example:
crypto_manager = CryptoManager()
encrypted_data = crypto_manager.encrypt_data_aes(b'example data')
print(encrypted_data)
