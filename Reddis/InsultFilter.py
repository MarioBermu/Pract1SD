import redis

# Conectar a Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

filter_queue = "FILTER_QUEUE"
result_queue = "RESULT_QUEUE"

# Lista de insultos a censurar
insults = ["subnormal profundo", "tarado sin neuronas", "pedazo de inútil", "retrasado mental de campeonato",
           "idiota", "torpe", "patán", "zoquete", "burro", "cabezón", "menso", "necio"]

print("Insult Filter Service is running...")

while True:
    # Esperar un mensaje del cliente
    _, text = redis_client.blpop(filter_queue)

    # Censurar los insultos
    for insult in insults:
        text = text.replace(insult, "CENSORED")

    # Guardar el texto censurado en Redis
    redis_client.rpush(result_queue, text)
    print(f"Processed text: {text}")
