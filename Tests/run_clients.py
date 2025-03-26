import subprocess
import time

NUM_CLIENTS = 50  # Número de clientes simultáneos
processes = []

print(f"Ejecutando {NUM_CLIENTS} clientes...")

start_time = time.time()

for _ in range(NUM_CLIENTS):
    p = subprocess.Popen(["python3", "insultClient.py"])
    processes.append(p)

# Esperar a que terminen todos los clientes
for p in processes:
    p.wait()

end_time = time.time()

total_time = end_time - start_time
avg_time_per_request = total_time / NUM_CLIENTS

print(f"\nTodos los clientes finalizaron en {total_time:.2f} segundos")
print(f"Tiempo promedio por cliente: {avg_time_per_request:.4f} segundos")
