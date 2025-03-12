import pika
import redis
import time

rabbitmq_host = 'localhost'
exchange_name = 'insult_exchange'
channel_name = 'insult_channel'
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
insult_list = "INSULTS"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

while True:
    insults = redis_client.smembers(insult_list)  # Get all stored insults
    
    for insult in insults:
        channel.basic_publish(exchange=exchange_name, routing_key='', body=insult)
        print(f"Broadcasted: {insult}")
    
    time.sleep(5)  # Publish insults every 5 seconds
