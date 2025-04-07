import time
import json
import subprocess
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import insult_client
import insult_filter_client


# Parámetros de prueba
NUM_SERVERS_LIST = [1, 2, 3]
NUM_CLIENTS = 5
NUM_MESSAGES = 50
NUM_MESSAGES_FILTER = 50
RESULTS_FILE = "results.json"
RESULTS_FILE_FILTER = "results_filter.json"

def start_filter():
    return subprocess.Popen(["python3", "insult_filter.py"])

def start_server():
    return subprocess.Popen(["python3", "insult_service.py"]) 

def start_AngryProducer():
    for _ in range(NUM_MESSAGES_FILTER):
        text = "Hola Menso, ¿cómo estás?"
        insult_filter_client.send_text(text)
        time.sleep(0.2)  # Esperar un poco entre envíos para simular carga
        
        

def start_client(client_id):
    for _ in range(NUM_MESSAGES):
        insult_client.send_insult()
        insult_client.get_insult()
        insult_client.get_insult_list()

def run_test():
    all_results = {}
    
    baseline_time = None

    for num_servers in NUM_SERVERS_LIST:
        print(f"Probando con {num_servers} servidores...")

        servers = [start_server() for _ in range(num_servers)]
        time.sleep(2)

        start_time = time.time()

        clients = []
        for i in range(NUM_CLIENTS):
            p = multiprocessing.Process(target=start_client, args=(i,))
            clients.append(p)
            p.start()

        for c in clients:
            c.join()

        end_time = time.time()
        total_time = end_time - start_time

        for s in servers:
            s.terminate()

        if num_servers == 1:
            baseline_time = total_time # tiempo con un servidor

        all_results[num_servers] = baseline_time / total_time  # Speedup

    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f)
    all_results = {}
    
    baseline_time = None

    print("Test completado.")

def run_test_filter():
    all_results = {}
    baseline_time = None

    for num_servers in NUM_SERVERS_LIST:
        print(f"Probando con {num_servers} filtros...")

        servers = [start_filter() for _ in range(num_servers)]
        time.sleep(2)

        start_time = time.time()

        clients = []
        for i in range(NUM_CLIENTS):
            p = multiprocessing.Process(target=start_AngryProducer)
            clients.append(p)
            p.start()

        for c in clients:
            c.join()

        end_time = time.time()
        total_time = end_time - start_time

        for s in servers:
            s.terminate()

        if num_servers == 1:
            baseline_time = total_time

        all_results[num_servers] = baseline_time / total_time  # Speedup

    with open(RESULTS_FILE_FILTER, "w") as f:
        json.dump(all_results, f)

    print("Test completado.")


def plot_results():
    
    with open(RESULTS_FILE, "r") as f:
        results = json.load(f)

    with open(RESULTS_FILE_FILTER, "r") as f:
        results_filter = json.load(f)

    speedupsfilter = [results_filter[str(s)] for s in NUM_SERVERS_LIST]
    servers = sorted(map(int, results.keys()))
    speedups = [results[str(s)] for s in servers]

    plt.figure(figsize=(10, 5))
    plt.plot(servers, speedups, marker='o', linestyle='-',label='Servicio de Insultos', color='red')
    plt.plot(servers, speedupsfilter, marker='o', linestyle='-',label='Servicio de Filtro', color='blue')
    plt.legend(title="Leyenda", title_fontsize='13', fontsize='11')
    plt.xticks(servers)
    plt.xlabel("Número de Servidores")
    plt.ylabel("Speedup")
    plt.title("Speedup comparativo de RabbitMQ")
    plt.grid(True)

 
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_test()
    run_test_filter()
    plot_results()
