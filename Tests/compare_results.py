import json
import matplotlib.pyplot as plt
import numpy as np

def load_results(filename="results.json"):
    with open(filename, "r") as file:
        return json.load(file)

def calculate_speedup(results):
    """Calcula y grafica el speedup para Pyro4 y XML-RPC."""
    services = {"Pyro4": [], "XML-RPC": []}
    
    for entry in results:
        if entry["operation"] == "send":
            services[entry["service"].strip()].append(entry["time"])
    
    avg_times = {service: np.mean(times) for service, times in services.items()}
    
    T1 = max(avg_times.values())  # Consideramos el mayor tiempo como referencia para speedup
    speedups = {service: T1 / avg_times[service] for service in avg_times}
    
    plt.bar(speedups.keys(), speedups.values(), color=["blue", "red"])
    plt.xlabel("Tecnología")
    plt.ylabel("Speedup")
    plt.title("Comparación de Speedup")
    plt.show()

def calculate_dynamic_scaling(results, lambda_rate=10, C=5, B=20, T_r=2):
    """Calcula y grafica el número de trabajadores necesarios para escalado dinámico."""
    services = {"Pyro4": [], "XML-RPC": []}
    
    for entry in results:
        if entry["operation"] == "send":
            services[entry["service"].strip()].append(entry["time"])
    
    avg_processing_time = {service: np.mean(times) for service, times in services.items()}
    
    N_msg_arrival = {service: np.ceil((lambda_rate * avg_processing_time[service]) / C) for service in avg_processing_time}
    N_backlog = {service: np.ceil((B + (lambda_rate * T_r)) / C) for service in avg_processing_time}
    
    x = np.arange(len(avg_processing_time))
    width = 0.4
    
    fig, ax = plt.subplots()
    ax.bar(x - width/2, N_msg_arrival.values(), width, label="Escalado por llegada")
    ax.bar(x + width/2, N_backlog.values(), width, label="Escalado con backlog")
    
    ax.set_xlabel("Tecnología")
    ax.set_ylabel("Número de Trabajadores Requeridos")
    ax.set_title("Comparación de Escalabilidad Dinámica")
    ax.set_xticks(x)
    ax.set_xticklabels(N_msg_arrival.keys())
    ax.legend()
    
    plt.show()

if __name__ == "__main__":
    results = load_results()
    calculate_speedup(results)
    calculate_dynamic_scaling(results)
