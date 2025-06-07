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

def list_vms(api_client):
    """Lists VMs and prints their information."""
    vm_api = ntnx_vmm_py_client.VmApi(api_client=api_client)
    try:
        api_response = vm_api.list_vms(_page=0, _limit=50)
        vm_data = api_response.data
        
        for vm in vm_data:
            vm_name = vm.name if hasattr(vm, 'name') else 'Unknown Name'
            ip_addresses = []
            for nic in vm.nics if hasattr(vm, 'nics') else []:
                if hasattr(nic, 'network_info') and hasattr(nic.network_info, 'ipv4_info') and nic.network_info.ipv4_info is not None:
                    learned_ips = nic.network_info.ipv4_info.learned_ip_addresses
                    for ip_data in learned_ips:
                        ip_address = ip_data.value if hasattr(ip_data, 'value') else 'Unknown IP'
                        ip_addresses.append(ip_address)

            print(f'VM Name: {vm_name}, IP Addresses: {", ".join(ip_addresses)}')

    except ntnx_vmm_py_client.rest.ApiException as e:
        print(f"Error fetching VMs: {e}")

def main():
    api_client = configure_client()
    list_vms(api_client)

if __name__ == "__main__":
    main()