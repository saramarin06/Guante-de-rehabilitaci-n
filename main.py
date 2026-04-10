from machine import Pin, ADC, SPI
from max7219 import Matrix8x8
from time import sleep, ticks_ms, ticks_diff

# =========================
# CONFIGURACION ADC
# =========================
flex1 = ADC(Pin(34))   # Dedo 1
flex2 = ADC(Pin(35))   # Dedo 2
flex3 = ADC(Pin(32))   # Dedo 3 (NUEVO)

for flex in [flex1, flex2, flex3]:
    flex.atten(ADC.ATTN_11DB)
    flex.width(ADC.WIDTH_12BIT)

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
# INTERRUPCION PARA PANTALLA
# =========================
boton_pantalla = Pin(15, Pin.IN, Pin.PULL_UP) # Conectar botón entre Pin 15 y GND
dedo_pantalla = 1
ultimo_tiempo_irq = 0

def cambiar_pantalla(pin):
    global dedo_pantalla, ultimo_tiempo_irq
    tiempo_actual = ticks_ms()
    # Anti-rebote de 300ms
    if ticks_diff(tiempo_actual, ultimo_tiempo_irq) > 300:
        dedo_pantalla += 1
        if dedo_pantalla > 3:
            dedo_pantalla = 1
        ultimo_tiempo_irq = tiempo_actual

# Configurar interrupción en el flanco de bajada (al presionar el botón)
boton_pantalla.irq(trigger=Pin.IRQ_FALLING, handler=cambiar_pantalla)

# =========================
# VARIABLES DEL SISTEMA
# =========================
rom1, rom2, rom3 = 0, 0, 0
repeticiones1, repeticiones2, repeticiones3 = 0, 0, 0
estado_flexion1, estado_flexion2, estado_flexion3 = 0, 0, 0

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
# FUNCIONES DE DIBUJO
# =========================
def set_pixel(x, y, color):
    if 0 <= x <= 31 and 0 <= y <= 7:
        px = 31 - x
        py = 7 - y
        display.pixel(px, py, color)

def dibujar_barra(modulo, nivel):
    x_inicio = modulo * 8
    for x in range(x_inicio, x_inicio + 8):
        for y in range(8):
            set_pixel(x, y, 0)
    
    nivel = max(0, min(nivel, 8))
    
    for fila in range(nivel):
        y = 7 - fila
        for x in range(x_inicio + 2, x_inicio + 6):
            set_pixel(x, y, 1)

def dibujar_numero(modulo, numero):
    x_inicio = modulo * 8
    for x in range(x_inicio, x_inicio + 8):
        for y in range(8):
            set_pixel(x, y, 0)
            
    numero = max(0, min(numero, 9))
    pixeles = FONT_3x5.get(numero, [])
    
    for px, py in pixeles:
        set_pixel(x_inicio + px + 2, py + 1, 1)

# =========================
# BUCLE PRINCIPAL
# =========================
while True:
    # --- LECTURA ---
    val_dedo1 = flex1.read()
    val_dedo2 = flex2.read()
    val_dedo3 = flex3.read()

    # --- CALCULOS DE VOLTAJE Y ANGULO ---
    voltaje1, angulo1 = (val_dedo1 / 4095) * 3.3, (val_dedo1 / 4095) * 90
    voltaje2, angulo2 = (val_dedo2 / 4095) * 3.3, (val_dedo2 / 4095) * 90
    voltaje3, angulo3 = (val_dedo3 / 4095) * 3.3, (val_dedo3 / 4095) * 90

    # --- ROM MAXIMO ---
    if angulo1 > rom1: rom1 = angulo1
    if angulo2 > rom2: rom2 = angulo2
    if angulo3 > rom3: rom3 = angulo3

    # --- REPETICIONES ---
    # Dedo 1
    if estado_flexion1 == 0 and angulo1 > UMBRAL_ALTO: estado_flexion1 = 1
    elif estado_flexion1 == 1 and angulo1 < UMBRAL_BAJO:
        estado_flexion1 = 0
        repeticiones1 += 1

    # Dedo 2
    if estado_flexion2 == 0 and angulo2 > UMBRAL_ALTO: estado_flexion2 = 1
    elif estado_flexion2 == 1 and angulo2 < UMBRAL_BAJO:
        estado_flexion2 = 0
        repeticiones2 += 1

    # Dedo 3
    if estado_flexion3 == 0 and angulo3 > UMBRAL_ALTO: estado_flexion3 = 1
    elif estado_flexion3 == 1 and angulo3 < UMBRAL_BAJO:
        estado_flexion3 = 0
        repeticiones3 += 1

    # =========================
    # VISUALIZACION MATRIZ
    # =========================
    # Dependiendo de qué dedo esté seleccionado por el botón, mapeamos los valores
    if dedo_pantalla == 1:
        corr_vis = int((val_dedo1 / 4095) * 8)
        reps = repeticiones1
        ang_niv = int((angulo1 / 90) * 8)
        rom_niv = int((rom1 / 90) * 8)
    elif dedo_pantalla == 2:
        corr_vis = int((val_dedo2 / 4095) * 8)
        reps = repeticiones2
        ang_niv = int((angulo2 / 90) * 8)
        rom_niv = int((rom2 / 90) * 8)
    else: # dedo_pantalla == 3
        corr_vis = int((val_dedo3 / 4095) * 8)
        reps = repeticiones3
        ang_niv = int((angulo3 / 90) * 8)
        rom_niv = int((rom3 / 90) * 8)

    # Actualizar la matriz garantizando que los módulos queden independientes
    dibujar_barra(0, corr_vis)
    dibujar_numero(1, reps)
    dibujar_barra(2, ang_niv)
    dibujar_barra(3, rom_niv)
    
    display.show()

    # =========================
    # COMUNICACION SERIAL
    # =========================
    mensaje = (
        f"D1,{round(angulo1,1)},{round(rom1,1)},{repeticiones1},{round(voltaje1,2)},{val_dedo1},"
        f"D2,{round(angulo2,1)},{round(rom2,1)},{repeticiones2},{round(voltaje2,2)},{val_dedo2},"
        f"D3,{round(angulo3,1)},{round(rom3,1)},{repeticiones3},{round(voltaje3,2)},{val_dedo3},"
        f"VIENDO_DEDO,{dedo_pantalla}"
    )
    print(mensaje)

    sleep(0.1)