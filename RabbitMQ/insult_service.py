import pika
import random
import json

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
QUEUE_RECEIVE = 'insult_receive_queue'
QUEUE_SEND = 'insult_send_queue'

# Internal insult storage
insult_list = []

# Callback to process incoming messages
def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    action = data.get('action')

    if action == 'send_insult':
        insult = data.get('insult')
        if insult and insult not in insult_list:
            insult_list.append(insult)
            print(f"Stored new insult: {insult}")
        else:
            print(f"Duplicate insult ignored: {insult}")

    elif action == 'get_insult':
        insult = random.choice(insult_list) if insult_list else 'No insults available'
        response = json.dumps({'insult': insult})
        channel.basic_publish(exchange='', routing_key=QUEUE_SEND, body=response)
        print(f"Sent insult: {insult}")

    elif action == 'get_insult_list':
        response = json.dumps({'insults': insult_list})
        channel.basic_publish(exchange='', routing_key=QUEUE_SEND, body=response)
        print('Sent full insult list')

    # Acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Setup RabbitMQ connection and queues
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
# Declare queues with durable=False to match existing configuration
channel.queue_declare(queue=QUEUE_RECEIVE, durable=False)
channel.queue_declare(queue=QUEUE_SEND, durable=False)
channel.basic_qos(prefetch_count=1)

print('InsultService is running and waiting for messages...')
channel.basic_consume(queue=QUEUE_RECEIVE, on_message_callback=callback)
channel.start_consuming()