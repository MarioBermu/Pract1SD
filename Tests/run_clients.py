# ---------- run_clients.py ----------
import Pyro4
import multiprocessing
import time
import xmlrpc.client
import json
from datetime import datetime
import concurrent.futures
import sys
import random

if len(sys.argv) < 2:
    print("Uso: python3 run_clients.py <num_nodos>")
    sys.exit(1)

num_nodos = int(sys.argv[1])

SERVER_LIST_FILE = "active_servers.json"
PYRO_SERVICES_FILE = "active_pyro_services.txt"

# ---------- Helpers ----------
def get_all_xmlrpc_servers():
    try:
        with open(SERVER_LIST_FILE, "r") as file:
            servers = json.load(file)
            return [xmlrpc.client.ServerProxy(f"http://localhost:{port}/RPC2", allow_none=True) for port in servers]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_all_valid_pyro_services():
    proxies = []
    try:
        with open(PYRO_SERVICES_FILE, "r") as f:
            names = [line.strip() for line in f if line.strip()]
            for name in names:
                try:
                    proxy = Pyro4.Proxy(f"PYRONAME:{name}")
                    proxy._pyroBind()  # Intenta conectarse para validarlo
                    proxies.append(proxy)
                except Pyro4.errors.CommunicationError:
                    print(f"⚠️ Servicio Pyro4 no disponible: {name}")
    except FileNotFoundError:
        pass
    return proxies

xmlrpc_servers = get_all_xmlrpc_servers()
pyro_insult_service = get_all_valid_pyro_services()

if not xmlrpc_servers:
    print("⚠️ No hay servidores XML-RPC disponibles")
    sys.exit(1)
if not pyro_insult_service:
    print("⚠️ No hay servicios Pyro4 disponibles")
    sys.exit(1)

insults = ["Tonto", "Subnormal", "Zoquete", "Patán", "Idiota", "Sabandija", "Cretino", "Bobalicón",
           "Lelo", "Mamarracho", "Papanatas", "Bocazas", "Cabezón", "Lerdos", "Tarado", "Tontaina",
           "Zopenco", "Torpe", "Mediocre", "Zorrita"]

RESULTS_FILE = "results.json"
LOCK = multiprocessing.Lock()
RESULTS = []

# ---------- Result Handling ----------
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

# ---------- Workload Functions ----------
def send_insults_pyro():
    for i in range(100):
        insult = insults[i % len(insults)]
        try:
            proxy = pyro_insult_service[i % len(pyro_insult_service)]
            proxy.add_insult(insult)
        except Exception as e:
            print(f"Pyro4 Send Error: {type(e).__name__} - {e}")

def receive_insults_pyro():
    for i in range(100):
        try:
            proxy = pyro_insult_service[i % len(pyro_insult_service)]
            print("[Pyro4] Insulto aleatorio:", proxy.get_random_insult())
        except Exception as e:
            print(f"Pyro4 Receive Error: {type(e).__name__} - {e}")

def send_insults_xmlrpc():
    with open(SERVER_LIST_FILE, "r") as file:
        ports = json.load(file)
    for i in range(50):
        insult = insults[i % len(insults)]
        try:
            port = ports[i % len(ports)]
            server = xmlrpc.client.ServerProxy(f"http://localhost:{port}/RPC2", allow_none=True)
            server.store_insult(insult)
        except Exception as e:
            print(f"XML-RPC Send Error: {type(e).__name__} - {e}")

def receive_insults_xmlrpc():
    with open(SERVER_LIST_FILE, "r") as file:
        ports = json.load(file)
    for i in range(2):
        try:
            port = ports[i % len(ports)]
            server = xmlrpc.client.ServerProxy(f"http://localhost:{port}/RPC2", allow_none=True)
            print("[XML-RPC] Insulto aleatorio:", server.get_random_insult())
        except Exception as e:
            print(f"XML-RPC Receive Error: {type(e).__name__} - {e}")

# ---------- MAIN ----------
if __name__ == "__main__":
    time.sleep(2)
    start_time = time.time()

    NUM_CLIENTS = 2
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CLIENTS * 2) as executor:

        # ---------- PYRO ----------
        futures = []
        start_time_pyro = time.time()
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(send_insults_pyro))
            futures.append(executor.submit(receive_insults_pyro))
        concurrent.futures.wait(futures)
        end_time_pyro = time.time()

        save_result({
            "service": "Pyro4",
            "operation": "send/receive",
            "time": end_time_pyro - start_time_pyro,
            "timestamp": datetime.now().isoformat(),
            "nodes": num_nodos
        })

        # ---------- XML-RPC ----------
        futures = []
        start_time_xmlrpc = time.time()
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(send_insults_xmlrpc))
            futures.append(executor.submit(receive_insults_xmlrpc))
        concurrent.futures.wait(futures)
        end_time_xmlrpc = time.time()

        save_result({
            "service": "XML-RPC",
            "operation": "send/receive",
            "time": end_time_xmlrpc - start_time_xmlrpc,
            "timestamp": datetime.now().isoformat(),
            "nodes": num_nodos
        })

    write_results_to_file()
    end_time = time.time()
    print(f"Stress test con {NUM_CLIENTS} clientes completado en {end_time - start_time:.2f} segundos")
