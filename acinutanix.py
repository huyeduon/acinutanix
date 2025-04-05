from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import os
import pprint

from base64 import b64encode

# Load environment variables from .env file
load_dotenv()

baseUrl = os.getenv('baseUrl')
username = os.getenv('username')
password = os.getenv('password')
print(baseUrl)

url = baseUrl + '/vmm/v4.0/ahv/config/vms'

def get_session_cookies(auth_url, username, password):
    """
    Authenticate with the server and return session cookies.
    
    :param auth_url: The URL to send the authentication request to.
    :param username: The username for authentication.
    :param password: The password for authentication.
    :return: A dictionary of session cookies.
    """
    response = requests.get(auth_url, auth=HTTPBasicAuth(username, password), verify=False)
    
    if response.status_code == 200:
        print("Authenticated successfully!")
        return response.cookies.get_dict()
    else:
        print(f"Authentication failed. Status code: {response.status_code}")
        print(response.text)
        return None

cookies = get_session_cookies(url, username, password)

#print(cookies), cookies function is not used yet, just for reference

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
request_url = f'{baseUrl}/vmm/v4.0/ahv/config/vms'
encoded_credentials = b64encode(bytes(f'{username}:{password}',
encoding='ascii')).decode('ascii')

auth_header = f'Basic {encoded_credentials}'
payload =  {}

headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
'Authorization': f'{auth_header}', 'cache-control': 'no-cache'}

response = requests.request('get', request_url, data=payload, headers=headers,
verify=False)

print("=========================================")

if response.status_code == 200:
    # Convert JSON string to Python object (usually a dictionary)
    data = response.json()['data']
else:
    print("Failed to retrieve data:", response.status_code)



# Print the header with fixed width
header_vm_name = "VM Name".ljust(20)
header_ip_address = "IP Address".ljust(40)
print(f"{header_vm_name} | {header_ip_address}")

# Print separator line
print("-" * (20 + 42))  # 20 + 40 + 2 for separator spaces

# Iterate over the list of VMs and print the required information
for vm in data:
    name = vm.get("name", "Unknown Name")
    ip_addresses = []
    for nic in vm.get("nics", []):
        ipv4_info = nic.get("networkInfo", {}).get("ipv4Info", {})
        learned_ips = ipv4_info.get("learnedIpAddresses", [])
        for ip_data in learned_ips:
            ip_address = ip_data.get("value", "Unknown IP")
            ip_addresses.append(ip_address)
    
    # Print VM name and IP addresses with fixed width
    vm_name = name.ljust(20)
    ips = ", ".join(ip_addresses).ljust(40)
    print(f"{vm_name} | {ips}")