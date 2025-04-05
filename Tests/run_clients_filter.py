import Pyro4
import multiprocessing
import time
import xmlrpc.client
import json
from datetime import datetime
import concurrent.futures
import psutil
import sys

if len(sys.argv) < 2:
    print("Uso: python3 run_clients.py <num_nodos>")
    sys.exit(1)

num_nodos = int(sys.argv[1])

SERVER_LIST_FILE = "active_servers_filter.json"

def get_all_xmlrpc_servers():
    """Devuelve una lista con todos los proxies XML-RPC disponibles."""
    try:
        with open(SERVER_LIST_FILE, "r") as file:
            servers = json.load(file)
            return [xmlrpc.client.ServerProxy(f"http://localhost:{port}/RPC2", allow_none=True) for port in servers]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

xmlrpc_servers = get_all_xmlrpc_servers()
if not xmlrpc_servers:
    print("⚠️ No hay servidores XML-RPC disponibles")
    sys.exit(1)


pyro_insult_filter = Pyro4.Proxy("PYRONAME:insult.filter")


texts = [
    "Eres un tonto y un idiota",
    "Hoy es un gran día",
    "Ese chico es muy torpe para los deportes",
    "Eres un genio, no un burro",
]

RESULTS_FILE = "results_filter.json"
LOCK = multiprocessing.Lock()  # Para evitar escritura simultánea en JSON
RESULTS = []


def save_result(data):
    """Guarda los resultados en el JSON de forma concurrente."""
    with LOCK:
        RESULTS.append(data)


def write_results_to_file():
    """Escribe todos los resultados almacenados en memoria al archivo JSON una vez."""
    with LOCK:
        try:
            with open(RESULTS_FILE, "r") as file:
                existing_results = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_results = []

        existing_results.extend(RESULTS)

        with open(RESULTS_FILE, "w") as file:
            json.dump(existing_results, file, indent=4)

def send_texts_pyro():
    """Cada cliente envía 5 textos al servidor Pyro4"""
    for text in texts:
        filtered = pyro_insult_filter.filter_text(text)
        


def send_texts_xmlrpc():
    """Cada cliente envía 5 textos al servidor XML-RPC"""

    for i, text in enumerate(texts):
        try:
            server = xmlrpc_servers[i % len(xmlrpc_servers)]
            filtered_text = server.filter_text(text)
        except Exception as e:
            print(f"XML-RPC Send Error: {e}")


def receive_texts_pyro():
    """Cada cliente recibe lista de textos filtrados del servidor Pyro4"""
    filtered_texts_pyro = pyro_insult_filter.get_filtered_texts()
    print("Lista de textos filtrados:")
    for txt in filtered_texts_pyro:
        #start_time = time.time()
        print("[Pyro4] Texto filtrado:",txt)        
        #end_time = time.time()



def receive_texts_xmlrpc():
    """Cada cliente recibe lista de textos del servidor XML-RPC"""
    for i in range(len(xmlrpc_servers)):
        try:
            server = xmlrpc_servers[i]
            filtered_texts = server.get_filtered_texts()
            for t in filtered_texts:
                print("[XML-RPC] Texto filtrado:", t)
        except Exception as e:
            print(f"XML-RPC Receive Error: {e}")

       

if __name__ == "__main__":
    time.sleep(2)
    start_time = time.time()

    # Número de clientes simultáneos
    NUM_CLIENTS = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CLIENTS * 4) as executor:
        futures = []

        # Lanzar tareas de envío
        for _ in range(NUM_CLIENTS):
            start_time_pyro = time.time()
            futures.append(executor.submit(send_texts_pyro))
            futures.append(executor.submit(send_texts_xmlrpc))
            end_time_pyro = time.time()
            
            save_result({
                "service": "Pyro4",
                "operation": "send/receive",
                "time": end_time_pyro - start_time_pyro,
                "timestamp": datetime.now().isoformat(),
                "nodes": num_nodos
            })

        # Esperar a que terminen
        concurrent.futures.wait(futures)

        # Lanzar tareas de recepción
        futures = []
        for _ in range(NUM_CLIENTS):
            start_time_xmlrpc = time.time()
            futures.append(executor.submit(receive_texts_pyro))
            futures.append(executor.submit(receive_texts_xmlrpc))
            end_time_xmlrpc = time.time()
            save_result({
                "service": "XML-RPC",
                "operation": "send/receive",
                "time": end_time_xmlrpc - start_time_xmlrpc,
                "timestamp": datetime.now().isoformat(),
                "nodes": num_nodos
            })

        concurrent.futures.wait(futures)

    # Guardar los resultados en JSON al final
    write_results_to_file()

    end_time = time.time()
    print(f"Stress test con {NUM_CLIENTS} clientes completado en {end_time - start_time:.2f} segundos")