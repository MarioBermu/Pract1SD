from flask import Flask, request, jsonify
import redis
import random

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

INSULTS_KEY = "insults"
r.delete(INSULTS_KEY)
def get_random_insult():
    insults = r.smembers(INSULTS_KEY)
    return random.choice(list(insults)) if insults else "No hay insultos aún"

@app.route('/insult', methods=['POST'])
def receive_insult():
    data = request.json
    insult = data.get("insult")

    if insult and not r.sismember(INSULTS_KEY, insult):
        r.sadd(INSULTS_KEY, insult)

    response_insult = get_random_insult()
    all_insults = list(r.smembers(INSULTS_KEY))

    return jsonify({"response_insult": response_insult, "all_insults": all_insults})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
