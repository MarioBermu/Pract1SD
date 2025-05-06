import pika
import json
import time

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
QUEUE_RECEIVE = 'text_receive_queue'
QUEUE_SEND = 'text_send_queue'

# Insults set for censoring
insults_set = {"Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"}

# Function to censor insults in text
def censor_text(text):
    time.sleep(0.1)  # Simulate processing delay
    censored = text
    for insult in insults_set:
        censored = censored.replace(insult, "CENSORED")
    print(f"Processed text: {censored}")
    return censored

# Callback to handle messages
def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    action = data.get("action")

    if action == "send_text":
        text = data.get("text")
        censored = censor_text(text)
        # Publish acknowledgment of processed text
        response = json.dumps({"censored": censored})
        ch.basic_publish(exchange='', routing_key=QUEUE_SEND, body=response)
        print(f"Acknowledgment sent: {censored}")

    elif action == "get_texts":
        response = json.dumps({"status": "OK"})
        ch.basic_publish(exchange='', routing_key=QUEUE_SEND, body=response)
        print("Sent text processing status")

    # Acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Establish connection and declare queues
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_RECEIVE, durable=False)
channel.queue_declare(queue=QUEUE_SEND, durable=False)
channel.basic_qos(prefetch_count=1)

print("InsultFilter is running and waiting for messages...")
channel.basic_consume(queue=QUEUE_RECEIVE, on_message_callback=callback)
channel.start_consuming()