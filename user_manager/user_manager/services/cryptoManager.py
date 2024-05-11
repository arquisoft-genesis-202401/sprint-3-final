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

    def get_key_from_kms(self, file_path):
        # Request the key from KMS
        key_version = self.client.crypto_key_version_path(
            self.project_id, self.location_id, self.key_ring_id, self.crypto_key_id, '1')  # Assuming '1' is the key version
        ciphertext = self.read_binary_file(file_path)
        response = self.client.asymmetric_decrypt(
            request={
                "name": key_version,
                "ciphertext": ciphertext  # The ciphertext would be your wrapped key
            }
        )
        # The decrypted response contains the plaintext key
        return response.plaintext

    def encrypt_data_aes(self, data):
        key = self.get_key_from_kms("wrapped_aes_key.bin")
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_data

    def decrypt_data_aes(self, encrypted_data):
        key = self.get_key_from_kms("wrapped_aes_key.bin")
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv), backend=backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    def calculate_hmac(self, data):
        key = self.get_key_from_kms("wrapped_hmac_key.bin")
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return h.finalize()
    
    def read_binary_file(file_path):
        try:
            # Open the file in binary read mode
            with open(file_path, 'rb') as file:
                binary_data = file.read()
                return binary_data
        except IOError as e:
            print(f"An error occurred while reading the file: {e}")
            return None

# Usage Example:
crypto_manager = CryptoManager()
encrypted_data = crypto_manager.encrypt_data_aes(b'example data')
print(encrypted_data)
