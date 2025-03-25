import Pyro4

@Pyro4.expose
class InsultFilterService:
    def __init__(self):
        self.filtered_texts = []
        self.insult_words = {"tonto", "idiota", "torpe", "burro"}  # Lista de insultos

    def filter_text(self, text):
        """Reemplaza insultos en el texto con 'CENSORED' y lo almacena."""
        words = text.split()
        censored_text = " ".join("CENSORED" if word.lower() in self.insult_words else word for word in words)
        self.filtered_texts.append(censored_text)
        return censored_text

    def get_filtered_texts(self):
        """Devuelve la lista de textos filtrados."""
        return self.filtered_texts

# Inicializar servidor PyRO4
daemon = Pyro4.Daemon()  # Servidor PyRO4
ns = Pyro4.locateNS()  # Buscar el Name Server de PyRO4
uri = daemon.register(InsultFilterService)  # Registrar el objeto remoto
ns.register("insult.filter", uri)  # Registrar el servicio con un nombre

print(f"InsultFilterService corriendo en {uri}")
daemon.requestLoop()  # Mantiene el servidor en ejecución
