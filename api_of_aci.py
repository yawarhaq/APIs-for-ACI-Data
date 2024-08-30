import requests
import json

APIC_IP = "https://172.16.100.75"
USERNAME = "vector"
PASSWORD = "Vector@123"

def get_apic_token(apic_ip, username, password):
    url = f"{apic_ip}/api/aaaLogin.json"
    payload = {
        "aaaUser": {
            "attributes": {
                "name": username,
                "pwd": password
            }
        }
    }

    response = requests.post(url, json=payload, verify=False)
    if response.status_code == 200:
        token = response.json()['imdata'][0]['aaaLogin']['attributes']['token']
        print("Successfully authenticated. Token obtained.")
        return token
    else:
        print(f"Failed to authenticate. Status code: {response.status_code}")
        return None
    
def fetch_data(url, token):
    headers = {
        "Cookie": f"APIC-cookie={token}"
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

def collect_data(apic_ip, token):
    data = {}
    data['apic_health'] = fetch_data(f"{apic_ip}/api/node/class/compCtrlr.json", token)
    data['fabric_health'] = fetch_data(f"{apic_ip}/api/node/class/fabricNode.json", token)
    data['node_utilization'] = fetch_data(f"{apic_ip}/api/node/class/topSystem.json", token)
    data['link_status'] = fetch_data(f"{apic_ip}/api/node/class/ethpmPhysIf.json", token)
    return data

token = get_apic_token(APIC_IP, USERNAME, PASSWORD)
data = collect_data(APIC_IP, token)

print("Api token:", token)

# Save data to a JSON file for later use
with open('aci_health_data.json', 'w') as f:
    json.dump(data, f, indent=2)