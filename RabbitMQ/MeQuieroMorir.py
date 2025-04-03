import multiprocessing
import time
import random

# Parámetros simulados
lambda_rate = 10  # mensajes por segundo
average_processing_time = 0.1  # segundos por mensaje
single_worker_capacity = 20  # mensajes por segundo
current_backlog = 50  # mensajes
target_response_time = 0.5  # segundos

def calculate_required_workers():
    # Escalado basado en tasa de llegada de mensajes y tiempo de procesamiento
    workers_needed = (lambda_rate * average_processing_time) / single_worker_capacity
    
    # Escalado basado en backlog y tiempo de respuesta objetivo
    workers_needed_backlog = (current_backlog + (lambda_rate * target_response_time)) / single_worker_capacity
    
    return max(int(workers_needed), int(workers_needed_backlog))

def worker(queue):
    while not queue.empty():
        message = queue.get()
        time.sleep(average_processing_time)  # Simula el procesamiento de un mensaje
        print(f"Processed: {message}")

def scale_system():
    num_workers = calculate_required_workers()
    print(f"Scaling to {num_workers} workers...")
    
    # Crear una cola de mensajes
    message_queue = multiprocessing.Queue()
    for _ in range(current_backlog):
        message_queue.put("Message")
    
    # Iniciar trabajadores
    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(message_queue,))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()

if __name__ == "__main__":
    scale_system()
