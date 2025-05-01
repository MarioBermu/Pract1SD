import Pyro4
import os

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultFilterService:
    def __init__(self):
        self.filtered_texts = []
        self.insult_words = {"tonto", "idiota", "torpe", "burro"}
        self.request_count = 0


    def filter_text(self, text):
        self.request_count += 1
        print(f"[PYRO FILTER:{os.getpid()}] Peticiones recibidas: {self.request_count}")

        words = text.split()
        censored_text = " ".join("CENSORED" if word.lower() in self.insult_words else word for word in words)
        self.filtered_texts.append(censored_text)
        return censored_text

    def get_filtered_texts(self):
        return self.filtered_texts

# Inicializar servidor PyRO4
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

filter_service = InsultFilterService()
service_name = f"insult.filter.{os.getpid()}"
uri = daemon.register(filter_service, service_name)
ns.register(service_name, uri)

# Guardar el nombre del servicio registrado para los clientes
with open("active_pyro_filters.txt", "a") as f:
    f.write(service_name + "\n")

print(f"InsultFilterService corriendo en {uri}")
daemon.requestLoop()
