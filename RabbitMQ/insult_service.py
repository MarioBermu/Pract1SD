import pika
import random
import json

rabbitmq_host = 'localhost'
queue_receive = 'insult_receive_queue'
queue_send = 'insult_send_queue'

# Lista de insultos almacenados en el servidor
insult_list = []

def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    action = data.get("action")

    if action == "send_insult":
        insult = data.get("insult")
        if insult and insult not in insult_list:
            insult_list.append(insult)
            print(f"Stored new insult: {insult}")
        else:
            print(f"Duplicate insult ignored: {insult}")

    elif action == "get_insult":
        if insult_list:
            insult = random.choice(insult_list)
        else:
            insult = "No insults available"

        response = json.dumps({"insult": insult})
        ch.basic_publish(exchange='', routing_key=queue_send, body=response)
        print(f"Sent insult: {insult}")

    elif action == "get_insult_list":
        response = json.dumps({"insults": insult_list})
        ch.basic_publish(exchange='', routing_key=queue_send, body=response)
        print("Sent full insult list")

    ch.basic_ack(delivery_tag=method.delivery_tag)

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

channel.queue_delete(queue=queue_receive)
channel.queue_delete(queue=queue_send)

channel.queue_declare(queue=queue_receive)
channel.queue_declare(queue=queue_send)

channel.basic_consume(queue=queue_receive, on_message_callback=callback)
print("InsultService is running and waiting for messages...")
channel.start_consuming()
