import Pyro4
import random

@Pyro4.expose
class InsultService:
    def __init__(self):
        self.insults = []

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            return "Insulto agregado"
        return "Insulto ya existe"

    def get_insults(self):
        return self.insults  # Devuelve la lista completa de insultos
    
    def get_random_insult(self):
        if not self.insults:
            return "No hay insultos en la lista."
        return random.choice(self.insults)

# Inicializar servidor PyRO4
daemon = Pyro4.Daemon()  # Servidor PyRO4
ns = Pyro4.locateNS()  # Buscar el Name Server de PyRO4
uri = daemon.register(InsultService)  # Registrar el objeto remoto
ns.register("insult.service", uri)  # Registrar el servicio con un nombre

print(f"InsultService corriendo en {uri}")
daemon.requestLoop()  # Mantiene el servidor en ejecución
