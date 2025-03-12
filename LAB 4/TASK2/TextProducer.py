import pika
import time


rabbitmq_host = 'localhost'
queue_name = 'work_queue'

text = "El sistema desarrollado implementa una arquitectura distribuida basada en RabbitMQ y Redis, permitiendo la gestión eficiente de mensajes a través de colas y canales de publicación/suscripción. Los productores generan información de manera periódica, que es consumida y almacenada en Redis solo si es nueva, evitando duplicados. Posteriormente, un servicio de difusión toma estos datos y los distribuye en tiempo real a múltiples suscriptores. Esta solución garantiza un flujo de datos optimizado, reducción de redundancias y una comunicación efectiva entre los distintos componentes del sistema."

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

while True:
    channel.basic_publish(exchange='', routing_key=queue_name, body=text)
    print(f"Produced: {text}")
    time.sleep(50)
