from django.db import transaction
from ..models import Customer, Application, ApplicationStatus, BasicInformation
from django.utils import timezone
from ..modules.crypto_module import CryptoModule

@transaction.atomic
def create_customer_application_basic_info(
    document_type: str, document_number: str, first_name: str, last_name: str,
    country: str, state: str, city: str, address: str, mobile_number: str, email: str
) -> int:
    customer, _ = get_or_create_customer(document_type, document_number)
    status = get_or_create_application_status()
    application = create_application(customer, status)
    encrypted_fields = encrypt_and_store_fields(
        first_name, last_name, country, state, city, address, mobile_number, email
    )
    store_basic_information(application, encrypted_fields)
    return application.pk

def get_or_create_customer(document_type: str, document_number: str):
    return Customer.objects.get_or_create(
        DocumentType=document_type,
        DocumentNumber=document_number,
        defaults={'DocumentType': document_type, 'DocumentNumber': document_number}
    )

def get_or_create_application_status():
    return ApplicationStatus.objects.get_or_create(
        StatusDescription='BasicInfo',
        defaults={'StatusDescription': 'BasicInfo', 'CreationDate': now(), 'ModificationDate': now()}
    )

def create_application(customer, status):
    return Application.objects.create(
        CustomerID=customer,
        StatusID=status,
        CreationDate=now(),
        ModificationDate=now()
    )

def encrypt_and_store_fields(*fields: str):
    crypto = CryptoModule()
    encrypted_fields = {}
    field_names = ['FirstName', 'LastName', 'Country', 'State', 'City', 'Address', 'MobileNumber', 'Email']

    for field, name in zip(fields, field_names):
        encoded_field = field.encode('utf-8')
        encrypted_fields[name] = encrypt_and_hash_field(crypto, encoded_field)

    return encrypted_fields

def encrypt_and_hash_field(crypto, data):
    encrypted_data = crypto.encrypt_data(data)
    data_hmac = crypto.calculate_hmac(data)
    return encrypted_data + ";" + data_hmac

def store_basic_information(application, encrypted_fields):
    return BasicInformation.objects.create(
        ApplicationID=application,
        **encrypted_fields,
        CreationDate=now(),
        ModificationDate=now()
    )

def now():
    return timezone.now()


@transaction.atomic
def update_customer_application_basic_info(application_id, first_name, last_name, country, state, city, address, mobile_number, email):
    # Check if the application exists and belongs to this customer
    try:
        application = Application.objects.get(pk=application_id)
    except Application.DoesNotExist:
        return "Application not found for this customer."

    # Find the BasicInformation linked to the application
    try:
        basic_information = BasicInformation.objects.get(ApplicationID=application)
    except BasicInformation.DoesNotExist:
        return "Basic Information not found for this application."

    # Initialize the cryptography module
    crypto = CryptoModule()

    # Encrypt and store each field individually with HMAC
    fields = [first_name, last_name, country, state, city, address, mobile_number, email]
    field_names = ['FirstName', 'LastName', 'Country', 'State', 'City', 'Address', 'MobileNumber', 'Email']

    for index, field in enumerate(fields):
        data_to_encrypt = field.encode('utf-8')
        encrypted_data = crypto.encrypt_data(data_to_encrypt)
        data_hmac = crypto.calculate_hmac(data_to_encrypt)
        encrypted_field = encrypted_data + ";" + data_hmac
        setattr(basic_information, field_names[index], encrypted_field)

    # Update modification date and save the changes
    basic_information.ModificationDate = timezone.now()
    basic_information.save()

    return application_id

def get_basic_information_by_application_id(application_id):
    try:
        # Retrieve the BasicInformation associated with the given Application ID
        basic_info = BasicInformation.objects.get(ApplicationID__id=application_id)
        crypto = CryptoModule()

        # Decrypt and verify each encrypted field
        fields = ['FirstName', 'LastName', 'Country', 'State', 'City', 'Address', 'MobileNumber', 'Email']
        decrypted_info = {}
        
        for field in fields:
            encrypted_data_hmac = getattr(basic_info, field)
            encrypted_data, stored_hmac = encrypted_data_hmac.split(';')

            # Decrypt the data
            decrypted_data = crypto.decrypt_data(encrypted_data)

            # Calculate HMAC of the decrypted data and compare with stored HMAC
            calculated_hmac = crypto.calculate_hmac(decrypted_data.encode())
            if calculated_hmac != stored_hmac:
                return {"error": f"Integrity check failed for {field}"}

            decrypted_info[field.lower()] = decrypted_data

        return decrypted_info

    except BasicInformation.DoesNotExist:
        # Return an error dictionary if no BasicInformation is found for the given Application ID
        return {"error": "BasicInformation not found for the provided Application ID"}