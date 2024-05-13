import json
import base64
from datetime import datetime, timedelta
from django.conf import settings
from .crypto_module import CryptoModule

class SessionModule:
    def __init__(self, application_id):
        self.application_id = application_id
        self.creation_date = datetime.utcnow()
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
        signature = CryptoModule.calculate_hmac(header_json + payload_json)
        token = f"{header_json}.{payload_json}.{signature}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()
        return encoded_token

    def create_token(self):
        """ Generate a complete token """
        return self.encode_token()

# Example usage within a Django view or a model
def generate_token():
    application_id = 'your_application_id_here'  # This should be dynamically determined based on context
    token_generator = SessionModule(application_id)
    token = token_generator.create_token()
    return token

print(generate_token())