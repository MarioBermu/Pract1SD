# run_clients.py
import multiprocessing
import time
import json
import pika
import random
import signal
import sys

rabbitmq_host = 'localhost'
insult_receive_queue = 'insult_receive_queue'
text_receive_queue = 'text_receive_queue'

insult_list = ["Idiota", "Torpe", "Patán", "Burro", "Zoquete", "Cabezón", "Necio"]

def send_insults():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    try:
        while True:
            insult = random.choice(insult_list)
            data = {"action": "send_insult", "insult": insult}
            channel.basic_publish(exchange='', routing_key=insult_receive_queue, body=json.dumps(data))
            time.sleep(0.05)  # 20 msg/s por proceso
    except KeyboardInterrupt:
        connection.close()

def send_texts():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    try:
        while True:
            sentence = "Eres un " + random.choice(insult_list)
            data = {"action": "send_text", "text": sentence}
            channel.basic_publish(exchange='', routing_key=text_receive_queue, body=json.dumps(data))
            time.sleep(0.1)  # 10 msg/s por proceso
    except KeyboardInterrupt:
        connection.close()

if __name__ == "__main__":
    insult_clients = [multiprocessing.Process(target=send_insults) for _ in range(5)]
    text_clients = [multiprocessing.Process(target=send_texts) for _ in range(5)]
    all_clients = insult_clients + text_clients

    for p in all_clients:
        p.start()

    try:
        run_time = 60  # segundos
        print(f"🌪️ Ejecutando carga durante {run_time} segundos...")
        time.sleep(run_time)

    except KeyboardInterrupt:
        print("Interrumpido manualmente. Cerrando procesos...")

    finally:
        for p in all_clients:
            p.terminate()
            p.join()
        print("✅ Todos los procesos terminados.")
