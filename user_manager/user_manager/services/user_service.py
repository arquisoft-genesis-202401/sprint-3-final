from django.db import transaction
from ..models import Customer, Application, ApplicationStatus, BasicInformation
from django.utils import timezone
from ..modules.crypto_module import CryptoModule

@transaction.atomic
def create_customer_application_service(document_type, document_number):
    # Check if the customer already exists
    customer, created = Customer.objects.get_or_create(
        DocumentType=document_type,
        DocumentNumber=document_number,
        defaults={'DocumentType': document_type, 'DocumentNumber': document_number}
    )

    # Get the predefined ApplicationStatus for "BasicInfo"
    status, status_created = ApplicationStatus.objects.get_or_create(
        StatusDescription='BasicInfo',
        defaults={'StatusDescription': 'BasicInfo', 'CreationDate': timezone.now(), 'ModificationDate': timezone.now()}
    )

    # Create an Application for this customer with the "BasicInfo" status
    application = Application.objects.create(
        CustomerID=customer,
        StatusID=status,
        CreationDate=timezone.now(),
        ModificationDate=timezone.now()
    )

    return application.id

@transaction.atomic
def create_update_application_basic_info_service(application_id, first_name, last_name, country, state, city, address, mobile_number, email):
    # Check if the application exists
    try:
        application = Application.objects.get(pk=application_id)
    except Application.DoesNotExist:
        return "Application not found for this customer."

    # Initialize the cryptography module
    crypto = CryptoModule()

    # Encrypt and store each field individually with HMAC
    fields = [first_name, last_name, country, state, city, address, mobile_number, email]
    field_names = ['FirstName', 'LastName', 'Country', 'State', 'City', 'Address', 'MobileNumber', 'Email']
    encrypted_data_dict = {}

    for index, field in enumerate(fields):
        data_to_encrypt = field.encode('utf-8')
        encrypted_data = crypto.encrypt_data(data_to_encrypt)
        data_hmac = crypto.calculate_hmac(data_to_encrypt)
        encrypted_field = encrypted_data + ";" + data_hmac
        encrypted_data_dict[field_names[index]] = encrypted_field

    # Find or create the BasicInformation linked to the application
    basic_information, created = BasicInformation.objects.get_or_create(
        ApplicationID=application,
        defaults={**encrypted_data_dict, 'CreationDate': timezone.now()}
    )

    # If the object was fetched, not created, update the data
    if not created:
        for key, value in encrypted_data_dict.items():
            setattr(basic_information, key, value)
        basic_information.ModificationDate = timezone.now()
        basic_information.save()

    return application_id

def get_basic_information_by_application_service(application_id):
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