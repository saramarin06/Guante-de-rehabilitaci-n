# Python para visualizar datos seriales del ESP32 en tiempo real

import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# =========================
# CONFIGURACION PUERTO SERIAL
# =========================
# Cambia COM5 por el puerto donde aparece tu ESP32
ser = serial.Serial('COM3', 115200)

# =========================
# VARIABLES PARA GRAFICA
# =========================
max_puntos = 50

angulo1_hist = deque([0]*max_puntos, maxlen=max_puntos)
angulo2_hist = deque([0]*max_puntos, maxlen=max_puntos)
rom1_hist = deque([0]*max_puntos, maxlen=max_puntos)
rom2_hist = deque([0]*max_puntos, maxlen=max_puntos)

reps1 = 0
reps2 = 0

# =========================
# CONFIGURACION FIGURA
# =========================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

linea1, = ax1.plot(angulo1_hist, label='Ángulo Dedo 1')
linea3, = ax1.plot(rom1_hist, label='ROM Dedo 1')

linea2, = ax2.plot(angulo2_hist, label='Ángulo Dedo 2')
linea4, = ax2.plot(rom2_hist, label='ROM Dedo 2')

ax1.set_ylim(0, 100)
ax1.set_xlim(0, max_puntos)
ax1.set_title('Dedo 1')
ax1.set_xlabel('Muestras')
ax1.set_ylabel('Ángulo / ROM')
ax1.legend()
ax1.grid(True)

ax2.set_ylim(0, 100)
ax2.set_xlim(0, max_puntos)
ax2.set_title('Dedo 2')
ax2.set_xlabel('Muestras')
ax2.set_ylabel('Ángulo / ROM')
ax2.legend()
ax2.grid(True)

texto_info = fig.text(
    0.5,
    0.02,
    '',
    ha='center',
    fontsize=11,
    bbox=dict(facecolor='lightgray', alpha=0.7)
)

plt.tight_layout(rect=[0, 0.08, 1, 1])

# =========================
# FUNCION DE ACTUALIZACION
# =========================
def actualizar(frame):
    global reps1, reps2

    try:
        linea = ser.readline().decode('utf-8').strip()
        print(linea)

        datos = linea.split(',')

        # Formato esperado:
        # D1,angulo1,rom1,reps1,volt1,adc1,D2,angulo2,rom2,reps2,volt2,adc2

        if len(datos) >= 12:
            angulo1 = float(datos[1])
            rom1 = float(datos[2])
            reps1 = int(float(datos[3]))

            angulo2 = float(datos[7])
            rom2 = float(datos[8])
            reps2 = int(float(datos[9]))

            angulo1_hist.append(angulo1)
            angulo2_hist.append(angulo2)
            rom1_hist.append(rom1)
            rom2_hist.append(rom2)

            linea1.set_ydata(angulo1_hist)
            linea1.set_xdata(range(len(angulo1_hist)))

            linea2.set_ydata(angulo2_hist)
            linea2.set_xdata(range(len(angulo2_hist)))

            linea3.set_ydata(rom1_hist)
            linea3.set_xdata(range(len(rom1_hist)))

            linea4.set_ydata(rom2_hist)
            linea4.set_xdata(range(len(rom2_hist)))

            ax1.set_xlim(0, max_puntos)
            ax2.set_xlim(0, max_puntos)

            texto_info.set_text(
                f'Dedo 1  |  Repeticiones: {reps1}  |  ROM: {rom1:.1f}°'
                f'Dedo 2  |  Repeticiones: {reps2}  |  ROM: {rom2:.1f}°'
            )

    except Exception as e:
        print('Error:', e)

    return linea1, linea2, linea3, linea4, texto_info

# =========================
# ANIMACION
# =========================
ani = FuncAnimation(fig, actualizar, interval=50)
plt.show()


