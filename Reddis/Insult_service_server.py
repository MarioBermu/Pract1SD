from flask import Flask, request, jsonify
import redis
import sys

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

INSULTS_KEY = "insults"
r.delete(INSULTS_KEY)

def get_random_insult():
    # Usar comando nativo para muestreo aleatorio en Redis
    return r.srandmember(INSULTS_KEY) or "No hay insultos aún"

@app.route('/insult', methods=['POST'])
def receive_insult():
    data = request.json
    insult = data.get("insult")

    if insult:
        r.sadd(INSULTS_KEY, insult)

    response_insult = get_random_insult()
    return jsonify({"response_insult": response_insult})

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    # Ejecutar con threading para mejorar concurrencia
    app.run(host='0.0.0.0', port=port, threaded=True)
