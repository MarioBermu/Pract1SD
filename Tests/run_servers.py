import subprocess
import time
import sys

# Recibir número de nodos desde la línea de comandos
if len(sys.argv) < 2:
    print("Uso: python3 run_servers.py <num_nodos>")
    sys.exit(1)

num_nodos = int(sys.argv[1])


available_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006]

# Servidores a ejecutar
base_servers = [
    ["python3", "../Pyro/insultService.py"],
    ["python3", "../XMLRPC/insult_service.py", "{port}"],
    ["python3", "../Pyro/insultFilter.py"],
    ["python3", "../XMLRPC/insult_service_filter.py", "{port}"]
]

# Crear múltiples instancias según num_nodos
servers = []
port_index = 0
for i in range(num_nodos):
    for server in base_servers:
        if "{port}" in server:
            if port_index >= len(available_ports):
                print("⚠️ No hay suficientes puertos disponibles. Reduce el número de nodos.")
                sys.exit(1)
            assigned_port = available_ports[port_index]
            port_index += 1
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
