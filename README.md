# Sprint 3 Final

## Overview
This document outlines the steps for deploying Sprint 3 Final using Python 3.12

## Deployment Instructions

### Step 1: Set Up Your GCP Project
Before you begin, you need to create a Google Cloud Platform (GCP) project if you don't already have one. This project will house all the resources required for our application.

- **Create a Project:**
  - Go to the [Google Cloud Console](https://console.cloud.google.com/).
  - Click on the project dropdown near the top of the dashboard.
  - Click on ‘New Project’ and follow the prompts to create a new project.

### Step 2: Configure Keyring and Keys
After setting up your GCP project, configure a keyring and encryption keys within Google Cloud Key Management Service (KMS) to handle encryption operations securely.

- **Create a Keyring:**
  - Navigate to the [KMS section](https://console.cloud.google.com/security/kms) in the Google Cloud Console.
  - Select your project.
  - Click ‘Create Keyring’ and provide a name and location for the keyring.

- **Create Encryption Key for Symmetric Encryption:**
  - With the keyring selected, click ‘Create Key’.
  - Choose a purpose (e.g., Symmetric Encrypt/Decrypt).
  - Configure the key with the following specifications:
    - Algorithm: AES-256
    - Mode: CBC
    - Padding: PKCS5Padding
    - Key length: 256 bits
    - Rotation period and starting time as per your security compliance requirements.

- **Create IV for Symmetric Encryption:**
  - Randomly-securely generated 16-byte vector

- **Create a Key for HMAC Calculation:**
  - Still within the same keyring, create another key for HMAC calculations.
  - Configure the key as follows:
    - Algorithm: HMAC-SHA256
    - Key length: 256 bits

- **Set Permissions:**
  - Assign roles to your project members to control access to the keyring and keys.
  - Use roles such as `roles/cloudkms.cryptoKeyEncrypterDecrypter` to give necessary permissions for handling encryption and decryption operations.

### Step 3: Integrate with User Manager
Ensure that your `user_manager` component is properly configured to fetch encryption keys from KMS and to manage encryption, decryption, and HMAC calculations effectively.

- **Update Configuration Files:**
  - Edit your configuration files to include references to your GCP project, keyring, keys, and IV specifications.
  - Ensure your application’s IAM policies include permissions for accessing KMS.

### Step 4: Download and Configure Templates
- Download the necessary templates:
    ```bash
    wget --no-cache https://raw.githubusercontent.com/arquisoft-genesis-202401/sprint-3-final/main/set_env_vars.sh.template
    wget --no-cache https://raw.githubusercontent.com/arquisoft-genesis-202401/sprint-3-final/main/deployment.yaml.template
    ```

- Update `set_env_vars.sh.template` with the real values and save it as `set_env_vars.sh`.

- Grant execution permission to the script:
    ```bash
    chmod +x set_env_vars.sh
    ```

- Source the environment variables:
    ```bash
    source set_env_vars.sh
    ```

### Step 5: Create and Manage Deployment
- Create the deployment using `gcloud deployment-manager`:
    ```bash
    gcloud deployment-manager deployments create sprint-3-final-deployment --config deployment.yaml
    ```

- To delete the deployment, run:
    ```bash
    gcloud deployment-manager deployments delete sprint-3-final-deployment
    ```

- To update the deployment configuration, use:
    ```bash
    gcloud deployment-manager deployments update sprint-3-final-deployment --config deployment.yaml
    ```

## Additional Steps (Optional)
- View startup logs using:
    ```bash
    sudo journalctl -u google-startup-scripts.service
    ```
- Log in into the business database:
    ```bash
    psql -U <db_user> -d <db_name> --password
    ```
