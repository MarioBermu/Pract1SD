import pika

rabbitmq_host = 'localhost'
exchange_name = 'insult_exchange'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange=exchange_name, queue=queue_name)

def callback(ch, method, properties, body):
    print(f"Received insult: {body.decode()}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Receiver is waiting for insults...")
channel.start_consuming()
