from dotenv import load_dotenv
import os
import requests
import json
import urllib3
import time
import argparse
from base64 import b64encode

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

baseUrl = os.getenv("baseUrl")
cluster_password = os.getenv("password")
username = os.getenv("username")
apic_detailed_version = os.getenv("apic_detailed_version", "").strip()
cluster_name = os.getenv("cluster_name").strip()
vapic_oob_subnet = os.getenv("vapic_oob_subnet").strip()
vapic_infra_subnet = os.getenv("vapic_infra_subnet").strip()
encoded_credentials = b64encode(bytes(f"{username}:{cluster_password}", encoding="ascii")).decode("ascii")
auth_header = f'Basic {encoded_credentials}'
headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': f"{auth_header}",
    'cache-control': "no-cache"
}

# Retrieve uuid of virtual apic ova
def get_ova_uuid(ova_file_name, baseUrl):
    try:
        payload = {
        "kind": "ova"
        }
        json_payload = json.dumps(payload)
        url = baseUrl + 'ovas/list'
        response = requests.request("POST", url, data=json_payload, headers=headers,
                                verify=False,
                                timeout=1)

        if response.ok:
            response_dict = json.loads(response.text)
            entities = response_dict.get("entities", [])

        for entity in entities:
            if ova_file_name.strip() in entity.get("info", {}).get("name", ""):
                return entity["metadata"]["uuid"]
            
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Please check your network or increase the timeout value.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: An HTTP error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Error: Missing key in the response: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_cluster_uuid(cluster_name, baseUrl):
    try: 
        cluster_url = baseUrl + "clusters/list"
        payload = {"kind": "cluster"}
        json_payload = json.dumps(payload)
        response = requests.request("POST", cluster_url, data=json_payload, headers=headers,
                                verify=False,
                                timeout=10)

        response_dict = json.loads(response.text)
        entities = response_dict.get("entities", [])
        for entity in entities:
            if cluster_name.strip() in entity.get("status", {}).get("name", ""):
                return entity["metadata"]["uuid"]
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Please check your network or increase the timeout value.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: An HTTP error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Error: Missing key in the response: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_subnet_uuid(subnet, baseUrl):
    try:
        url = baseUrl + "subnets/list"
        payload = {"kind": "subnet"}
        json_payload = json.dumps(payload)
        response = requests.request("POST", url, data=json_payload, headers=headers,
                                verify=False,
                                timeout=10)

        response_dict = json.loads(response.text)
        entities = response_dict.get("entities", [])
        for entity in entities:
            if subnet.strip() in entity.get("status", {}).get("name", ""):
                return entity["metadata"]["uuid"]
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Please check your network or increase the timeout value.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: An HTTP error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Error: Missing key in the response: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def create_vm_spec(ova_file_name, vm_name, vm_size, oob_subnet, infra_subnet, baseUrl):
    try:
        ova_uuid = get_ova_uuid(ova_file_name, baseUrl)
        vm_spec_url = baseUrl + "ovas/" + ova_uuid + "/vm_spec"

        response = requests.request("GET", vm_spec_url, data={}, headers=headers,
                                verify=False,
                                timeout=10)

        original_response = json.loads(response.text)
        oob_subnet_uuid = get_subnet_uuid(oob_subnet, baseUrl)
        infra_subnet_uuid = get_subnet_uuid(infra_subnet, baseUrl)
        subnet_uuids = [oob_subnet_uuid, infra_subnet_uuid]

        nic_list = original_response["vm_spec"]["spec"]["resources"]["nic_list"]
        for i, nic in enumerate(nic_list):
            if i < len(subnet_uuids):
                nic["subnet_reference"]["uuid"] = subnet_uuids[i]
    # Set num_sockets and memory_size_mib dynamically
    # Dynamically set num_sockets and memory_size_mib based on vm_size
    # Dynamically set num_sockets and memory_size_mib based on vm_size
        if vm_size == "small":
            num_sockets = 8
            memory_size_mib = 32768
        elif vm_size == "medium":
            num_sockets = 16
            memory_size_mib = 98304 
     
        else:
            raise ValueError(f"Invalid vm_size: {vm_size}")

 
        original_response["vm_spec"]["spec"]["resources"]["num_sockets"] = num_sockets
        original_response["vm_spec"]["spec"]["resources"]["memory_size_mib"] = memory_size_mib

        # Extract the desired parts of the JSON
        new_json = {
            "metadata": original_response["vm_spec"]["metadata"],
            "spec": {
                "cluster_reference": original_response["vm_spec"]["spec"]["cluster_reference"],
                "name": vm_name,
                "resources": original_response["vm_spec"]["spec"]["resources"]
            }
        }
        return json.dumps(new_json, indent=2)
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Please check your network or increase the timeout value.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: An HTTP error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Error: Missing key in the response: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def create_vapic(vm_spec, baseUrl):
    url = baseUrl + "vms"
    try:
        # Send the POST request to create the VM
        response = requests.request("POST", url, data=vm_spec, headers=headers, verify=False, timeout=10)

        # Handle API response errors
        if not response.ok:
            raise RuntimeError(f"Failed to create vAPIC. Status code: {response.status_code}, Response: {response.text}")

        print("vAPIC creation request successfully sent.")
        return response.json()  # Return the response as a JSON object if needed
    except requests.exceptions.Timeout:
        print("Error: The request to create vAPIC timed out. Please check your connection or increase the timeout value.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: An HTTP error occurred while creating vAPIC: {e}")
        return None
    except ValueError as e:
        print(f"Error: Invalid response format: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Create virtual APIC on Nutanix Cluster.")
    parser.add_argument("--name", type=str, required=True, help="Virtual APIC VM name.")
    parser.add_argument("--size", type=str, required=False, default="medium", choices=["small", "medium"], help="VM size: 'small' or 'medium' (default: medium).")
    args = parser.parse_args()
    vapic_name = args.name
    vm_size = args.size.lower()

    print("vAPIC OVA uuid:", end=" ")
    uuid = get_ova_uuid(apic_detailed_version, baseUrl)
    print(uuid)

    print("Cluster uuid:", end=" ")
    cluster_uuid = get_cluster_uuid(cluster_name, baseUrl)
    print(cluster_uuid)

    print("OOB Subnet uuid:", end=" ")
    oob_subnet_uuid = get_subnet_uuid(vapic_oob_subnet, baseUrl)
    print(oob_subnet_uuid)

    print("Infra Subnet uuid:", end=" ")
    infra_subnet_uuid = get_subnet_uuid(vapic_infra_subnet, baseUrl)
    print(infra_subnet_uuid)

    vm_spec = create_vm_spec(apic_detailed_version, vapic_name, vm_size, vapic_oob_subnet, vapic_infra_subnet, baseUrl)
    time.sleep(2)

    create_vapic(vm_spec, baseUrl)
    print(f"Virtual APIC '{vapic_name}' has been created successfully!")


if __name__ == '__main__':
    main()