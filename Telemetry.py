import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

TRACK_SCALE = 10.0 # from settings import TRACK_SCALE

def format_time(t):
    minutes = int(t // 60)
    seconds = int(t % 60)
    millis  = int((t - int(t)) * 1000)
    return f"{minutes:02}:{seconds:02}.{millis:03}"

def plot_telemetry(json_file, track_image_path):
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No se encontró el archivo de telemetría.")
        return

    telemetry = data["telemetry"]
    lap_time = data["lap_time"]
    splits = data["splits"]

    # Extraer datos
    x = np.array([p["x"] for p in telemetry])
    y = np.array([p["y"] for p in telemetry])
    th = np.array([p["thr"] for p in telemetry])
    br = np.array([p["brk"] for p in telemetry])
    rev = np.array([p["rev"] for p in telemetry])

    # Configurar el gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Cargar y mostrar la imagen de la pista
    img = mpimg.imread(track_image_path)
    # Reescalamos la imagen según el TRACK_SCALE para que coincida con las coordenadas
    h, w = img.shape[:2]
    ax.imshow(img, extent=[0, w * TRACK_SCALE, h * TRACK_SCALE, 0], alpha=0.7)

    # Dibujar la trayectoria con colores dinámicos
    for i in range(len(x) - 1):
        # Color dinámico basado en inputs (R=Brake, G=Throttle, B=Reverse)
        color = (br[i], th[i], rev[i])
        
        # Si no hay ningún input, usamos gris para la inercia
        if sum(color) == 0:
            color = (0.5, 0.5, 0.5)
        else:
            # Normalizar para que sea un color válido si hay combinación
            max_val = max(color)
            color = tuple(c/max_val for c in color)

        ax.plot(x[i:i+2], y[i:i+2], color=color, linewidth=2)

    # Añadir marcadores para los sectores (Coordenadas base * SCALE)
    sectors = [(226, 102), (205, 420), (467, 174)]
    for i, (p1, p2) in enumerate(sectors):
        sx = p1 * TRACK_SCALE
        sy = p2 * TRACK_SCALE   
        ax.text(sx, sy, f"S{i+1}: {splits[i]:.3f}s", color='white', 
                fontsize=10, fontweight='bold', bbox=dict(facecolor='black', alpha=0.5))

    # Título y tiempo total
    plt.title(f"Telemetría de Mejor Vuelta: {format_time(lap_time)}", fontsize=15)
    ax.set_xlabel("X (Píxeles)")
    ax.set_ylabel("Y (Píxeles)")
    
    # Leyenda manual
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='green', lw=2),
                    Line2D([0], [0], color='red', lw=2),
                    Line2D([0], [0], color='blue', lw=2),
                    Line2D([0], [0], color='gray', lw=2)]
    ax.legend(custom_lines, ['Acelerando', 'Frenando', 'Reversa', 'Inercia'], loc='upper right')

    plt.show()

if __name__ == "__main__":
    # plot_telemetry("best_lap_record.json", "assets/images/tracks/track_1.png")
    plot_telemetry("Best-Laps/L3.json", "assets/images/tracks/track_1.png")