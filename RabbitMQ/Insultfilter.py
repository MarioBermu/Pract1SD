import pika
import redis

rabbitmq_host = 'localhost'
queue_name = 'work_queue'
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Lista de insultos a censurar
insults = ["subnormal profundo", "tarado sin neuronas", "pedazo de inútil", "retrasado mental de campeonato"]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

def callback(ch, method, properties, body):
    text = body.decode()

    # Reemplazar insultos por "CENSORED"
    for insult in insults:
        text = text.replace(insult, "CENSORED")

    # Guardar texto limpio en Redis
    redis_client.rpush("RESULTS", text)
    
    print(f"Processed text: {text}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
print("Consumer is waiting for messages...")
channel.start_consuming()
