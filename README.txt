1. Para ejecutar el test de speedrun de pyro y XMLRCP:

Entrar en la carpeta Tests y abrir 3 terminales. 
En la primera ejecutaremos: 
python3 run_servers.py <num_nodos> (Primero haremos con uno, luego dos y asi todos los que se deseen)

En la segunda ejecutaremos los clientes del insult_server: 
python3 run_clients.py <num_nodos> (Igual que en el server)

Y en la tercera ejecutaremos los clientes del insult_filter: 
python3 run_clients_filter.py <num_nodos> (Igual que en el server)

2. Para el speedrun del reddis, solo hace falta ejecutar el Speedup.py que hay en la carpeta Reddis.
3. Y para el speedrun del rabbitmq, solo hace falta ejecutar el Speedup.py que hay en la carpeta RabbitMQ.

4. Por ultimo, para ejecutar el Dynamic scaling using message arrival rate, lo hemos hecho con el RabbitMQ. 
Primero hay que ejecutar el run_servers.py de la carpeta de Rabbit, luego el archivo run_clients.py y por ultimo, 
cuando se crea que ya ha estado el tiempo suficiente se puede parar el cliente para ver como bajan los nodos y luego
se ejecuta la grafica ejecutando el plot_dynamic.py.
