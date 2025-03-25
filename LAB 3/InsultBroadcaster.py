import redis
import time
import random  # Importar random para elegir insultos aleatorios

# Conectar a Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

channel_name = "insult_channel"
insult_list = "INSULTS"

while True:
    insults = client.lrange(insult_list, 0, -1)  # Obtener todos los insultos almacenados

    if insults:  # Verificar si hay insultos almacenados
        insult = random.choice(insults)  # Seleccionar un insulto aleatorio
        client.publish(channel_name, insult)  # Publicar insulto
        print(f"Broadcasted: {insult}")

    time.sleep(5)  # Esperar 5 segundos antes de volver a enviar
