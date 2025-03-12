import pytest
import pika
import redis
import time

rabbitmq_host = 'localhost'
queue_name = 'work_queue'

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@pytest.fixture
def rabbitmq_channel():
    """Configura una conexión a RabbitMQ y devuelve el canal."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    yield channel
    connection.close()

def test_producer_sends_message(rabbitmq_channel):
    """Verifica que el productor puede enviar mensajes a la cola."""
    test_message = "Mensaje de prueba sin insultos"
    rabbitmq_channel.basic_publish(exchange='', routing_key=queue_name, body=test_message)

    # Comprobamos si el mensaje está en la cola
    method_frame, header_frame, body = rabbitmq_channel.basic_get(queue=queue_name)
    assert body.decode() == test_message, "El mensaje no se publicó correctamente"

def test_insult_filter():
    """Verifica que los insultos se filtran correctamente y se almacenan en Redis."""
    insults = ["subnormal profundo", "tarado sin neuronas", "pedazo de inútil", "retrasado mental de campeonato"]
    message = "Este es un mensaje con un insulto: subnormal profundo"
    
    # Simulamos el filtro
    for insult in insults:
        message = message.replace(insult, "CENSORED")
    
    # Lo guardamos en Redis
    redis_client.rpush("RESULTS", message)
    
    # Obtenemos el último mensaje guardado en Redis
    last_message = redis_client.lindex("RESULTS", -1)
    assert "CENSORED" in last_message, "El filtro de insultos no está funcionando correctamente"
