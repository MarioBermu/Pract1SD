import Pyro4

# Conectar con el servidor
remote_object = Pyro4.Proxy("PYRONAME:example.remote.object")

# Llamar a los métodos remotos
print(remote_object.greet("Mario"))
print(f"2 + 3 = {remote_object.add(2, 3)}")

# Obtener métodos disponibles (introspección dinámica)
print("Available methods:", remote_object._pyroMethods)
