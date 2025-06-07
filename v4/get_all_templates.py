#List VM in Nutanix cluster using v4 Python SDK

import urllib3
from dotenv import load_dotenv
import ntnx_vmm_py_client
import os

# Load environment variables
load_dotenv()

# Retrieve credentials from environment variables
pc_ip_address = os.getenv('pc')
pc_username = os.getenv('username')
pc_password = os.getenv('password')

def configure_client():
    """Configures and returns a Nutanix API client."""
    config = ntnx_vmm_py_client.Configuration()
    config.host = pc_ip_address
    config.port = 9440
    config.max_retry_attempts = 3
    config.backoff_factor = 3
    config.username = pc_username
    config.password = pc_password
    config.verify_ssl = False

    return ntnx_vmm_py_client.ApiClient(configuration=config)

def get_all_templates(client): 
    templates_api = ntnx_vmm_py_client.TemplatesApi(api_client=client)
    page = 0
    limit = 50
    try:
        api_response = templates_api.list_templates(_page=page, _limit=limit)
        print(api_response)
    except ntnx_vmm_py_client.rest.ApiException as e:
        print(e)

def main():
    api_client = configure_client()
    get_all_templates(api_client)

if __name__ == "__main__":
    main()