import xmlrpc.client
import random
import time

# Conectar con el servidor XML-RPC
server = xmlrpc.client.ServerProxy("http://localhost:8000")

# Lista de insultos que enviará el cliente
insults = ["Idiota", "Torpe", "Patán", "Zoquete", "Burro", "Cabezón", "Menso", "Necio"]


i=0
# Agregar insultos 5 veces
while i<5:
    print(server.store_insult(random.choice(insults)))
    i += 1
# Obtener la lista de insultos
insult_list = server.get_insult_list()
print("Lista de insultos:", insult_list)

try:
    while True:
        random_insult = server.get_random_insult()
        print("Insulto aleatorio:", random_insult)
        time.sleep(3)  # Espera 3 segundos antes de la siguiente solicitud
except KeyboardInterrupt:
    insults = server.get_insult_list()
    print("Lista de insultos:", insults)
    print("\nCliente detenido por el usuario.")
