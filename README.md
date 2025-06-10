# Introduction

The script helps to deploy Cisco Virtual APIC on Nutanix Cluster using rest API.

# Prerequisite

- Cisco Virtual APIC ova exists on Nutanix cluster
- OOB subnet and Infra subnet
- Nutanix Prism Central 2024.6.0.5 or above
- Nutanix AOS 6.10 or above

# Supported VM profile

The script supports 2 VM profiles

- vAPIC-Small: 8 vCPU, 32GB Memory
- vAPIC-Medium: 16 vCPU, 96GB Memory

For vAPIC-Large profile, please use Prism Central UI to deploy.

# Install Python environment

```python
pip install -r requirements.txt
```

# Prepare .env file

Create a .env file in the same folder with create_vapic.py using below format:

- baseUrl=https://ip_address_of_prism_central:9440/api/nutanix/v3/
- username=prism_central_admin
- password=prism_central_password
- pc=prism_central_IP_address
- apic_detailed_version=aci-apic-dk9.6.1.3.186_nutanix
- cluster_name=nutanix_cluster_name
- vapic_oob_subnet=oob_subet_name
- vapic_infra_subnet=infra_subnet_name

# How to run the script

- For example, create a vpic name "vapic-test1" with profile small

```python
python create_vapic.py --name vapic-test1 --size small
```
