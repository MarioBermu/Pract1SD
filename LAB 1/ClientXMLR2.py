import xmlrpc.client

# Connect to the server
s = xmlrpc.client.ServerProxy('http://localhost:8000')

# Add some insults
#print(s.add_insult("Eres un tonto y no me haces gracia."))
#print(s.add_insult("Tienes menos futuro que un submariono descapotable."))
#print(s.add_insult("Eres mas inutil que las mangas de un chaleco."))
#print(s.add_insult("Tienes menos luces que un barco pirata."))

# Get the list of insults
print(s.get_insults())

# Get a random insult
#print(s.insult_me())