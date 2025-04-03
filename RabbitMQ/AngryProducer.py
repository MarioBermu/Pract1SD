import pika
import time

rabbitmq_host = 'localhost'
queue_name = 'work_queue'
text_to_send = "Texto con posibles insultos para filtrar."

def run_for_duration(duration=60):
    """Función que envía mensajes durante un tiempo limitado."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    start_time = time.time()
    while time.time() - start_time < duration:
        channel.basic_publish(exchange='', routing_key=queue_name, body=text_to_send)
        print(f"AngryProduced: {text_to_send}")
        time.sleep(1)  # Controlar la velocidad de envío para simular carga realista

    connection.close()

if __name__ == "__main__":
    run_for_duration(60)  # Ejecutar durante 60 segundos
