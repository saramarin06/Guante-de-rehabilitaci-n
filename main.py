from machine import Pin, ADC, SPI
from max7219 import Matrix8x8
from time import sleep

# =========================
# CONFIGURACION ADC
# =========================
flex1 = ADC(Pin(34))   # Dedo 1
flex2 = ADC(Pin(35))   # Dedo 2

flex1.atten(ADC.ATTN_11DB)
flex2.atten(ADC.ATTN_11DB)

flex1.width(ADC.WIDTH_12BIT)
flex2.width(ADC.WIDTH_12BIT)

# =========================
# CONFIGURACION MAX7219
# =========================
spi = SPI(
    1,
    baudrate=1000000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(23)
)

cs = Pin(5, Pin.OUT)

display = Matrix8x8(spi, cs, 4)
display.brightness(3)
display.fill(0)
display.show()

# =========================
# VARIABLES DEL SISTEMA
# =========================
rom1 = 0
rom2 = 0

repeticiones1 = 0
repeticiones2 = 0

estado_flexion1 = 0
estado_flexion2 = 0

UMBRAL_ALTO = 60
UMBRAL_BAJO = 20

# =========================
# FUENTE MANUAL DE NUMEROS
# =========================
FONT_3x5 = {
    0: [(0,0),(1,0),(2,0), (0,1),(2,1), (0,2),(2,2), (0,3),(2,3), (0,4),(1,4),(2,4)],
    1: [(1,0), (0,1),(1,1), (1,2), (1,3), (0,4),(1,4),(2,4)],
    2: [(0,0),(1,0),(2,0), (2,1), (0,2),(1,2),(2,2), (0,3), (0,4),(1,4),(2,4)],
    3: [(0,0),(1,0),(2,0), (2,1), (0,2),(1,2),(2,2), (2,3), (0,4),(1,4),(2,4)],
    4: [(0,0),(2,0), (0,1),(2,1), (0,2),(1,2),(2,2), (2,3), (2,4)],
    5: [(0,0),(1,0),(2,0), (0,1), (0,2),(1,2),(2,2), (2,3), (0,4),(1,4),(2,4)],
    6: [(0,0),(1,0),(2,0), (0,1), (0,2),(1,2),(2,2), (0,3),(2,3), (0,4),(1,4),(2,4)],
    7: [(0,0),(1,0),(2,0), (2,1), (2,2), (2,3), (2,4)],
    8: [(0,0),(1,0),(2,0), (0,1),(2,1), (0,2),(1,2),(2,2), (0,3),(2,3), (0,4),(1,4),(2,4)],
    9: [(0,0),(1,0),(2,0), (0,1),(2,1), (0,2),(1,2),(2,2), (2,3), (0,4),(1,4),(2,4)]
}

# =========================
# FUNCION PIXEL CORREGIDA
# =========================
def set_pixel(x, y, color):
    if 0 <= x <= 31 and 0 <= y <= 7:
        px = 31 - x
        py = 7 - y
        display.pixel(px, py, color)

# =========================
# FUNCION BARRA
# =========================
def dibujar_barra(modulo, nivel):
    x_inicio = modulo * 8

    # Limpiar módulo
    for x in range(x_inicio, x_inicio + 8):
        for y in range(8):
            set_pixel(x, y, 0)

    # Limitar rango
    if nivel < 0:
        nivel = 0
    if nivel > 8:
        nivel = 8

    # Dibujar barra
    for fila in range(nivel):
        y = 7 - fila
        for x in range(x_inicio + 2, x_inicio + 6):
            set_pixel(x, y, 1)

# =========================
# FUNCION NUMERO
# =========================
def dibujar_numero(modulo, numero):
    x_inicio = modulo * 8

    # Limpiar módulo
    for x in range(x_inicio, x_inicio + 8):
        for y in range(8):
            set_pixel(x, y, 0)

    # Limitar a 0-9
    if numero < 0:
        numero = 0
    if numero > 9:
        numero = 9

    pixeles = FONT_3x5.get(numero, [])

    for px, py in pixeles:
        set_pixel(x_inicio + px + 2, py + 1, 1)

# =========================
# BUCLE PRINCIPAL
# =========================
while True:

    # =========================
    # LECTURA DE SENSORES
    # =========================
    dedo1 = flex1.read()
    dedo2 = flex2.read()

    # =========================
    # CALCULOS DEDO 1
    # =========================
    voltaje1 = (dedo1 / 4095) * 3.3
    angulo1 = (dedo1 / 4095) * 90

    # =========================
    # CALCULOS DEDO 2
    # =========================
    voltaje2 = (dedo2 / 4095) * 3.3
    angulo2 = (dedo2 / 4095) * 90

    # =========================
    # ROM MAXIMO
    # =========================
    if angulo1 > rom1:
        rom1 = angulo1

    if angulo2 > rom2:
        rom2 = angulo2

    # =========================
    # REPETICIONES DEDO 1
    # =========================
    if estado_flexion1 == 0 and angulo1 > UMBRAL_ALTO:
        estado_flexion1 = 1

    elif estado_flexion1 == 1 and angulo1 < UMBRAL_BAJO:
        estado_flexion1 = 0
        repeticiones1 += 1

    # =========================
    # REPETICIONES DEDO 2
    # =========================
    if estado_flexion2 == 0 and angulo2 > UMBRAL_ALTO:
        estado_flexion2 = 1

    elif estado_flexion2 == 1 and angulo2 < UMBRAL_BAJO:
        estado_flexion2 = 0
        repeticiones2 += 1

    # =========================
    # NIVELES VISUALES
    # =========================
    corriente_visual1 = int((dedo1 / 4095) * 8)
    angulo_nivel1 = int((angulo1 / 90) * 8)
    rom_nivel1 = int((rom1 / 90) * 8)

    # =========================
    # VISUALIZACION MATRIZ
    # =========================
    dibujar_barra(0, corriente_visual1)
    dibujar_numero(1, repeticiones1)
    dibujar_barra(2, angulo_nivel1)
    dibujar_barra(3, rom_nivel1)

    display.show()

    # =========================
    # COMUNICACION SERIAL
    # Formato:
    # D1,Angulo,ROM,Repeticiones,Voltaje,ADC,D2,...
    # =========================
    mensaje = (
        f"D1,{round(angulo1,1)},{round(rom1,1)},{repeticiones1},{round(voltaje1,2)},{dedo1},"
        f"D2,{round(angulo2,1)},{round(rom2,1)},{repeticiones2},{round(voltaje2,2)},{dedo2}"
    )

    print(mensaje)

    sleep(0.1)