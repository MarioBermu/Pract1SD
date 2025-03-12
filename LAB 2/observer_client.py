import Pyro4

@Pyro4.expose
class Observer:
    def update(self, message):
        print(f"Received notification: {message}")

# Iniciar el observador y registrarlo en el servidor
def start_observer():
    daemon = Pyro4.Daemon()  # Crear el servidor Pyro
    observer = Observer()
    uri = daemon.register(observer)  # Registrar el observador
    ns = Pyro4.locateNS()  # Conectarse al Name Server
    observable = Pyro4.Proxy(ns.lookup("example.observable"))  # Obtener el objeto observable
    observable.register_observer(uri)  # Registrarse en el servidor
    print("Observer registered and waiting for notifications...")
    daemon.requestLoop()  # Mantenerlo activo para recibir notificaciones

if __name__ == "__main__":
    start_observer()
