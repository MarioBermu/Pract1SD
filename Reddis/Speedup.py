import time
import subprocess
import threading

# Función para iniciar los servidores
def start_server():
    subprocess.Popen(["python", "Insult_service_server.py"])

# Función para los clientes que envían insultos
def client_task():
    for _ in range(10):  # Cada cliente envía 10 mensajes
        subprocess.run(["python", "Insult_service_client.py"])

def start_filter():
    subprocess.Popen(["python", "Insult_filter_server.py"])

def start_filter_client():
    for _ in range(10):  # Cada cliente envía 2 mensajes
        subprocess.run(["python", "Insult_filter_client.py"])

# Ejecutar el test para diferentes configuraciones de servidores
server_counts = [1, 2, 3]
results = []
results_filter = []

for count in server_counts:
    # Iniciar los servidores
    servers = [threading.Thread(target=start_server) for _ in range(count)]
    for server in servers:
        server.start()

    time.sleep(5)  # Dar tiempo para que los servidores estén listos

    start_time = time.time()

    # Iniciar los clientes
    clients = [threading.Thread(target=client_task) for _ in range(10)]
    for client in clients:
        client.start()
    for client in clients:
        client.join()

    end_time = time.time()

    if count == 1:
       basspeed = end_time - start_time

    # Guardar el tiempo total de ejecución
    results.append(basspeed/(end_time - start_time))

    # Terminar los servidores
    for server in servers:
        server.join()

for count in server_counts:
    # Iniciar los servidores
    servers = [threading.Thread(target=start_filter) for _ in range(count)]
    for server in servers:
        server.start()

    time.sleep(5)  # Dar tiempo para que los servidores estén listos

    start_time = time.time()

    # Iniciar los clientes
    clients = [threading.Thread(target=start_filter_client) for _ in range(10)]
    for client in clients:
        client.start()
    for client in clients:
        client.join()

    end_time = time.time()

    if count == 1:
       basspeed = end_time - start_time

    # Guardar el tiempo total de ejecución
    results_filter.append(basspeed/(end_time - start_time))

    # Terminar los servidores
    for server in servers:
        server.join()


# Graficar los resultados
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.plot(server_counts, results, marker='o', label='Servicio de Insultos', color='blue')
plt.plot(server_counts, results_filter, marker='*', label='Servicio de Filtro', color='red')
plt.xticks(server_counts)
plt.title('Comparación de Speedup por Número de Servidores')
plt.xlabel('Número de Servidores')
plt.ylabel('Speedup')
plt.legend(title="Leyenda", title_fontsize='13', fontsize='11')
plt.grid(True)
plt.show()