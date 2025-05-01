import matplotlib.pyplot as plt
import pandas as pd
import os
import json

# Buscar el último archivo JSON generado
json_files = sorted([f for f in os.listdir('.') if f.startswith("scaling_metrics_") and f.endswith(".json")])
if not json_files:
    print(" No se encontró ningún archivo de métricas .json.")
    exit()

latest_json = json_files[-1]
print(f" Usando archivo de métricas: {latest_json}")

# Leer el JSON como DataFrame
with open(latest_json, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Convertir la columna 'time' (timestamp UNIX) a datetime
df["time"] = pd.to_datetime(df["time"], unit='s')
df.set_index("time", inplace=True)

# Forzar columnas numéricas por si acaso
cols_to_convert = [
    "insult_workers", "filter_workers",
    "lambda_insult", "lambda_filter",
    "queue_insult_backlog", "queue_filter_backlog"
]
for col in cols_to_convert:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# === GRÁFICO 1: Número de Workers ===
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["insult_workers"], label="InsultService Workers", linewidth=2)
plt.plot(df.index, df["filter_workers"], label="FilterService Workers", linewidth=2)
plt.xlabel("Tiempo")
plt.ylabel("Número de Workers")
plt.title("Escalado Dinámico: Workers a lo largo del tiempo")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === GRÁFICO 2: Tasas de llegada (λ) ===
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["lambda_insult"], label="λ InsultService", linewidth=2)
plt.plot(df.index, df["lambda_filter"], label="λ FilterService", linewidth=2)
plt.xlabel("Tiempo")
plt.ylabel("Tasa de llegada (mensajes/s)")
plt.title("Tasa de llegada de mensajes a lo largo del tiempo")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === GRÁFICO 3: Backlog de colas (si existe) ===
if "queue_insult_backlog" in df.columns and "queue_filter_backlog" in df.columns:
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["queue_insult_backlog"], label="Backlog Insult Queue", linewidth=2)
    plt.plot(df.index, df["queue_filter_backlog"], label="Backlog Filter Queue", linewidth=2)
    plt.xlabel("Tiempo")
    plt.ylabel("Mensajes pendientes en cola")
    plt.title("Backlog en RabbitMQ a lo largo del tiempo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ No se encontraron columnas de backlog en el JSON.")
