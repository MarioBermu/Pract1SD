import xmlrpc.client
import time

# Connect to the Insult Server
s = xmlrpc.client.ServerProxy('http://localhost:8000')

# Register subscribers
s.add_subscriber('http://localhost:8001')
s.add_subscriber('http://localhost:8002')
s.add_subscriber('http://localhost:8003')

# List of insults to send
insults = [
    "Eres tan lento que cuando llegas, ya me fui.",
    "Tienes menos futuro que una piedra en el aire.",
    "Eres más inútil que un lápiz sin punta.",
    "Tienes menos gracia que un semáforo en ámbar."
]

# Send insults every 3 seconds
for insult in insults:
    print(s.add_insult(insult))
    time.sleep(3)
