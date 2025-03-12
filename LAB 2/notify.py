import Pyro4

# Conectar con el servidor observable
observable = Pyro4.Proxy("PYRONAME:example.observable")

# Enviar un mensaje de prueba
observable.notify_observers("Hello, Observers!")
print("Notification sent.")
