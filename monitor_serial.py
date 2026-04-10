# Python para visualizar datos seriales del ESP32 en tiempo real

import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# =========================
# CONFIGURACION PUERTO SERIAL
# =========================
ser = serial.Serial('COM3', 115200)

# =========================
# VARIABLES PARA GRAFICA
# =========================
max_puntos = 50

angulo1_hist = deque([0]*max_puntos, maxlen=max_puntos)
rom1_hist = deque([0]*max_puntos, maxlen=max_puntos)

angulo2_hist = deque([0]*max_puntos, maxlen=max_puntos)
rom2_hist = deque([0]*max_puntos, maxlen=max_puntos)

angulo3_hist = deque([0]*max_puntos, maxlen=max_puntos)
rom3_hist = deque([0]*max_puntos, maxlen=max_puntos)

reps1, reps2, reps3 = 0, 0, 0
dedo_en_matriz = 1

# =========================
# CONFIGURACION FIGURA
# =========================
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

linea1, = ax1.plot(angulo1_hist, label='Ángulo Dedo 1', color='blue')
linea_rom1, = ax1.plot(rom1_hist, label='ROM Dedo 1', color='orange')

linea2, = ax2.plot(angulo2_hist, label='Ángulo Dedo 2', color='green')
linea_rom2, = ax2.plot(rom2_hist, label='ROM Dedo 2', color='red')

linea3, = ax3.plot(angulo3_hist, label='Ángulo Dedo 3', color='purple')
linea_rom3, = ax3.plot(rom3_hist, label='ROM Dedo 3', color='brown')

for ax, titulo in zip([ax1, ax2, ax3], ['Dedo 1', 'Dedo 2', 'Dedo 3']):
    ax.set_ylim(0, 100)
    ax.set_xlim(0, max_puntos)
    ax.set_title(titulo)
    ax.set_xlabel('Muestras')
    ax.set_ylabel('Ángulo / ROM')
    ax.legend(loc='upper right')
    ax.grid(True)

texto_info = fig.text(
    0.5, 0.02, '', ha='center', fontsize=11,
    bbox=dict(facecolor='lightgray', alpha=0.7)
)

plt.tight_layout(rect=[0, 0.10, 1, 1])

# =========================
# FUNCION DE ACTUALIZACION
# =========================
def actualizar(frame):
    global reps1, reps2, reps3, dedo_en_matriz

    try:
        linea_valida = None
        
        # LA MAGIA ESTÁ AQUÍ:
        # Vaciamos el buffer leyendo todo lo que haya acumulado
        # y nos quedamos ÚNICAMENTE con la última línea que llegó.
        while ser.in_waiting > 0:
            linea_valida = ser.readline().decode('utf-8').strip()

        # Solo actualizamos la gráfica si logramos rescatar una línea nueva
        if linea_valida:
            datos = linea_valida.split(',')

            if len(datos) >= 20:
                # Dedo 1
                angulo1 = float(datos[1])
                rom1 = float(datos[2])
                reps1 = int(float(datos[3]))

                # Dedo 2
                angulo2 = float(datos[7])
                rom2 = float(datos[8])
                reps2 = int(float(datos[9]))

                # Dedo 3
                angulo3 = float(datos[13])
                rom3 = float(datos[14])
                reps3 = int(float(datos[15]))
                
                dedo_en_matriz = int(float(datos[19]))

                angulo1_hist.append(angulo1)
                rom1_hist.append(rom1)
                angulo2_hist.append(angulo2)
                rom2_hist.append(rom2)
                angulo3_hist.append(angulo3)
                rom3_hist.append(rom3)

                linea1.set_ydata(angulo1_hist)
                linea_rom1.set_ydata(rom1_hist)

                linea2.set_ydata(angulo2_hist)
                linea_rom2.set_ydata(rom2_hist)

                linea3.set_ydata(angulo3_hist)
                linea_rom3.set_ydata(rom3_hist)

                info_str = (
                    f"Dedo 1 | Repeticiones: {reps1} | ROM: {rom1:.1f}°   ---   "
                    f"Dedo 2 | Repeticiones: {reps2} | ROM: {rom2:.1f}°   ---   "
                    f"Dedo 3 | Repeticiones: {reps3} | ROM: {rom3:.1f}°\n"
                    f"-> Mostrando en Matriz LED Física: DEDO {dedo_en_matriz} <-"
                )
                texto_info.set_text(info_str)

    except Exception as e:
        # Silenciamos errores menores de lectura para que no traben la gráfica
        pass

    return linea1, linea_rom1, linea2, linea_rom2, linea3, linea_rom3, texto_info

# =========================
# ANIMACION
# =========================
# Bajamos el intervalo a 20ms para que intente refrescar más rápido
ani = FuncAnimation(fig, actualizar, interval=20, cache_frame_data=False)
plt.show()