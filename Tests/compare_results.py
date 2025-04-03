import json
import matplotlib.pyplot as plt

RESULTS_FILE = "tests/results.json"
RESULTS_FILE_FILTER = "tests/results_filter.json"

def analyze_speedup(ax, data, title):
    pyro_times = {}
    xmlrpc_times = {}

    # Clasificar los datos por tipo de servidor
    for entry in data:
        nodes = entry["nodes"]
        server_type = entry["service"]  
        
        if server_type == "Pyro4":
            if nodes not in pyro_times:
                pyro_times[nodes] = []
            pyro_times[nodes].append(entry["time"])
        elif server_type == "XML-RPC":
            if nodes not in xmlrpc_times:
                xmlrpc_times[nodes] = []
            xmlrpc_times[nodes].append(entry["time"])

    avg_pyro_times = {nodes: sum(pyro_times[nodes]) / len(pyro_times[nodes]) for nodes in pyro_times}
    avg_xmlrpc_times = {nodes: sum(xmlrpc_times[nodes]) / len(xmlrpc_times[nodes]) for nodes in xmlrpc_times}

    if 1 in avg_pyro_times and 1 in avg_xmlrpc_times:
        base_time_pyro = avg_pyro_times[1]
        base_time_xmlrpc = avg_xmlrpc_times[1]

        pyro_speedups = {nodes: base_time_pyro / avg_pyro_times[nodes] for nodes in avg_pyro_times}
        xmlrpc_speedups = {nodes: base_time_xmlrpc / avg_xmlrpc_times[nodes] for nodes in avg_xmlrpc_times}

        # Graficar Pyro4
        ax.plot(list(pyro_speedups.keys()), list(pyro_speedups.values()), label='Pyro4', marker='o', color='b', linestyle='-', linewidth=2, markersize=8)

        # Graficar XML-RPC
        ax.plot(list(xmlrpc_speedups.keys()), list(xmlrpc_speedups.values()), label='XML-RPC', marker='s', color='r', linestyle='--', linewidth=2, markersize=8)

        # Etiquetas y título
        ax.set_xlabel('Número de Nodos', fontsize=12)
        ax.set_ylabel('Speedup', fontsize=12)
        ax.set_title(f'Speedup en función del número de nodos ({title})', fontsize=14)
        ax.legend()
        ax.grid(True)

if __name__ == "__main__":
    with open(RESULTS_FILE, "r") as file:
        data1 = json.load(file)
    
    with open(RESULTS_FILE_FILTER, "r") as file:
        data2 = json.load(file)

    # Crear una figura con dos subgráficos (1 fila, 2 columnas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    analyze_speedup(axes[0], data1, "Insult Service")
    analyze_speedup(axes[1], data2, "Filter Service")

    # Mostrar la figura completa con ambas gráficas
    plt.tight_layout()  
    plt.show()
