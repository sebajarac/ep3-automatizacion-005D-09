#!/usr/bin/env python3
import os
import datetime
import yaml
import requests
import json

# Desactivar advertencias de certificados SSL autofirmados
requests.packages.urllib3.disable_warnings()

# 1. Metadatos de ejecución
print("=== VALIDACIÓN RESTCONF ===")
print(f"Script: {os.path.basename(__file__)}")
print(f"Fecha/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Host VM: {os.uname()[1]}")
print("==========================\n")

# 2. Cargar variables desde el archivo YAML
with open("../vars/vars_005D-09.yaml", "r") as f:
    vars_data = yaml.safe_load(f)

# Valores esperados
expected_hostname = vars_data['cliente']['hostname']
expected_loopback_ip = vars_data['router']['loopback_ip']
expected_descripcion_wan = vars_data['router']['descripcion_wan']
expected_ntp_server = vars_data['router']['ntp_server']

router_ip = vars_data['router']['ip']
auth = (vars_data['router']['usuario'], vars_data['router']['password'])
headers = {"Accept": "application/yang-data+json"}

base_url = f"https://{router_ip}/restconf/data"

# 3. Endpoints a consultar y archivos de salida
endpoints = {
    "hostname": (f"{base_url}/Cisco-IOS-XE-native:native/hostname", "evidencias/responses/get_hostname.json"),
    "loopback": (f"{base_url}/ietf-interfaces:interfaces/interface=Loopback10", "evidencias/responses/get_loopback.json"),
    "interface": (f"{base_url}/ietf-interfaces:interfaces/interface=GigabitEthernet1", "evidencias/responses/get_interfaces.json"),
    "ntp": (f"{base_url}/Cisco-IOS-XE-native:native/ntp", "evidencias/responses/get_ntp.json")
}

responses_data = {}

# Ejecutar las consultas GET
for key, (url, path) in endpoints.items():
    try:
        response = requests.get(url, auth=auth, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            responses_data[key] = data
            with open(path, "w") as jf:
                json.dump(data, jf, indent=2)
        else:
            responses_data[key] = None
    except Exception as e:
        responses_data[key] = None

# 4. Extraer valores reales para la comparación
try:
    real_hostname = responses_data['hostname']['Cisco-IOS-XE-native:hostname']
except: real_hostname = "NOT FOUND"

try:
    real_loopback_ip = responses_data['loopback']['ietf-interfaces:interface']['ietf-ip:ipv4']['address'][0]['ip']
except: real_loopback_ip = "NOT FOUND"

try:
    real_descripcion_wan = responses_data['interface']['ietf-interfaces:interface']['description']
except: real_descripcion_wan = "NOT FOUND"

try:
    # Búsqueda flexible en el JSON de NTP
    ntp_str = json.dumps(responses_data.get('ntp', {}))
    real_ntp_server = expected_ntp_server if expected_ntp_server in ntp_str else "NOT FOUND"
except: real_ntp_server = "NOT FOUND"

# 5. Comparación de criterios
criterios = [
    ("Hostname corporativo", expected_hostname, real_hostname),
    ("IP del Loopback", expected_loopback_ip, real_loopback_ip),
    ("Descripcion WAN", expected_descripcion_wan, real_descripcion_wan),
    ("Servidor NTP", expected_ntp_server, real_ntp_server)
]

ok_count = 0
for desc, exp, real in criterios:
    if exp == real:
        print(f"[OK] {desc}: Esperado='{exp}', Real='{real}'")
        ok_count += 1
    else:
        print(f"[FAIL] {desc}: Esperado='{exp}', Real='{real}'")

print("\n==============================")
if ok_count == 4:
    print(f"Resultado global: CONFORME ({ok_count}/4 OK)")
else:
    print(f"Resultado global: NO CONFORME ({ok_count}/4 OK)")
print("==============================")
