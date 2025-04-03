import Pyro4
import multiprocessing
import time
import xmlrpc.client
import json
from datetime import datetime
import concurrent.futures
import psutil

pyro_insult_filter = Pyro4.Proxy("PYRONAME:insult.filter")
#xmlrpc_insult_service = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2")
xmlrpc_insult_filter = xmlrpc.client.ServerProxy("http://localhost:8001/RPC2", allow_none=True)
xmlrpc_insult_filter._ServerProxy__transport.timeout = 10


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
        start_time = time.time()
        filtered = pyro_insult_filter.filter_text(text)
        end_time = time.time()

        save_result({
            "service": "Pyro4",
            "operation": "send",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })

def send_texts_xmlrpc():
    """Cada cliente envía 5 textos al servidor XML-RPC"""
    for text in texts:
        start_time = time.time()
        try:
            filtered_text = xmlrpc_insult_filter.filter_text(text)
        except Exception as e:
            print(f"XML-RPC Send Error: {e}")
        end_time = time.time()

        save_result({
            "service": "XML-RPC",
            "operation": "send",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })

def receive_texts_pyro():
    """Cada cliente recibe lista de textos filtrados del servidor Pyro4"""
    filtered_texts_pyro = pyro_insult_filter.get_filtered_texts()
    print("Lista de textos filtrados:")
    for txt in filtered_texts_pyro:
        start_time = time.time()
        print("[Pyro4] Texto filtrado:",txt)        
        end_time = time.time()

        save_result({
            "service": "Pyro4",
            "operation": "receive",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })
        


def receive_texts_xmlrpc():
    """Cada cliente recibe lista de textos del servidor XML-RPC"""
    filtered_texts = xmlrpc_insult_filter.get_filtered_texts()
    print("\nLista de textos filtrados almacenados:")
    for t in filtered_texts:
        start_time = time.time()
        print("[XML-RPC] Texto filtrado:", t)
        end_time = time.time()

        save_result({
            "service": "XML-RPC",
            "operation": "receive",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    time.sleep(2)
    start_time = time.time()

    # Número de clientes simultáneos
    NUM_CLIENTS = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CLIENTS * 4) as executor:
        futures = []

        # Lanzar tareas de envío
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(send_texts_pyro))
            futures.append(executor.submit(send_texts_xmlrpc))

        # Esperar a que terminen
        concurrent.futures.wait(futures)

        # Lanzar tareas de recepción
        futures = []
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(receive_texts_pyro))
            futures.append(executor.submit(receive_texts_xmlrpc))

        concurrent.futures.wait(futures)

    # Guardar los resultados en JSON al final
    write_results_to_file()

    end_time = time.time()
    print(f"Stress test con {NUM_CLIENTS} clientes completado en {end_time - start_time:.2f} segundos")