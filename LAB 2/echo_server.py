import Pyro4

# Exponer la clase para que pueda ser accedida remotamente
@Pyro4.expose
class EchoServer:
    def echo(self, message):
        print(f"Received message: {message}")
        return f"Echo: {message}"

# Conectar el servidor al Name Server
def start_server():
    daemon = Pyro4.Daemon()  # Crear el servidor Pyro
    ns = Pyro4.locateNS()  # Conectarse al Name Server
    uri = daemon.register(EchoServer())  # Registrar el objeto remoto
    ns.register("echo.server", uri)  # Asignarle un nombre en el Name Server
    print("EchoServer running...")
    daemon.requestLoop()  # Mantener el servidor en ejecución

if __name__ == "__main__":
    start_server()
