import pika
import redis

rabbitmq_host = 'localhost'
queue_name = 'insult_queue'
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
insult_list = "INSULTS"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

def callback(ch, method, properties, body):
    insult = body.decode()
    
    # Check if insult is already stored
    if not redis_client.sismember(insult_list, insult):
        redis_client.sadd(insult_list, insult)  # Store in Redis
        print(f"New insult added: {insult}")
    else:
        print(f"Duplicate insult ignored: {insult}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
print("Consumer is waiting for insults...")
channel.start_consuming()
