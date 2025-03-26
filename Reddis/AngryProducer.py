import redis
import time

# Conectar a Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

filter_queue = "FILTER_QUEUE"
result_queue = "RESULT_QUEUE"

# Lista de textos con insultos
texts = [
    "Eres más torpe que un burro con patines, de verdad, cada cosa que haces demuestra lo zoquete que eres.",
    "Menso como siempre, te las das de listo pero no logras hacer nada bien. Es increíble cómo puedes ser tan cabezón y necio.",
    "Si la estupidez fuera un arte, tú serías el maestro supremo. No hay nadie más zoquete, torpe y desesperante que tú.",
    "Nunca había visto a alguien tan patán en mi vida, es que no das una. Eres el claro ejemplo de por qué algunas personas simplemente no deberían intentar pensar.",
    "Cada vez que hablas, se me confirma que eres un idiota sin solución. No importa cuánto intentes parecer inteligente, sigues siendo un pedazo de inútil."
]

# Enviar los 5 textos al filtro
for text in texts:
    redis_client.rpush(filter_queue, text)  # Enviar al filtro
    print(f"Sent: {text}")

# Esperar un momento para que el filtro los procese
time.sleep(2)

# Recibir los 5 textos censurados
for _ in range(5):
    censored_text = redis_client.blpop(result_queue, timeout=5)
    if censored_text:
        print(f"Censored: {censored_text[1]}")
    else:
        print("No response from filter.")

print("Client finished execution.")
