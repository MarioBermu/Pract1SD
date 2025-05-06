import subprocess
import time
import sys
import redis
import requests
import json
import matplotlib.pyplot as plt
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor

# --- Configuración general ---
MAX_WORKERS               = [1, 2, 3]
BASE_FILTER_MESSAGES      = 1000   # Para tests de filtro Redis
BASE_SERVICE_MESSAGES     = 20     # Para tests de servicio HTTP
FILTER_QUEUE              = 'FILTER_QUEUE'
RESULT_QUEUE              = 'RESULT_QUEUE'
RESULTS_FILE              = 'results_Redis_and_Service.json'
BASE_SERVICE_PORT         = 5000
SERVICE_URL               = f'http://localhost:{BASE_SERVICE_PORT}/insult'

# Cliente Redis para filtro
db = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def measure_filter():
    tiempos = {}
    for workers in MAX_WORKERS:
        num_msgs = BASE_FILTER_MESSAGES * workers
        print(f"→ Filtro: {workers} worker(s), {num_msgs} msgs")
        # limpiar colas
        db.delete(FILTER_QUEUE)
        db.delete(RESULT_QUEUE)
        # arrancar procesos de filtro (uno por worker)
        procs = [subprocess.Popen([sys.executable, 'Insult_filter_server.py']) for _ in range(workers)]
        time.sleep(0.5)  # asegurarse de que estén listos

        # medir solo el procesamiento (push + pop)
        start = time.time()
        for _ in range(num_msgs):
            db.rpush(FILTER_QUEUE, 'Texto con Menso y Zoquete')
        while db.llen(RESULT_QUEUE) < num_msgs:
            time.sleep(0.01)
        elapsed = time.time() - start
        print(f"   Tiempo filtro ({workers}): {elapsed:.2f}s")

        # apagar procesos
        for p in procs:
            p.terminate()
        tiempos[workers] = elapsed
    return tiempos


def measure_service():
    tiempos = {}
    # arrancar UNA única instancia del servicio HTTP
    print(f"→ Iniciando servidor HTTP en puerto {BASE_SERVICE_PORT} (solo 1 proceso)")
    server_proc = subprocess.Popen([
        sys.executable,
        'Insult_service_server.py',
        str(BASE_SERVICE_PORT)
    ])
    time.sleep(1)  # esperar arranque

    # prepare conexión y pool de conexiones
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=max(MAX_WORKERS), pool_maxsize=max(MAX_WORKERS))
    session.mount('http://', adapter)

    for workers in MAX_WORKERS:
        num_msgs = BASE_SERVICE_MESSAGES * workers
        print(f"→ Servicio HTTP: {workers} hilos cliente, {num_msgs} msgs")
        # medir solo el envío/paralelismo de peticiones
        start = time.time()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(
                lambda i: session.post(SERVICE_URL, json={"insult": "Menso"}),
                range(num_msgs)
            )
        elapsed = time.time() - start
        print(f"   Tiempo servicio (hilos={workers}): {elapsed:.2f}s")
        tiempos[workers] = elapsed

    # terminar servidor
    server_proc.terminate()
    return tiempos


if __name__ == '__main__':
    # Test filtro (arranque medido fuera del cronómetro)
    filter_times = measure_filter()
    base_f = filter_times[MAX_WORKERS[0]]
    filter_speedups = {w: base_f / t for w, t in filter_times.items()}

    # Test servicio (un solo servidor, midiendo sólo paralelismo de clientes)
    service_times = measure_service()
    base_s = service_times[MAX_WORKERS[0]]
    service_speedups = {w: base_s / t for w, t in service_times.items()}

    # Guardar resultados
    results = {'Filter': filter_speedups, 'Service': service_speedups}
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))

    # Graficar
    workers = MAX_WORKERS
    plt.figure(figsize=(10,6))
    plt.plot(workers, [filter_speedups[w] for w in workers], marker='o', label='InsultFilter Redis')
    plt.plot(workers, [service_speedups[w] for w in workers], marker='s', label='InsultService HTTP')
    plt.xticks(workers)
    plt.xlabel('Número de procesos/instancias')
    plt.ylabel('Speedup')
    plt.title(f'Speedup Redis e HTTP (Filtro {BASE_FILTER_MESSAGES} msgs, Servicio {BASE_SERVICE_MESSAGES} msgs)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
