import redis
import time

# Conectar a Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

channel_name = "insult_channel"
insult_list = "INSULTS"

while True:
    insults = client.lrange(insult_list, 0, -1)  # Obtener todos los insultos almacenados

    for insult in insults:
        client.publish(channel_name, insult)  # Publicar insulto
        print(f"Broadcasted: {insult}")
    
    time.sleep(5)  # Esperar antes de volver a enviar
