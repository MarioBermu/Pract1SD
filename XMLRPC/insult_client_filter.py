import xmlrpc.client

# Conectar con el servidor XML-RPC
server = xmlrpc.client.ServerProxy("http://localhost:8001")

# Lista de textos que el cliente enviará para filtrar
texts = [
    "Eres un idiota total",
    "No seas torpe",
    "Ese burro no entiende nada",
    "Eres muy inteligente",
    "Oye necio, hazlo bien"
]

# Enviar los textos al servidor y recibir las versiones filtradas
for text in texts:
    filtered_text = server.filter_text(text)
    print(f"Original: {text} -> Filtrado: {filtered_text}")

# Recuperar la lista completa de textos filtrados
filtered_list = server.get_filtered_texts()
print("\nLista de textos filtrados almacenados:")
for t in filtered_list:
    print(t)
