import json
import matplotlib.pyplot as plt

# Cargar los datos desde los archivos JSON
def load_results(file_path):
    """Carga resultados desde un archivo JSON."""
    with open(file_path, "r") as file:
        return json.load(file)

# Obtener tiempos promedios de ejecución para cada número de nodos
def calculate_avg_times(results):
    """Calcula tiempos promedios agrupados por número de nodos."""
    times_per_node = {}
    
    for entry in results:
        num_nodes = entry.get("num_nodes", 1)  # Valor por defecto: 1
        time = entry.get("time", 0)  # Asegurar que haya un tiempo registrado
        
        if num_nodes not in times_per_node:
            times_per_node[num_nodes] = []
        times_per_node[num_nodes].append(time)

    # Calcular promedios
    avg_times = {n: sum(times) / len(times) for n, times in times_per_node.items()}
    
    return dict(sorted(avg_times.items()))  # Ordenar por número de nodos

# Cargar archivos JSON
results_service = load_results("results.json")
results_filter = load_results("results_filter.json")

# Calcular tiempos promedios
times_service = calculate_avg_times(results_service)
times_filter = calculate_avg_times(results_filter)

# Usar tiempos del servicio como referencia para T1
T1_service = times_service.get(1, None)
T1_filter = times_filter.get(1, None)

# Evitar errores si no hay datos de un solo nodo
if T1_service is None or T1_filter is None:
    raise ValueError("No hay datos para 1 nodo, no se puede calcular el speedup.")

# Calcular speedup para cada número de nodos
speedup_service = {n: (T1_service / Tn) if Tn > 0 else 0 for n, Tn in times_service.items()}
speedup_filter = {n: (T1_filter / Tn) if Tn > 0 else 0 for n, Tn in times_filter.items()}

# Graficar Speedup vs. Número de nodos
plt.figure(figsize=(8, 5))
plt.plot(speedup_service.keys(), speedup_service.values(), label="InsultService", marker="o", linestyle="-")
plt.plot(speedup_filter.keys(), speedup_filter.values(), label="InsultFilter", marker="x", linestyle="--")

plt.xlabel("Número de nodos")
plt.ylabel("Speedup")
plt.title("Speedup vs. Número de Nodos")
plt.legend()
plt.grid(True)

plt.show()
