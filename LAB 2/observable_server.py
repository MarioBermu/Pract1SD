import Pyro4

# Exponer la clase para Pyro4 y permitir una sola instancia
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Observable:
    def __init__(self):
        self.observers = []  # Lista de clientes suscritos

    def register_observer(self, observer_uri):
        """Registra un observador en la lista"""
        self.observers.append(observer_uri)
        print(f"Observer {observer_uri} registered.")
        return f"Observer {observer_uri} registered successfully."

    def unregister_observer(self, observer_uri):
        """Elimina un observador de la lista"""
        if observer_uri in self.observers:
            self.observers.remove(observer_uri)
            print(f"Observer {observer_uri} unregistered.")
            return f"Observer {observer_uri} unregistered successfully."
        return "Observer not found."

    def notify_observers(self, message):
        """Notifica a todos los observadores con un mensaje"""
        for observer_uri in self.observers:
            try:
                observer = Pyro4.Proxy(observer_uri)
                observer.update(message)
            except Exception as e:
                print(f"Failed to notify {observer_uri}: {e}")

# Iniciar el servidor
def start_server():
    daemon = Pyro4.Daemon()  # Crear el servidor Pyro
    ns = Pyro4.locateNS()  # Conectarse al Name Server
    uri = daemon.register(Observable())  # Registrar la clase observable
    ns.register("example.observable", uri)  # Publicarla en el Name Server
    print("ObservableServer running...")
    daemon.requestLoop()  # Mantener el servidor en ejecución

if __name__ == "__main__":
    start_server()
