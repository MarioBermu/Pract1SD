import subprocess
import time
import math
import json
import redis
import pika
from datetime import datetime

rabbitmq_host = 'localhost'
MAX_WORKERS = 10
INTERVAL = 1  # segundos
METRICS_FILENAME = f"scaling_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

insult_procs = []
filter_procs = []

redis_client = redis.Redis(host='localhost', port=6379, db=0)
INSULT_KEY = "insult_processed_count"
FILTER_KEY = "filter_processed_count"

def worker_insult():
    return subprocess.Popen(["python3", "insult_service.py"])

def worker_filter():
    return subprocess.Popen(["python3", "insult_filter.py"])

def measure_T():
    print("⚠️ Midiendo T ficticio (fijo = 0.5s por mensaje)")
    return 0.5, 2  # T=0.5s → C=2 msg/s

def get_queue_size(queue_name):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        queue = channel.queue_declare(queue=queue_name, passive=True)
        message_count = queue.method.message_count
        connection.close()
        return message_count
    except Exception as e:
        print(f" Error al consultar tamaño de cola {queue_name}: {e}")
        return 0

def dynamic_scaling_loop(T_insult, C_insult, T_filter, C_filter):
    print("Iniciando escalado dinámico basado en tráfico real y backlog...")
    metrics = []

    last_insult_total = int(redis_client.get(INSULT_KEY) or 0)
    last_filter_total = int(redis_client.get(FILTER_KEY) or 0)

    while True:
        time.sleep(INTERVAL)

        insult_total = int(redis_client.get(INSULT_KEY) or 0)
        filter_total = int(redis_client.get(FILTER_KEY) or 0)

        λ_insult = max(0, insult_total - last_insult_total) / INTERVAL
        λ_filter = max(0, filter_total - last_filter_total) / INTERVAL

        last_insult_total = insult_total
        last_filter_total = filter_total

        queue_insult_pending = get_queue_size("insult_receive_queue")
        queue_filter_pending = get_queue_size("text_receive_queue")

        # Escalado por tasa λ
        N_insult = math.ceil((λ_insult * T_insult) / C_insult)
        N_filter = math.ceil((λ_filter * T_filter) / C_filter)

        # Escalado agresivo si hay backlog
        if queue_insult_pending > 1000:
            N_insult = MAX_WORKERS
        if queue_filter_pending > 1000:
            N_filter = MAX_WORKERS

        # Nunca bajar de 1 worker
        N_insult = max(1, min(MAX_WORKERS, N_insult))
        N_filter = max(1, min(MAX_WORKERS, N_filter))

        delta_insult = N_insult - len(insult_procs)
        if delta_insult > 0:
            for _ in range(min(delta_insult, 2)):
                insult_procs.append(worker_insult())
        elif delta_insult < 0:
            for _ in range(min(-delta_insult, 2)):
                proc = insult_procs.pop()
                if proc.poll() is None:
                    proc.terminate()

        delta_filter = N_filter - len(filter_procs)
        if delta_filter > 0:
            for _ in range(min(delta_filter, 2)):
                filter_procs.append(worker_filter())
        elif delta_filter < 0:
            for _ in range(min(-delta_filter, 2)):
                proc = filter_procs.pop()
                if proc.poll() is None:
                    proc.terminate()

        print(f"[{time.strftime('%H:%M:%S')}] λ_insult={λ_insult:.2f} | λ_filter={λ_filter:.2f} | "
              f"Backlog: insult={queue_insult_pending} filter={queue_filter_pending} → "
              f"Workers: {len(insult_procs)} / {len(filter_procs)}")

        metrics.append({
            "time": round(time.time(), 2),
            "insult_workers": len(insult_procs),
            "filter_workers": len(filter_procs),
            "lambda_insult": λ_insult,
            "lambda_filter": λ_filter,
            "queue_insult_backlog": queue_insult_pending,
            "queue_filter_backlog": queue_filter_pending
        })

        with open(METRICS_FILENAME, 'w') as f:
            json.dump(metrics, f, indent=4)

def reset_redis_counters():
    redis_client.set(INSULT_KEY, 0)
    redis_client.set(FILTER_KEY, 0)

if __name__ == "__main__":
    reset_redis_counters()
    time.sleep(1)
    T_insult, C_insult = measure_T()
    T_filter, C_filter = measure_T()

    # Lanzar 1 worker de cada tipo para arrancar
    insult_procs.append(worker_insult())
    filter_procs.append(worker_filter())

    dynamic_scaling_loop(T_insult, C_insult, T_filter, C_filter)
