import requests
import json

# Replace with your APIC credentials and URL
apic_url = "https://your-apic-url"
username = "your-username"
password = "your-password"

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Function to log in and get a session token
def login():
    login_url = f"{apic_url}/api/aaaLogin.json"
    login_payload = {
        "aaaUser": {
            "attributes": {
                "name": username,
                "pwd": password
            }
        }
    }
    response = requests.post(login_url, json=login_payload, verify=False)
    response.raise_for_status()
    token = response.json()['imdata'][0]['aaaLogin']['attributes']['token']
    cookies = {'APIC-cookie': token}
    return cookies

# Function to get unused interface policies
def get_unused_interface_policies(cookies):
    policies_url = f"{apic_url}/api/node/class/infraAccPortP.json"
    response = requests.get(policies_url, cookies=cookies, verify=False)
    policies = response.json()['imdata']
    unused_policies = []
    
    for policy in policies:
        policy_dn = policy['infraAccPortP']['attributes']['dn']
        usage_url = f"{apic_url}/api/node/class/infraRsAccBaseGrp.json?query-target-filter=eq(infraRsAccBaseGrp.tDn,\"{policy_dn}\")"
        usage_response = requests.get(usage_url, cookies=cookies, verify=False)
        if not usage_response.json()['imdata']:
            unused_policies.append(policy_dn)
    return unused_policies

# Function to get unused QoS policies
def get_unused_qos_policies(cookies):
    qos_url = f"{apic_url}/api/node/class/qosInstPol.json"
    response = requests.get(qos_url, cookies=cookies, verify=False)
    policies = response.json()['imdata']
    unused_policies = []
    
    for policy in policies:
        policy_dn = policy['qosInstPol']['attributes']['dn']
        usage_url = f"{apic_url}/api/node/class/infraRsQosP.json?query-target-filter=eq(infraRsQosP.tDn,\"{policy_dn}\")"
        usage_response = requests.get(usage_url, cookies=cookies, verify=False)
        if not usage_response.json()['imdata']:
            unused_policies.append(policy_dn)
    return unused_policies

# Function to get unused bridge domains
def get_unused_bridge_domains(cookies):
    bd_url = f"{apic_url}/api/node/class/fvBD.json"
    response = requests.get(bd_url, cookies=cookies, verify=False)
    bridge_domains = response.json()['imdata']
    unused_bds = []
    
    for bd in bridge_domains:
        bd_dn = bd['fvBD']['attributes']['dn']
        usage_url = f"{apic_url}/api/node/class/fvRsCtx.json?query-target-filter=eq(fvRsCtx.tDn,\"{bd_dn}\")"
        usage_response = requests.get(usage_url, cookies=cookies, verify=False)
        if not usage_response.json()['imdata']:
            unused_bds.append(bd_dn)
    return unused_bds

# Function to get unused contracts
def get_unused_contracts(cookies):
    contract_url = f"{apic_url}/api/node/class/vzBrCP.json"
    response = requests.get(contract_url, cookies=cookies, verify=False)
    contracts = response.json()['imdata']
    unused_contracts = []
    
    for contract in contracts:
        contract_dn = contract['vzBrCP']['attributes']['dn']
        usage_url = f"{apic_url}/api/node/class/fvRsProv.json?query-target-filter=eq(fvRsProv.tDn,\"{contract_dn}\")"
        usage_response = requests.get(usage_url, cookies=cookies, verify=False)
        if not usage_response.json()['imdata']:
            unused_contracts.append(contract_dn)
    return unused_contracts

# Function to detect all unused policies category-wise
def detect_all_unused_policies(cookies):
    unused_policies = {
        "Unused Interface Policies": get_unused_interface_policies(cookies),
        "Unused QoS Policies": get_unused_qos_policies(cookies),
        "Unused Bridge Domains": get_unused_bridge_domains(cookies),
        "Unused Contracts": get_unused_contracts(cookies)
    }
    
    return unused_policies

def main():
    cookies = login()
    unused_policies = detect_all_unused_policies(cookies)
    
    print("Unused Policies Category-wise:")
    for category, policies in unused_policies.items():
        if policies:
            print(f"\n{category}:")
            for policy in policies:
                print(policy)
        else:
            print(f"\nNo unused policies found for {category}.")

if __name__ == "__main__":
    main()
