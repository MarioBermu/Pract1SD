
import multiprocessing
import time
import json
import pika
import random
import argparse

rabbitmq_host = 'localhost'
insult_receive_queue = 'insult_receive_queue'
text_receive_queue = 'text_receive_queue'

insult_list = ["Idiota", "Torpe", "Patán", "Burro", "Zoquete", "Cabezón", "Necio"]

def send_insults(rate):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    delay = 1.0 / rate
    try:
        while True:
            insult = random.choice(insult_list)
            data = {"action": "send_insult", "insult": insult}
            channel.basic_publish(exchange='', routing_key=insult_receive_queue, body=json.dumps(data))
            time.sleep(delay)
    except KeyboardInterrupt:
        connection.close()

def send_texts(rate):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    delay = 1.0 / rate
    try:
        while True:
            sentence = "Eres un " + random.choice(insult_list)
            data = {"action": "send_text", "text": sentence}
            channel.basic_publish(exchange='', routing_key=text_receive_queue, body=json.dumps(data))
            time.sleep(delay)
    except KeyboardInterrupt:
        connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress test clients for insult service")
    parser.add_argument("--insult_clients", type=int, default=10, help="Número de procesos de envío de insultos")
    parser.add_argument("--text_clients", type=int, default=10, help="Número de procesos de envío de textos")
    parser.add_argument("--insult_rate", type=int, default=100, help="Mensajes por segundo por proceso de insultos")
    parser.add_argument("--text_rate", type=int, default=50, help="Mensajes por segundo por proceso de textos")
    parser.add_argument("--duration", type=int, default=60, help="Duración total del test en segundos")
    args = parser.parse_args()

    insult_processes = [
        multiprocessing.Process(target=send_insults, args=(args.insult_rate,))
        for _ in range(args.insult_clients)
    ]
    text_processes = [
        multiprocessing.Process(target=send_texts, args=(args.text_rate,))
        for _ in range(args.text_clients)
    ]
    all_processes = insult_processes + text_processes

    for p in all_processes:
        p.start()

    try:
        print(f"🚀 Ejecutando prueba de carga durante {args.duration} segundos...")
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("⛔ Interrumpido manualmente.")

    print("🛑 Finalizando procesos...")
    for p in all_processes:
        p.terminate()
        p.join()
    print("✅ Todos los procesos finalizados.")
