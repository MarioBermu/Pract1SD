import pika
import random
import json
import time

rabbitmq_host = 'localhost'
queue_receive = 'insult_receive_queue'
queue_send = 'insult_send_queue'

# Lista de insultos del cliente
insults = ["Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"]

def connect():
    """Crea y devuelve una conexión a RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_receive)
    channel.queue_declare(queue=queue_send)
    return connection, channel

def send_request(channel, action, insult=None):
    """Envía una solicitud al servidor."""
    data = {"action": action}
    if insult:
        data["insult"] = insult
    channel.basic_publish(exchange='', routing_key=queue_receive, body=json.dumps(data))

def receive_response(channel):
    """Espera y recibe una respuesta del servidor."""
    while True:
        method_frame, header_frame, body = channel.basic_get(queue=queue_send, auto_ack=True)
        if body:
            return json.loads(body.decode())
        time.sleep(0.1)  # Pequeña espera para evitar bucles vacíos

def send_insult():
    """Envía un insulto aleatorio al servidor."""
    connection, channel = connect()
    insult = random.choice(insults)
    send_request(channel, "send_insult", insult)
    connection.close()
    return insult

def get_insult():
    """Solicita un insulto aleatorio del servidor."""
    connection, channel = connect()
    send_request(channel, "get_insult")
    time.sleep(1)  # Espera para recibir la respuesta
    response = receive_response(channel)
    connection.close()
    return response.get("insult", "No response")

def get_insult_list():
    """Solicita la lista completa de insultos almacenados en el servidor."""
    connection, channel = connect()
    send_request(channel, "get_insult_list")
    time.sleep(1)
    response = receive_response(channel)
    connection.close()
    return response.get("insults", [])
