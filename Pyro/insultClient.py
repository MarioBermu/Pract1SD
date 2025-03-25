import Pyro4
import time
import random

# Conectarse al Name Server y buscar el servicio
insult_service = Pyro4.Proxy("PYRONAME:insult.service")
insults = ["Tonto", "Subnormal", "Zoquete", "Patán", "Idiota", "Tonto"]

i=0
# Agregar insultos 5 veces
while i<5:
    print(insult_service.add_insult(random.choice(insults)))
    i += 1
# Obtener la lista de insultos
insults = insult_service.get_insults()
print("Lista de insultos:", insults)

#random_insult = insult_service.get_random_insult()
#print("Insulto aleatorio:", random_insult)

# Bucle infinito para obtener insultos aleatorios cada 3 segundos
try:
    while True:
        random_insult = insult_service.get_random_insult()
        print("Insulto aleatorio:", random_insult)
        time.sleep(3)  # Espera 3 segundos antes de la siguiente solicitud
except KeyboardInterrupt:
    insults = insult_service.get_insults()
    print("Lista de insultos:", insults)
    print("\nCliente detenido por el usuario.")