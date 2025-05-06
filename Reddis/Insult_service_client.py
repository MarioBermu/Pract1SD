import requests
import random

client_insults = ["Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"]

SERVER_URL = "http://localhost:5000/insult"

for _ in range(5):
    insult = random.choice(client_insults)
    response = requests.post(SERVER_URL, json={"insult": insult})
    
    if response.status_code == 200:
        data = response.json()
        print(f"Cliente envió: {insult}")
        print(f"Servidor respondió: {data['response_insult']}")
        print(f"Lista de insultos en el servidor: {data['all_insults']}\n")