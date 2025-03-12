import pika
import time
import random

rabbitmq_host = 'localhost'
queue_name = 'insult_queue'

insults = ["Tonto", "Idiota", "Torpe", "Patán", "Zoquete"]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

while True:
    insult = random.choice(insults)  # Pick a random insult
    channel.basic_publish(exchange='', routing_key=queue_name, body=insult)
    print(f"Produced: {insult}")
    time.sleep(5)
