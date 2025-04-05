import pika
import json
import time

rabbitmq_host = 'localhost'
queue_receive = 'text_receive_queue'
queue_send = 'text_send_queue'

def connect():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    return connection, channel

def send_text(text):
    connection, channel = connect()
    data = {"action": "send_text", "text": text}
    channel.basic_publish(exchange='', routing_key=queue_receive, body=json.dumps(data))
    connection.close()
    

def get_texts():
    connection, channel = connect()
    data = {"action": "get_texts"}
    channel.basic_publish(exchange='', routing_key=queue_receive, body=json.dumps(data))
    response = None
    while response is None:
        method_frame, header_frame, body = channel.basic_get(queue=queue_send, auto_ack=True)
        if body:
            response = json.loads(body.decode())
        time.sleep(0.1)
    connection.close()
    return response.get("texts", [])

