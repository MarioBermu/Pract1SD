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

# Crear eje X como número de iteración (0, 1, 2, ...)
df["iteration"] = range(len(df))

# Graficar número de workers
plt.figure(figsize=(10, 6))
plt.plot(df["iteration"], df["insult_workers"], label="InsultService Workers")
plt.plot(df["iteration"], df["filter_workers"], label="FilterService Workers")
plt.xlabel("Iteración")
plt.ylabel("Número de Workers")
plt.title("Escalado Dinámico: Workers a lo largo del tiempo")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Graficar tasas de llegada (lambda)
plt.figure(figsize=(10, 6))
plt.plot(df["iteration"], df["lambda_insult"], label="λ InsultService")
plt.plot(df["iteration"], df["lambda_filter"], label="λ FilterService")
plt.xlabel("Iteración")
plt.ylabel("Tasa de llegada (mensajes/s)")
plt.title("Tasa de llegada de mensajes (λ) a lo largo del tiempo")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Graficar backlog de colas (si existe)
if "queue_insult_backlog" in df.columns and "queue_filter_backlog" in df.columns:
    plt.figure(figsize=(10, 6))
    plt.plot(df["iteration"], df["queue_insult_backlog"], label="Backlog Insult Queue")
    plt.plot(df["iteration"], df["queue_filter_backlog"], label="Backlog Filter Queue")
    plt.xlabel("Iteración")
    plt.ylabel("Mensajes pendientes en cola")
    plt.title("Backlog en RabbitMQ a lo largo del tiempo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Las columnas de backlog no están presentes en el JSON.")
