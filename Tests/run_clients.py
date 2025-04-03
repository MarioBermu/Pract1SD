import Pyro4
import multiprocessing
import time
import xmlrpc.client
import json
from datetime import datetime
import concurrent.futures
import psutil
import sys
import random

if len(sys.argv) < 2:
    print("Uso: python3 run_clients.py <num_nodos>")
    sys.exit(1)

num_nodos = int(sys.argv[1])


SERVER_LIST_FILE = "active_servers.json"

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


pyro_insult_service = Pyro4.Proxy("PYRONAME:insult.service")
#xmlrpc_insult_service = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2", allow_none=True)


insults = ["Tonto", "Subnormal", "Zoquete", "Patán", "Idiota", "Sabandija", "Cretino", "Bobalicón",
           "Lelo", "Mamarracho", "Papanatas", "Bocazas", "Cabezón", "Lerdos", "Tarado", "Tontaina",
           "Zopenco", "Torpe", "Mediocre", "Zorrita"]

RESULTS_FILE = "results.json"
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

def send_insults_pyro():
    """Cada cliente envía 100 insultos al servidor Pyro4"""
    start_time = time.time()
    for _ in range(100):
        insult = insults[_ % len(insults)]
        pyro_insult_service.add_insult(insult)
    
    end_time = time.time()
        

def send_insults_xmlrpc():
    """Cada cliente envía 100 insultos al servidor XML-RPC"""
    start_time = time.time()
    for _ in range(55):
        insult = insults[_ % len(insults)]
        try:
            server = xmlrpc_servers[_ % len(xmlrpc_servers)]  
            server.store_insult(insult)
        except Exception as e:
            print(f"XML-RPC Send Error: {e}")
    end_time = time.time()


def receive_insults_pyro():
    """Cada cliente recibe insultos del servidor Pyro4"""
    for _ in range(100):
        start_time = time.time()
        print("[Pyro4] Insulto aleatorio:", pyro_insult_service.get_random_insult())
        end_time = time.time()
        


def receive_insults_xmlrpc():
    """Cada cliente recibe insultos del servidor XML-RPC"""
    for _ in range(1):
        start_time = time.time()
        server = xmlrpc_servers[_ % len(xmlrpc_servers)]  # 🔄 Reparte entre los servidores disponibles
        print("[XML-RPC] Insulto aleatorio:", server.get_random_insult())
        end_time = time.time()
        #time.sleep(3)


if __name__ == "__main__":
    time.sleep(2)
    start_time = time.time()

    # Número de clientes simultáneos
    NUM_CLIENTS = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CLIENTS * 2) as executor:
        futures = []

        # Lanzar tareas de envío
        for _ in range(NUM_CLIENTS):
            start_time_pyro = time.time()
            futures.append(executor.submit(send_insults_pyro))
            futures.append(executor.submit(receive_insults_pyro))
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
            futures.append(executor.submit(send_insults_xmlrpc))
            futures.append(executor.submit(receive_insults_xmlrpc))
            end_time_xmlrpc = time.time()
            save_result({
                "service": "XML-RPC",
                "operation": "send/receive",
                "time": end_time_xmlrpc - start_time_xmlrpc,
                "timestamp": datetime.now().isoformat(),
                "nodes": num_nodos
            })
        # Esperar a que terminen

        concurrent.futures.wait(futures)

    # Guardar los resultados en JSON al final
    write_results_to_file()

    end_time = time.time()
    print(f"Stress test con {NUM_CLIENTS} clientes completado en {end_time - start_time:.2f} segundos")