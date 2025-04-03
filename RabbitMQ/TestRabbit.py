import time
import json
import subprocess
import multiprocessing
import insult_client  # Asegúrate de que se importa correctamente
import AngryProducer  # Asegúrate de que se importa correctamente

# Parámetros de prueba
NUM_CLIENTS = 100   # Número de clientes simultáneos
DURATION = 60  # Duración de la prueba en segundos
RESULTS_FILE = "results_rabbitmq.json"

def start_insult_service():
    """Inicia el servidor de insultos RabbitMQ."""
    return subprocess.Popen(["python", "insult_service.py"])

def start_insult_filter():
    """Inicia el servidor de filtro RabbitMQ."""
    return subprocess.Popen(["python", "Insultfilter.py"])

def start_insult_client(client_id, results):
    """Cliente que interactúa con insult_service."""
    count = 0
    start_time = time.time()

    while time.time() - start_time < DURATION:
        insult = insult_client.send_insult()  # Envía un insulto al servidor
        insult = insult_client.get_insult()   # Solicita un insulto al servidor
        
        if insult:
            count += 2  # Contar respuestas recibidas

    results.append(count)  # Guardar número de respuestas procesadas

def start_angry_producer(client_id, results):
    """Cliente que interactúa con insultfilter."""
    # Inicializar el contador de respuestas procesadas
    count = 0
    start_time = time.time()

    # Ejecutar AngryProducer por una duración limitada y monitorear las respuestas
    while time.time() - start_time < DURATION:
        # Asegúrate de que la función 'run_for_duration' esté siendo importada y usada correctamente
        AngryProducer.run_for_duration(DURATION)  # Ajustado para enviar texto durante un tiempo limitado
        # No necesitamos un resultado directo ya que el procesamiento es automático y el conteo debe ser ajustado externamente si es necesario

    # Agregar el conteo al resultado global (opcional, depende de cómo desees contar las respuestas)
    results.append(count)

def run_test():
    """Ejecuta la prueba de carga con 2 servidores y múltiples clientes."""
    print("Iniciando servidores...")
    insult_service = start_insult_service()
    insult_filter = start_insult_filter()
    time.sleep(2)  # Esperar que los servidores se inicien

    print(f"Iniciando prueba con {NUM_CLIENTS} clientes durante {DURATION} segundos...")
    results_insult = multiprocessing.Manager().list()
    results_filter = multiprocessing.Manager().list()

    # Iniciar clientes para insult_service
    clients_insult = [multiprocessing.Process(target=start_insult_client, args=(i, results_insult)) for i in range(NUM_CLIENTS)]
    # Iniciar clientes para insult_filter
    clients_filter = [multiprocessing.Process(target=start_angry_producer, args=(i, results_filter)) for i in range(NUM_CLIENTS)]

    for client in clients_insult + clients_filter:
        client.start()

    for client in clients_insult + clients_filter:
        client.join()

    # Detener los servidores
    insult_service.terminate()
    insult_filter.terminate()

    total_requests_insult = sum(results_insult)
    total_requests_filter = sum(results_filter)

    print(f"Total de peticiones procesadas por insult_service en {DURATION} segundos: {total_requests_insult}")
    print(f"Total de peticiones procesadas por insult_filter en {DURATION} segundos: {total_requests_filter}")

    # Guardar resultados en JSON
    with open(RESULTS_FILE, "w") as f:
        json.dump({"total_requests_insult": total_requests_insult, "total_requests_filter": total_requests_filter}, f)

    print("Prueba completada. Resultados guardados.")

if __name__ == "__main__":
    run_test()
