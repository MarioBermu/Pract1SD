import redis
from flask import Flask, jsonify

# Conectar a Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insult_queue"
insult_list = "INSULTS"

app = Flask(__name__)

print("Consumer is waiting for insults...")

while True:
    insult = client.blpop(queue_name, timeout=0)  # Espera hasta recibir un insulto
    insult_text = insult[1]

    # Verificar si el insulto ya está en la lista
    if insult_text not in client.lrange(insult_list, 0, -1):
        client.rpush(insult_list, insult_text)  # Agregar insulto si es nuevo
        print(f"Consumed and stored: {insult_text}")
    else:
        print(f"Duplicated insult ignored: {insult_text}")

# Nuevo endpoint para obtener la lista de insultos
@app.route('/insults', methods=['GET'])
def get_insults():
    insults = client.lrange(insult_list, 0, -1)  # Obtener todos los insultos almacenados
    return jsonify(insults)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
