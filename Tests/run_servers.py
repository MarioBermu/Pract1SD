import subprocess
import time

# Lista de servidores a ejecutar
servers = [
    ["python3", "insultService.py"]  # Más adelante añadiremos otros aquí
]

processes = []

print("Iniciando servidores...")
for server in servers:
    p = subprocess.Popen(server)
    processes.append(p)

print("Todos los servidores están corriendo.")
print("Presiona Ctrl+C para detenerlos.")

try:
    while True:  # Mantener el script corriendo hasta que se detenga manualmente
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDeteniendo servidores...")
    for p in processes:
        p.terminate()  # Detener todos los procesos
    print("Servidores detenidos.")
