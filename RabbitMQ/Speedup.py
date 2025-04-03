import time
import json
import subprocess
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import insult_client


# Parámetros de prueba
NUM_SERVERS_LIST = [1, 2, 3]
NUM_CLIENTS = 10
NUM_MESSAGES = 10
RESULTS_FILE = "results.json"


def start_server():
    return subprocess.Popen(["python", "insult_service.py"])

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
            baseline_time = total_time

        all_results[num_servers] = baseline_time / total_time  # Speedup

    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f)

    print("Test completado.")

def plot_results():
    with open(RESULTS_FILE, "r") as f:
        results = json.load(f)

    servers = sorted(map(int, results.keys()))
    speedups = [results[str(s)] for s in servers]

    plt.figure(figsize=(10, 5))
    plt.plot(servers, speedups, marker='o', linestyle='-', color='red')
    plt.xticks(servers)
    plt.xlabel("Número de Servidores")
    plt.ylabel("Speedup")
    plt.title("Speedup comparativo de RabbitMQ")
    plt.grid(True)

 
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_test()
    plot_results()
