# ---------- run_servers.py ----------
import subprocess
import time
import sys
import os

# Recibir número de nodos desde la línea de comandos
if len(sys.argv) < 2:
    print("Uso: python3 run_servers.py <num_nodos>")
    sys.exit(1)

num_nodos = int(sys.argv[1])

# Limpiar registros previos
open("active_pyro_services.txt", "w").close()
open("active_servers.json", "w").close()
open("active_pyro_filters.txt", "w").close()

available_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006]

service_ports = available_ports[:len(available_ports)//2]
filter_ports = available_ports[len(available_ports)//2:]

# Servidores a ejecutar
base_servers = [
    ["python3", "../Pyro/insultService.py"],
    ["python3", "../XMLRPC/insult_service.py", "{port}"],
    ["python3", "../Pyro/insultFilter.py"],
    ["python3", "../XMLRPC/insult_service_filter.py", "{port}"]
]

# Crear múltiples instancias según num_nodos
servers = []
service_port_index = 0
filter_port_index = 0

for i in range(num_nodos):
    for server in base_servers:
        if "insult_service.py" in server[1] and "{port}" in server:
            assigned_port = service_ports[service_port_index]
            service_port_index += 1
            servers.append([arg.replace("{port}", str(assigned_port)) for arg in server])
        elif "insult_service_filter.py" in server[1] and "{port}" in server:
            assigned_port = filter_ports[filter_port_index]
            filter_port_index += 1
            servers.append([arg.replace("{port}", str(assigned_port)) for arg in server])
        else:
            servers.append(server)

processes = []

print(f"Iniciando servidores con {num_nodos} nodos...")
for server in servers:
    p = subprocess.Popen(server)
    processes.append(p)

print("Todos los servidores están corriendo.")
print("Presiona Ctrl+C para detenerlos.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDeteniendo servidores...")
    for p in processes:
        p.terminate()
    print("Servidores detenidos.")
