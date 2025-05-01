import Pyro4
import random
import os

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultService:
    def __init__(self):
        self.insults = []
        self.request_count = 0

    def add_insult(self, insult):
        self.request_count += 1
        print(f"[PYRO:{os.getpid()}] Peticiones recibidas: {self.request_count}")

        if insult not in self.insults:
            self.insults.append(insult)
            return "Insulto agregado"
        return "Insulto ya existe"

    def get_insults(self):
        return self.insults

    def get_random_insult(self):
        if not self.insults:
            return "No hay insultos en la lista."
        return random.choice(self.insults)

# Inicializar servidor Pyro4
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

insult_service = InsultService()
service_name = f"insult.service.{os.getpid()}"
uri = daemon.register(insult_service, service_name)
ns.register(service_name, uri)

# Guardar el nombre del servicio registrado para los clientes
with open("active_pyro_services.txt", "a") as f:
    f.write(service_name + "\n")

print(f"InsultService corriendo en {uri}")
daemon.requestLoop()
