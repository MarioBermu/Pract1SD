import Pyro4
import multiprocessing
import time
import xmlrpc.client
import json
from datetime import datetime
import concurrent.futures
import sys
import traceback

if len(sys.argv) < 2:
    print("Uso: python3 run_clients_filter.py <num_nodos>")
    sys.exit(1)

num_nodos = int(sys.argv[1])

SERVER_LIST_FILE = "active_servers_filter.json"
PYRO_FILTERS_FILE = "active_pyro_filters.txt"

REPEAT_PYRO = 1000 
REPEAT_XMLRPC = 100 

def get_all_xmlrpc_ports():
    try:
        with open(SERVER_LIST_FILE, "r") as file:
            ports = json.load(file)
            return ports if isinstance(ports, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_valid_pyro_filters():
    proxies = []
    try:
        with open(PYRO_FILTERS_FILE, "r") as f:
            names = [line.strip() for line in f if line.strip()]
            for name in names:
                try:
                    proxy = Pyro4.Proxy(f"PYRONAME:{name}")
                    proxy._pyroBind()
                    proxies.append(proxy)
                except Pyro4.errors.CommunicationError:
                    print(f"⚠️ Pyro no disponible: {name}")
    except FileNotFoundError:
        pass
    return proxies

xmlrpc_ports = get_all_xmlrpc_ports()
pyro_insult_filters = get_valid_pyro_filters()

if not xmlrpc_ports:
    print("⚠️ No hay puertos XML-RPC disponibles")
    sys.exit(1)
if not pyro_insult_filters:
    print("⚠️ No hay filtros Pyro disponibles")
    sys.exit(1)

texts = [
    "Eres un tonto y un idiota",
    "Hoy es un gran día",
    "Ese chico es muy torpe para los deportes",
    "Eres un genio, no un burro",
]

RESULTS_FILE = "results_filter.json"
LOCK = multiprocessing.Lock()
RESULTS = []

def save_result(data):
    with LOCK:
        RESULTS.append(data)

def write_results_to_file():
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
    for _ in range(REPEAT_PYRO):
        for i, text in enumerate(texts):
            try:
                proxy = pyro_insult_filters[i % len(pyro_insult_filters)]
                proxy.filter_text(text)
            except Exception as e:
                print(f"Pyro4 Filter Error: {type(e).__name__} - {e}")

def receive_texts_pyro():
    for _ in range(REPEAT_PYRO):
        for i in range(len(pyro_insult_filters)):
            try:
                proxy = pyro_insult_filters[i % len(pyro_insult_filters)]
                filtered_texts_pyro = proxy.get_filtered_texts()
                #for txt in filtered_texts_pyro:
                    #print("[Pyro4] Texto filtrado:", txt)
            except Exception as e:
                print(f"Pyro4 Receive Error: {type(e).__name__} - {e}")

def send_texts_xmlrpc():
    for _ in range(REPEAT_XMLRPC):
        for i, text in enumerate(texts):
            try:
                port = xmlrpc_ports[i % len(xmlrpc_ports)]
                server = xmlrpc.client.ServerProxy(f"http://localhost:{port}/RPC2", allow_none=True)
                server.filter_text(text)
            except Exception:
                print("XML-RPC Send Error:")
                traceback.print_exc()

def receive_texts_xmlrpc():
    for _ in range(REPEAT_XMLRPC):
        for i in range(len(xmlrpc_ports)):
            try:
                port = xmlrpc_ports[i]
                server = xmlrpc.client.ServerProxy(f"http://localhost:{port}/RPC2", allow_none=True)
                filtered_texts = server.get_filtered_texts()
                for t in filtered_texts:
                    print("[XML-RPC] Texto filtrado:", t)
            except Exception:
                print("XML-RPC Receive Error:")
                traceback.print_exc()

if __name__ == "__main__":
    time.sleep(3)
    start_time = time.time()

    NUM_CLIENTS = 2 * num_nodos
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CLIENTS * 2) as executor:
        futures = []

        # Lanzar tareas de envio
        start_time_pyro = time.time()
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(send_texts_pyro))
            futures.append(executor.submit(send_texts_xmlrpc))
        concurrent.futures.wait(futures)
        end_time_pyro = time.time()

        save_result({
            "service": "Pyro4",
            "operation": "send",
            "time": end_time_pyro - start_time_pyro,
            "timestamp": datetime.now().isoformat(),
            "nodes": num_nodos
        })

        futures = []
        start_time_receive = time.time()
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(receive_texts_pyro))
            futures.append(executor.submit(receive_texts_xmlrpc))
        concurrent.futures.wait(futures)
        end_time_receive = time.time()

        save_result({
            "service": "XML-RPC",
            "operation": "receive",
            "time": end_time_receive - start_time_receive,
            "timestamp": datetime.now().isoformat(),
            "nodes": num_nodos
        })

    write_results_to_file()
    end_time = time.time()
    print(f"Stress test con {NUM_CLIENTS} clientes completado en {end_time - start_time:.2f} segundos")
