import requests
import json

# Replace with your APIC credentials and URL
apic_url = "https://172.16.100.75"
username = "vector"
password = "Vector@123"

# Disable warnings for unverified HTTPS requests
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

# Function to get all EPGs
def get_epgs(cookies):
    epg_url = f"{apic_url}/api/node/class/fvAEPg.json"
    response = requests.get(epg_url, cookies=cookies, verify=False)
    response.raise_for_status()
    epgs = response.json()['imdata']
    return epgs

# Function to get endpoints associated with an EPG
def get_endpoints(cookies, dn):
    endpoint_url = f"{apic_url}/api/node/class/fvRsCEpToPathEp.json?query-target-filter=eq(fvRsCEpToPathEp.tDn,\"{dn}\")"
    response = requests.get(endpoint_url, cookies=cookies, verify=False)
    response.raise_for_status()
    endpoints = response.json()['imdata']
    return endpoints

# Function to detect unused EPGs
def detect_unused_epgs(epgs, cookies):
    unused_epgs = []
    for epg in epgs:
        epg_dn = epg['fvAEPg']['attributes']['dn']
        endpoints = get_endpoints(cookies, epg_dn)
        if not endpoints:
            unused_epgs.append(epg_dn)
    return unused_epgs

def main():
    cookies = login()
    epgs = get_epgs(cookies)
    unused_epgs = detect_unused_epgs(epgs, cookies)
    
    if unused_epgs:
        print("Unused EPGs detected:")
        for epg in unused_epgs:
            print(epg)
    else:
        print("No unused EPGs found.")

if __name__ == "__main__":
    main()
