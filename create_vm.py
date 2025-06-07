import os
from dotenv import load_dotenv
import ntnx_vmm_py_client
from ntnx_vmm_py_client.rest import ApiException

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

def create_vm_from_template(client):
    """Creates a VM from a specified template."""

    templates_api = ntnx_vmm_py_client.TemplatesApi(api_client=client)
    templateDeployment = ntnx_vmm_py_client.TemplateDeployment()

    # TemplateDeployment object initializations here...
    
    templateDeployment.cluster_reference = "0006308d-5eab-509d-5d96-8c44a538bb5c"  # required field
    templateDeployment.number_of_vms = 1  # required field
    ext_id = "a0ad2f9d-e257-4b7f-b9a2-4c650ac8b567"
  

    try:
        api_response = templates_api.deploy_template(extId=ext_id, body=templateDeployment)
        print(api_response)
    except ntnx_vmm_py_client.rest.ApiException as e:
        print(e)


def main():
    api_client = configure_client()
    create_vm_from_template(api_client)

if __name__ == "__main__":
    main()