import matplotlib.pyplot as plt
import pandas as pd
import os
import json

# Buscar el último archivo JSON generado
json_files = sorted([f for f in os.listdir('.') if f.startswith("scaling_metrics_") and f.endswith(".json")])
if not json_files:
    print("❌ No se encontró ningún archivo de métricas .json.")
    exit()

latest_json = json_files[-1]
print(f"📊 Usando archivo de métricas: {latest_json}")

# Leer el JSON como DataFrame
with open(latest_json, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Graficar número de workers
plt.figure(figsize=(10, 6))
plt.plot(df["time"], df["insult_workers"], label="InsultService Workers")
plt.plot(df["time"], df["filter_workers"], label="FilterService Workers")
plt.xlabel("Tiempo (s)")
plt.ylabel("Número de Workers")
plt.title("Escalado Dinámico: Workers a lo largo del tiempo")
plt.legend()
plt.grid(True)
plt.tight_layout()
#plt.savefig("workers_over_time.png")
plt.show()

# Graficar backlog
plt.figure(figsize=(10, 6))
plt.plot(df["time"], df["insult_backlog"], label="InsultService Backlog")
plt.plot(df["time"], df["filter_backlog"], label="FilterService Backlog")
plt.xlabel("Tiempo (s)")
plt.ylabel("Mensajes en cola")
plt.title("Backlog de colas a lo largo del tiempo")
plt.legend()
plt.grid(True)
plt.tight_layout()
#plt.savefig("backlog_over_time.png")
plt.show()
