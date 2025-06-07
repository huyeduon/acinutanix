from dotenv import load_dotenv
import os
import requests
import json
import urllib3
import time
import argparse
from base64 import b64encode

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)  # Force load .env from the v3 folder

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


def get_cluster_uuid(cluster_name, baseUrl):
    cluster_url = baseUrl + "clusters/list"
    payload = {"kind": "cluster"}
    json_payload = json.dumps(payload)
    response = requests.request("POST", cluster_url, data=json_payload, headers=headers,
                                verify=False,
                                timeout=1)

    response_dict = json.loads(response.text)
    entities = response_dict.get("entities", [])
    for entity in entities:
        if cluster_name.strip() in entity.get("status", {}).get("name", ""):
            return entity["metadata"]["uuid"]


def get_subnet_uuid(subnet, baseUrl):
    url = baseUrl + "subnets/list"
    payload = {"kind": "subnet"}
    json_payload = json.dumps(payload)
    response = requests.request("POST", url, data=json_payload, headers=headers,
                                verify=False,
                                timeout=1)

    response_dict = json.loads(response.text)
    entities = response_dict.get("entities", [])
    for entity in entities:
        if subnet.strip() in entity.get("status", {}).get("name", ""):
            return entity["metadata"]["uuid"]


def create_vm_spec(ova_file_name, vm_name, oob_subnet, infra_subnet, baseUrl):
    ova_uuid = get_ova_uuid(ova_file_name, baseUrl)
    vm_spec_url = baseUrl + "ovas/" + ova_uuid + "/vm_spec"
    response = requests.request("GET", vm_spec_url, data={}, headers=headers,
                                verify=False,
                                timeout=1)

    original_response = json.loads(response.text)
    oob_subnet_uuid = get_subnet_uuid(oob_subnet, baseUrl)
    infra_subnet_uuid = get_subnet_uuid(infra_subnet, baseUrl)
    subnet_uuids = [oob_subnet_uuid, infra_subnet_uuid]

    nic_list = original_response["vm_spec"]["spec"]["resources"]["nic_list"]
    for i, nic in enumerate(nic_list):
        if i < len(subnet_uuids):
            nic["subnet_reference"]["uuid"] = subnet_uuids[i]

    new_json = {
        "metadata": original_response["vm_spec"]["metadata"],
        "spec": {
            "cluster_reference": original_response["vm_spec"]["spec"]["cluster_reference"],
            "name": vm_name,
            "resources": original_response["vm_spec"]["spec"]["resources"]
        }
    }
    return json.dumps(new_json, indent=2)


def create_vapic(vm_spec, baseUrl):
    url = baseUrl + "vms"
    requests.request("POST", url, data=vm_spec, headers=headers,
                     verify=False,
                     timeout=1)


def main():
    parser = argparse.ArgumentParser(description="Create virtual APIC on Nutanix Cluster.")
    parser.add_argument("--name", type=str, required=True, help="Virtual APIC VM name.")
    args = parser.parse_args()
    vapic_name = args.name

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

    vm_spec = create_vm_spec(apic_detailed_version, vapic_name, vapic_oob_subnet, vapic_infra_subnet, baseUrl)
    time.sleep(2)

    create_vapic(vm_spec, baseUrl)
    print(f"Virtual APIC '{vapic_name}' has been created successfully!")


if __name__ == '__main__':
    main()