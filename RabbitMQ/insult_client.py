import pika
import random
import json
import time

rabbitmq_host = 'localhost'
queue_receive = 'insult_receive_queue'
queue_send = 'insult_send_queue'

# Lista de insultos del cliente
insults = ["Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"]

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_receive)
channel.queue_declare(queue=queue_send)

def send_request(action, insult=None):
    """Envía una solicitud al servidor"""
    data = {"action": action}
    if insult:
        data["insult"] = insult
    channel.basic_publish(exchange='', routing_key=queue_receive, body=json.dumps(data))

def receive_response():
    """Espera y recibe una respuesta del servidor"""
    method_frame, header_frame, body = channel.basic_get(queue=queue_send, auto_ack=True)
    if body:
        return json.loads(body.decode())
    return None

# Ejecutar el proceso solo 5 veces
for _ in range(5):
    # Enviar un insulto aleatorio al servidor
    insult = random.choice(insults)
    send_request("send_insult", insult)
    print(f"Sent insult: {insult}")

    time.sleep(2)

    # Solicitar un insulto aleatorio del servidor
    send_request("get_insult")
    time.sleep(1)  # Esperar un momento para recibir la respuesta
    response = receive_response()
    if response:
        print(f"Received insult: {response['insult']}")

    time.sleep(2)

    # Solicitar la lista completa de insultos
    send_request("get_insult_list")
    time.sleep(1)
    response = receive_response()
    if response:
        print(f"Full insult list: {response['insults']}")

    time.sleep(5)

# Cerrar la conexión cuando termina
connection.close()
print("Client finished execution.")
