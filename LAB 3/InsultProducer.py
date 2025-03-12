import redis
import time
import random  # Importar la librería random

# Conectar a Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insult_queue"

# Lista de insultos de ejemplo
insults = ["Tonto", "Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"]

while True:
    insult = random.choice(insults)  # Seleccionar un insulto aleatorio
    client.rpush(queue_name, insult)  # Agregar insulto a la cola
    print(f"Produced: {insult}")
    time.sleep(5)  # Esperar 5 segundos antes de enviar el siguiente
