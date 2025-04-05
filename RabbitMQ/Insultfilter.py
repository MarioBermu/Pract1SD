import pika
import json
import redis

REDIS_KEY = "filter_processed_count"


rabbitmq_host = 'localhost'
queue_receive = 'text_receive_queue'
queue_send = 'text_send_queue'

redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Configuración de Redis
insults = {"Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"}

def censor_text(text):
    for insult in insults:
        text = text.replace(insult, "CENSORED")
    redis_client.rpush("RESULTS", text)  # Almacenar el texto procesado en Redis
    print(f"Processed text: {text}")
    redis_client.incr(REDIS_KEY)
    return text

def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    action = data.get("action")

    if action == "send_text":
        text = data.get("text")
        censor_text(text)

    elif action == "get_texts":
        texts = [redis_client.lindex("RESULTS", i).decode('utf-8') for i in range(redis_client.llen("RESULTS"))]
        response = json.dumps({"texts": texts})
        ch.basic_publish(exchange='', routing_key=queue_send, body=response)
        print("Sent list of stored texts")

    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_receive)
channel.queue_declare(queue=queue_send)
channel.basic_consume(queue=queue_receive, on_message_callback=callback)
print("Text service is running and waiting for messages...")
channel.start_consuming()
