import subprocess
import multiprocessing
import time
import math
import pika
import json
from datetime import datetime

# Configuración
rabbitmq_host = 'localhost'
insult_receive_queue = 'insult_receive_queue'
text_receive_queue = 'text_receive_queue'

T_r = 1.0  # Tiempo de respuesta objetivo
C = 1      # Capacidad de procesamiento (mensajes por segundo)

# Historial de procesos lanzados
insult_procs = []
filter_procs = []

# Funciones para lanzar workers
def worker_insult():
    subprocess.Popen(["python3", "insult_service.py"])

def worker_filter():
    subprocess.Popen(["python3", "insultfilter.py"])

# Obtener backlog de una cola
def get_backlog(queue_name):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        queue = channel.queue_declare(queue=queue_name, passive=True)
        message_count = queue.method.message_count
        connection.close()
        return message_count
    except Exception as e:
        print(f"Error getting backlog for {queue_name}: {e}")
        return 0

# Escalado dinámico y recolección de métricas
def dynamic_scaling_loop(duration_seconds=60):
    start_time = time.time()
    metrics = []

    while time.time() - start_time < duration_seconds:
        timestamp = round(time.time() - start_time, 2)

        # InsultService
        B_insult = get_backlog(insult_receive_queue)
        λ_insult = B_insult / T_r
        N_insult = math.ceil((B_insult + λ_insult * T_r) / C)
        delta_insult = N_insult - len(insult_procs)

        if delta_insult > 0:
            for _ in range(delta_insult):
                worker_insult()
                insult_procs.append("worker")
        elif delta_insult < 0:
            for _ in range(-delta_insult):
                insult_procs.pop()

        # FilterService
        B_filter = get_backlog(text_receive_queue)
        λ_filter = B_filter / T_r
        N_filter = math.ceil((B_filter + λ_filter * T_r) / C)
        delta_filter = N_filter - len(filter_procs)

        if delta_filter > 0:
            for _ in range(delta_filter):
                worker_filter()
                filter_procs.append("worker")
        elif delta_filter < 0:
            for _ in range(-delta_filter):
                filter_procs.pop()

        print(f"[{timestamp}s] insult_workers={len(insult_procs)} filter_workers={len(filter_procs)}")
        print(f"    Backlogs -> insult={B_insult} | filter={B_filter}")

        metrics.append({
            "time": timestamp,
            "insult_workers": len(insult_procs),
            "filter_workers": len(filter_procs),
            "insult_backlog": B_insult,
            "filter_backlog": B_filter
        })

        time.sleep(2)

    # Guardar en JSON
    filename = f"scaling_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(metrics, f, indent=4)

    print(f"\n📊 Métricas guardadas en: {filename}")

# Esperar a que se creen las colas
def wait_for_queues(timeout=10):
    print("⏳ Esperando a que se creen las colas en RabbitMQ...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.queue_declare(queue=insult_receive_queue, passive=True)
            channel.queue_declare(queue=text_receive_queue, passive=True)
            connection.close()
            print("✅ Colas encontradas. Iniciando escalado dinámico.")
            return True
        except:
            time.sleep(1)
    print("❌ No se detectaron las colas a tiempo. ¿Están corriendo los servicios?")
    return False

# Ejecución principal
if __name__ == "__main__":
    worker_insult()
    worker_filter()

    if wait_for_queues(timeout=15):
        dynamic_scaling_loop(duration_seconds=60)
    else:
        print("⛔ Abortando ejecución.")
