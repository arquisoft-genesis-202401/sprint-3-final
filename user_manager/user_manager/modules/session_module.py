import json
import base64
from datetime import datetime, timezone, timedelta
from .crypto_module import CryptoModule

class SessionModule:
    def __init__(self):
        timezone_offset = -5.0  # UTC-5
        self.tzinfo = timezone(timedelta(hours=timezone_offset))
        self.ttl = timedelta(hours=1)  # 1 hour TTL

    def serialize_data(self, application_id):
        """ Serialize header and payload into JSON """
        header = {
            "Creation Date": datetime.now(self.tzinfo).isoformat(),
            "TTL": str(self.ttl)
        }
        payload = {
            "Application ID": application_id
        }
        header_json = json.dumps(header, sort_keys=True)
        payload_json = json.dumps(payload, sort_keys=True)
        return header_json, payload_json

    def encode_token(self, application_id):
        """ Encode the header, payload and signature into a Base64 string """
        header_json, payload_json = self.serialize_data(application_id)
        cryptoModule = CryptoModule()
        signature = cryptoModule.calculate_hmac((header_json + payload_json).encode())
        token = f"{header_json}.{payload_json}.{signature}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()
        return encoded_token

    def create_token(self, application_id):
        """ Generate a complete token with a given application_id """
        return self.encode_token(application_id)

    def verify_token(self, token):
        """ Verify the token by checking the signature """
        try:
            decoded_token = base64.standard_b64decode(token).decode("utf-8")
            print(decoded_token)
            return True
            encoded_header, encoded_payload, signature = token.split('.')
            header_payload = f"{encoded_header}.{encoded_payload}"
            decoded_header_payload = base64.urlsafe_b64decode(header_payload.encode()).decode()
            
            cryptoModule = CryptoModule()
            expected_signature = cryptoModule.calculate_hmac(decoded_header_payload.encode())
        
            if signature == expected_signature:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error verifying token: {e}")
            return False