import json
import matplotlib.pyplot as plt

RESULTS_FILE = "tests/results.json"
RESULTS_FILE_FILTER = "tests/results_filter.json"

# Mensajes por nodo según tu configuración
MESSAGES_PER_NODE = {
    "Insult Service": {"Pyro4": 10000, "XML-RPC": 5000},
    "Filter Service": {"Pyro4": 400, "XML-RPC": 400},
}

def analyze_speedup(ax, data, title):
    pyro_times = {}
    xmlrpc_times = {}

    for entry in data:
        n = entry["nodes"]
        if entry["service"] == "Pyro4":
            pyro_times.setdefault(n, []).append(entry["time"])
        elif entry["service"] == "XML-RPC":
            xmlrpc_times.setdefault(n, []).append(entry["time"])

    # Calcular promedios por nodo
    avg_pyro = {n: sum(v)/len(v) for n, v in pyro_times.items()}
    avg_xml  = {n: sum(v)/len(v)  for n, v in xmlrpc_times.items()}

    # Calcular speedup
    # El speedup se calcula como el tiempo base dividido por el tiempo actual
    if 1 in avg_pyro and 1 in avg_xml:
        base_pyro = avg_pyro[1]
        base_xml  = avg_xml[1]
        speed_pyro = {n: base_pyro/avg_pyro[n] for n in sorted(avg_pyro)}
        speed_xml  = {n: base_xml/avg_xml[n]   for n in sorted(avg_xml)}

        # Etiquetas que incluyen msgs/nodo
        msgs = MESSAGES_PER_NODE[title]
        pyro_label   = f"Pyro4 ({msgs['Pyro4']} msgs/nodo)"
        xmlrpc_label = f"XML-RPC ({msgs['XML-RPC']} msgs/nodo)"

        # Graficar
        ax.plot(list(speed_pyro), list(speed_pyro.values()),
                label=pyro_label, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
        ax.plot(list(speed_xml), list(speed_xml.values()),
                label=xmlrpc_label, marker='s', color='r', linestyle='--', linewidth=2, markersize=8)

        ax.set_xlabel('Número de Nodos', fontsize=12)
        ax.set_ylabel('Speedup', fontsize=12)
        ax.set_title(f'Speedup vs nodos ({title})', fontsize=14)
        ax.legend()
        ax.grid(True)

if __name__ == "__main__":
    with open(RESULTS_FILE, "r") as f:
        data1 = json.load(f)
    with open(RESULTS_FILE_FILTER, "r") as f:
        data2 = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    analyze_speedup(axes[0], data1, "Insult Service")
    analyze_speedup(axes[1], data2, "Filter Service")
    plt.tight_layout()
    plt.show()
