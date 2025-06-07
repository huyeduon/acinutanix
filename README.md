# Pre-requisite

- vapic ova exists on Nutanix cluster
- OOB subnet and Infra subnet

# Install Python environment

pip install -r requirements.txt

# Prepare .env file

Setup .env file with below format

- baseUrl=https://10.68.39.237:9440/api/nutanix/v3/
- username=prism_central_admin
- password=prism_central_password
- pc=prism_central_IP_address
- apic_detailed_version=aci-apic-dk9.6.1.3.186_nutanix
- cluster_name=nutanix_cluster_name
- vapic_oob_subnet=oob_subet_name
- vapic_infra_subnet=infra_subnet_name

# How to run the script

- For example, create a vpic name "vapic-test1" with profile small
- python create_vapic.py --name vapic-test1 --size small
