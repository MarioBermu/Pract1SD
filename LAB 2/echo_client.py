import Pyro4

# Conectarse al Name Server y obtener el objeto remoto
echo_server = Pyro4.Proxy("PYRONAME:echo.server")

# Enviar un mensaje al servidor
response = echo_server.echo("HOLA")
print(response)
