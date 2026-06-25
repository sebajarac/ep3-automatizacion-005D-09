# Informe Técnico de Implementación y Compliance Automatizado

## 1. Objetivo del Proyecto
Este proyecto implementó la incorporación automatizada y auditable de un nuevo router corporativo para la empresa Pesquera Austral SpA. El objetivo principal consistió en estandarizar la configuración inicial del dispositivo de forma reproducible mediante metodologías de automatización de redes, reduciendo errores humanos y certificando de manera independiente el cumplimiento del despliegue.

## 2. Alcance
* **Dentro del alcance:** Levantamiento del estado inicial del router (baseline), automatización de servicios programables (NETCONF/RESTCONF), aprovisionamiento de parámetros corporativos (hostname, banner, NTP, interfaz WAN y Loopback) y auditoría automatizada final.
* **Fuera del alcance:** Enrutamiento dinámico avanzado, políticas de seguridad perimetral complejas (ACLs de producción) y cableado físico del dispositivo.

## 3. Infraestructura Utilizada
* **Estación de Trabajo:** DEVASC VM (Sistema Operativo Linux Ubuntu, labvm).
* **Dispositivo de Red:** Cisco CSR1kv (Sistema Operativo Cisco IOS-XE).
* **Herramientas de Software:** Ansible (versión core), pyATS / Genie, Python 3, Git y GitHub.

## 4. Tecnologías Empleadas y Justificación
* **pyATS / Genie:** Se utilizó en la Fase 1 y 5 debido a su alta capacidad de conectarse vía CLI tradicional y transformar configuraciones complejas en datos estructurados de Python para realizar análisis comparativos (diffs).
* **Ansible:** Empleado en la Fase 2 por su capacidad de orquestación sin agentes e idempotencia, garantizando consistencia en la aplicación de la configuración corporativa.
* **NETCONF:** Protocolo robusto basado en XML utilizado en la Fase 3 como validador nativo e independiente para auditar de forma estructurada el estado del router.
* **RESTCONF:** Protocolo liviano basado en API HTTP/JSON utilizado en la Fase 4 para realizar consultas rápidas a recursos específicos del modelo YANG de manera ágil.

## 5. Configuración Aplicada
* **Código de Alumno:** 005D-09
* **Nombre de la Empresa:** Pesquera Austral SpA
* **Hostname Corporativo:** RTR-PESAUST
* **IP Loopback de Gestión:** 10.5.9.1 /24
* **Descripción Interfaz WAN:** Enlace-WAN-Rancagua
* **Banner de Acceso:** ACCESO RESTRINGIDO - PESAUST
* **Servidor NTP:** 1.1.1.1

## 6. Resultados de Validación
* **Validación NETCONF (Fase 3):** CONFORME (5/5 criterios validados exitosamente en formato XML).
* **Validación RESTCONF (Fase 4):** CONFORME (4/4 endpoints consultados y validados exitosamente en formato JSON).

## 7. Conclusiones
El aprovisionamiento del router se completó de manera exitosa y sin desvíos. La infraestructura cumple al 100% con los estándares exigidos por la empresa cliente, habiendo superado las auditorías automatizadas independientes. El equipo se declara en estado **CONFORME** y se encuentra listo para ser entregado al departamento de operaciones de red.
