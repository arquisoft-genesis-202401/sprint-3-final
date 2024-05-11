import os
from google.cloud import kms

class CryptoManager:
    def __init__(self):
        self.client = kms.KeyManagementServiceClient()
        self.project_id = os.getenv("PROJECT_ID")
        self.location_id = os.getenv("LOCATION_ID")
        self.key_ring_id = os.getenv("KEY_RING_ID")
        self.crypto_key_id = os.getenv("KEY_AES_ID")
        self.hmac_key_id = os.getenv("KEY_HMAC_ID")
        self.crypto_key_path = self.client.crypto_key_path(
            self.project_id, self.location_id, self.key_ring_id, self.crypto_key_id)
        self.hmac_key_path = self.client.crypto_key_path(
            self.project_id, self.location_id, self.key_ring_id, self.hmac_key_id)

    def encrypt_data(self, plaintext):
        plaintext_bytes = plaintext.encode('utf-8')
        response = self.client.encrypt(request={'name': self.crypto_key_path, 'plaintext': plaintext_bytes})
        return response.ciphertext

    def decrypt_data(self, ciphertext):
        response = self.client.decrypt(request={'name': self.crypto_key_path, 'ciphertext': ciphertext})
        return response.plaintext.decode('utf-8')

    def sign_data(self, data):
        # Convert data to bytes, if necessary
        data_bytes = data.encode('utf-8') if isinstance(data, str) else data
        # Sign the data
        response = self.client.mac_sign(request={'name': self.hmac_key_path, 'data': data_bytes})
        return response.mac

    def verify_signature(self, data, signature):
        # Convert data to bytes, if necessary
        data_bytes = data.encode('utf-8') if isinstance(data, str) else data
        # Verify the signature
        response = self.client.mac_verify(request={'name': self.hmac_key_path, 'data': data_bytes, 'mac': signature})
        return response.success  # Will be True if verification is successful

cm = CryptoManager()
ed = cm.encrypt_data("hola :)")
dd = cm.decrypt_data(ed)
print(ed)
print(dd)