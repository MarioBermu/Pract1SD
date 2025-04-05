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

def progressive_load(insult_rate, text_rate, max_clients=5, step_time=10):
    insult_processes = []
    text_processes = []

    print(f"🚀 Enviando carga progresiva (hasta {max_clients} procesos por tipo)...")

    for i in range(max_clients):
        insult_proc = multiprocessing.Process(target=send_insults, args=(insult_rate,))
        text_proc = multiprocessing.Process(target=send_texts, args=(text_rate,))
        insult_proc.start()
        text_proc.start()
        insult_processes.append(insult_proc)
        text_processes.append(text_proc)

        print(f"[{i * step_time}s] Activos -> Insultos: {i+1}, Textos: {i+1}")
        time.sleep(step_time)

    print("🟢 Carga establecida. Esperando Ctrl+C para detener...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Deteniendo procesos...")
        for p in insult_processes + text_processes:
            p.terminate()
            p.join()
        print("✅ Todos los procesos finalizados.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente con carga progresiva para escalado dinámico")
    parser.add_argument("--insult_rate", type=int, default=5, help="Mensajes/seg por proceso de insultos")
    parser.add_argument("--text_rate", type=int, default=3, help="Mensajes/seg por proceso de textos")
    parser.add_argument("--max_clients", type=int, default=6, help="Número máximo de procesos por tipo")
    parser.add_argument("--step_time", type=int, default=5, help="Segundos entre procesos nuevos")
    args = parser.parse_args()

    progressive_load(args.insult_rate, args.text_rate, args.max_clients, args.step_time)
