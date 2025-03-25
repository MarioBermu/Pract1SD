import Pyro4

# Conectarse al Name Server y buscar el servicio
filter_service = Pyro4.Proxy("PYRONAME:insult.filter")

# Lista de textos de prueba
texts = [
    "Eres un tonto y un idiota",
    "Hoy es un gran día",
    "Ese chico es muy torpe para los deportes",
    "Eres un genio, no un burro",
]

# Enviar los textos para filtrar
for text in texts:
    filtered = filter_service.filter_text(text)
    print(f"Original: {text}")
    print(f"Filtrado: {filtered}\n")

# Obtener la lista de textos filtrados
filtered_texts = filter_service.get_filtered_texts()
print("Lista de textos filtrados:")
for txt in filtered_texts:
    print(txt)
