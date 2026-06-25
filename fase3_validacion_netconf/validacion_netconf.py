k#!/usr/bin/env python3
import os
import datetime
import yaml
from lxml import etree
from ncclient import manager

# 1. Metadatos de ejecución
print("=== VALIDACIÓN NETCONF ===")
print(f"Script: {os.path.basename(__file__)}")
print(f"Fecha/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Host VM: {os.uname()[1]}")
print("==========================\n")

# 2. Cargar variables desde el archivo YAML
with open("../vars/vars_005D-09.yaml", "r") as f:
    vars_data = yaml.safe_load(f)

# Extraer valores esperados
expected_hostname = vars_data['cliente']['hostname']
expected_loopback_ip = vars_data['router']['loopback_ip']
expected_loopback_mask = vars_data['router']['loopback_mask']
expected_descripcion_wan = vars_data['router']['descripcion_wan']
expected_ntp_server = vars_data['router']['ntp_server']

# 3. Conexión NETCONF al router
router_info = vars_data['router']
try:
    with manager.connect(
        host=router_info['ip'],
        port=830,
        username=router_info['usuario'],
        password=router_info['password'],
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False
    ) as m:
        
        # Filtro XML amplio para traer la configuración nativa completa
        xml_filter = """
        <filter>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
          </native>
        </filter>
        """
        
        # Ejecutar get_config
        rpc_reply = m.get_config(source='running', filter=xml_filter)
        
        # Guardar XML crudo en evidencias
        with open("evidencias/rpc_reply_raw.xml", "w") as xml_file:
            xml_file.write(rpc_reply.xml)
            
        # Parsear la respuesta XML
        root = etree.fromstring(rpc_reply.xml.encode('utf-8'))
        namespaces = {'ns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-native'}
        
        # Extraer valores reales devueltos por el router
        try:
            real_hostname = root.find('.//ns:hostname', namespaces).text
        except: real_hostname = "NOT FOUND"
            
        try:
            real_loopback_ip = root.find('.//ns:Loopback[ns:name="10"]/ns:ip/ns:address/ns:primary/ns:address', namespaces).text
            real_loopback_mask = root.find('.//ns:Loopback[ns:name="10"]/ns:ip/ns:address/ns:primary/ns:mask', namespaces).text
        except: real_loopback_ip, real_loopback_mask = "NOT FOUND", "NOT FOUND"
            
        try:
            real_descripcion_wan = root.find('.//ns:GigabitEthernet[ns:name="1"]/ns:description', namespaces).text
        except: real_descripcion_wan = "NOT FOUND"
            
        # Búsqueda flexible para el servidor NTP en el XML
        real_ntp_server = "NOT FOUND"
        ntp_nodes = root.xpath('//*[local-name()="ntp"]//*[local-name()="ip-address" or local-name()="name" or local-name()="server"]')
        for node in ntp_nodes:
            if node.text == expected_ntp_server:
                real_ntp_server = node.text
                break
        if real_ntp_server == "NOT FOUND" and expected_ntp_server in rpc_reply.xml:
            real_ntp_server = expected_ntp_server

        # 4. Comparación de criterios
        criterios = [
            ("Hostname corporativo", expected_hostname, real_hostname),
            ("IP del Loopback", expected_loopback_ip, real_loopback_ip),
            ("Mascara del Loopback", expected_loopback_mask, real_loopback_mask),
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
        if ok_count == 5:
            print(f"Resultado global: CONFORME ({ok_count}/5 OK)")
        else:
            print(f"Resultado global: NO CONFORME ({ok_count}/5 OK)")
        print("==============================")

except Exception as e:
    print(f"Error de conexion o ejecucion NETCONF: {e}")
