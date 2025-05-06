
import time
import json
import subprocess
import pika
import matplotlib.pyplot as plt

# Configuration
NUM_SERVERS_LIST = [1, 2, 3]
RESULTS_FILE = "results.json"
RESULTS_FILE_FILTER = "results_filter.json"
BASE_MESSAGES = 5000  # Base number of messages for 1 server

RABBITMQ_HOST = 'localhost'
INSULT_RECV_QUEUE = 'insult_receive_queue'
TEXT_RECV_QUEUE = 'text_receive_queue'
TEXT_SEND_QUEUE = 'text_send_queue'

# Helper functions for RabbitMQ

def purge_queue(channel, queue_name):
    channel.queue_purge(queue=queue_name)

def get_queue_length(channel, queue_name):
    q = channel.queue_declare(queue=queue_name, passive=True)
    return q.method.message_count

# Test InsultService: send all messages first, then start servers

def run_test_service():
    results = {}
    baseline = None
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = conn.channel()
    channel.queue_declare(queue=INSULT_RECV_QUEUE, durable=False)

    for n in NUM_SERVERS_LIST:
        total_msgs = int(BASE_MESSAGES * (1 + 0.5 * (n - 1)))
        print(f"Testing InsultService: {n} server(s), {total_msgs} messages")
        purge_queue(channel, INSULT_RECV_QUEUE)

        # 1) Send all insults to queue
        for _ in range(total_msgs):
            payload = json.dumps({"action": "send_insult", "insult": "Menso"})
            channel.basic_publish(exchange='', routing_key=INSULT_RECV_QUEUE, body=payload)

        # 2) Start servers to process
        servers = [subprocess.Popen(['python', 'insult_service.py']) for _ in range(n)]
        time.sleep(1)  # allow processes to connect

        # 3) Measure processing time
        start = time.time()
        while get_queue_length(channel, INSULT_RECV_QUEUE) > 0:
            time.sleep(0.01)
        elapsed = time.time() - start

        # 4) Terminate servers
        for p in servers:
            p.terminate()

        if n == 1:
            baseline = elapsed
        speedup = baseline / elapsed if baseline else 1.0
        results[n] = speedup
        print(f"  Time: {elapsed:.2f}s, Speedup: {speedup:.2f}")

    conn.close()
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f)

# Test InsultFilter: send all messages first, then start filters

def run_test_filter():
    results = {}
    baseline = None
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = conn.channel()
    channel.queue_declare(queue=TEXT_RECV_QUEUE, durable=False)
    channel.queue_declare(queue=TEXT_SEND_QUEUE, durable=False)

    for n in NUM_SERVERS_LIST:
        total_msgs = int(BASE_MESSAGES * (1 + 0.5 * (n - 1)))
        print(f"Testing InsultFilter: {n} process(es), {total_msgs} messages")
        purge_queue(channel, TEXT_RECV_QUEUE)
        purge_queue(channel, TEXT_SEND_QUEUE)

        # 1) Send all texts to queue
        for _ in range(total_msgs):
            payload = json.dumps({"action": "send_text", "text": "Hola Menso"})
            channel.basic_publish(exchange='', routing_key=TEXT_RECV_QUEUE, body=payload)

        # 2) Start filter processes
        filters = [subprocess.Popen(['python', 'insult_filter.py']) for _ in range(n)]
        time.sleep(1)

        # 3) Measure acknowledgments received
        start = time.time()
        received = 0
        while received < total_msgs:
            method, header, body = channel.basic_get(queue=TEXT_SEND_QUEUE, auto_ack=True)
            if body:
                received += 1
            else:
                time.sleep(0.01)
        elapsed = time.time() - start

        # 4) Terminate filters
        for p in filters:
            p.terminate()

        if n == 1:
            baseline = elapsed
        speedup = baseline / elapsed if baseline else 1.0
        results[n] = speedup
        print(f"  Time: {elapsed:.2f}s, Speedup: {speedup:.2f}")

    conn.close()
    with open(RESULTS_FILE_FILTER, 'w') as f:
        json.dump(results, f)

# Plot results

def plot_results():
    with open(RESULTS_FILE, 'r') as f:
        res = json.load(f)
    with open(RESULTS_FILE_FILTER, 'r') as f:
        res_f = json.load(f)

    servers = sorted(map(int, res.keys()))
    speedups = [res[str(s)] for s in servers]
    speedups_f = [res_f[str(s)] for s in servers]

    plt.figure(figsize=(8,5))
    plt.plot(servers, speedups, marker='o', label="InsultService")
    plt.plot(servers, speedups_f, marker='s', label="InsultFilter")
    plt.xticks(servers)
    plt.xlabel("Number of processes")
    plt.ylabel("Speedup")
    plt.title(f"Speedup for {BASE_MESSAGES} msgs/unit (50% increase per server)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_test_service()
    run_test_filter()
    plot_results()
