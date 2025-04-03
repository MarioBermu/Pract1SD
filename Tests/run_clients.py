import Pyro4
import multiprocessing
import time
import xmlrpc.client
import json
from datetime import datetime
import concurrent.futures
import psutil

pyro_insult_service = Pyro4.Proxy("PYRONAME:insult.service")
xmlrpc_insult_service = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2", allow_none=True)
xmlrpc_insult_service._ServerProxy__transport.timeout = 10
print(xmlrpc_insult_service.get_insult_list()) 
#print("[XML-RPC] Insulto aleatorio:", xmlrpc_insult_service.get_random_insult())

insults = ["Tonto", "Subnormal", "Zoquete", "Patán", "Idiota", "Sabandija", "Cretino", "Bobalicón",
           "Lelo", "Mamarracho", "Papanatas", "Bocazas", "Cabezón", "Lerdos", "Tarado", "Tontaina",
           "Zopenco", "Torpe", "Mediocre", "Zorrita"]

RESULTS_FILE = "results.json"
LOCK = multiprocessing.Lock()  # Para evitar escritura simultánea en JSON
RESULTS = []


def count_active_servers():
    """Cuenta cuántos procesos de los servidores están en ejecución."""
    server_keywords = ["insultService", "insult_service"]
    active_servers = 0

    for proc in psutil.process_iter(attrs=['cmdline']):
        try:
            cmdline = proc.info.get("cmdline", [])
            if any(keyword in " ".join(cmdline) for keyword in server_keywords):
                active_servers += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue  # Evita errores si un proceso desaparece o no se puede acceder

    print(f"🔍 DEBUG: Servidores activos detectados: {active_servers}")  # 🚀 Debugging
    return active_servers

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
    for _ in range(100):
        start_time = time.time()
        insult = insults[_ % len(insults)]
        pyro_insult_service.add_insult(insult)
        end_time = time.time()
        

        save_result({
            "service": "Pyro4",
            "operation": "send",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })

def send_insults_xmlrpc():
    """Cada cliente envía 100 insultos al servidor XML-RPC"""
    for _ in range(2):
        start_time = time.time()
        insult = insults[_ % len(insults)]
        try:
            xmlrpc_insult_service.store_insult(insult)
        except Exception as e:
            print(f"XML-RPC Send Error: {e}")
        end_time = time.time()

        save_result({
            "service": "XML-RPC",
            "operation": "send",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })

def receive_insults_pyro():
    """Cada cliente recibe insultos del servidor Pyro4"""
    for _ in range(10):
        start_time = time.time()
        print("[Pyro4] Insulto aleatorio:", pyro_insult_service.get_random_insult())
        end_time = time.time()
        #time.sleep(3)

        save_result({
            "service": "Pyro4",
            "operation": "receive",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })
        #time.sleep(3)


def receive_insults_xmlrpc():
    """Cada cliente recibe insultos del servidor XML-RPC"""
    for _ in range(2):
        start_time = time.time()
        print("[XML-RPC] Insulto aleatorio:", xmlrpc_insult_service.get_random_insult())
        end_time = time.time()
        #time.sleep(3)

        save_result({
            "service": "XML-RPC",
            "operation": "receive",
            "time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        })
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
            futures.append(executor.submit(send_insults_pyro))
            futures.append(executor.submit(send_insults_xmlrpc))

        # Esperar a que terminen
        concurrent.futures.wait(futures)

        # Lanzar tareas de recepción
        futures = []
        for _ in range(NUM_CLIENTS):
            futures.append(executor.submit(receive_insults_pyro))
            futures.append(executor.submit(receive_insults_xmlrpc))

        concurrent.futures.wait(futures)

    # Guardar los resultados en JSON al final
    write_results_to_file()

    end_time = time.time()
    print(f"Stress test con {NUM_CLIENTS} clientes completado en {end_time - start_time:.2f} segundos")