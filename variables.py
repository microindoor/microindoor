"""
MIT License

Copyright (c) 2025 microindoor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from machine import Pin,PWM,RTC
import archivo_config as c
rtc = RTC()
#si usar archivo configuracion
archivo_config = True
existe_archivo = c.archivo_existe('config.bin')
#existen_datos = c.archivo_existe('datos.bin')
if archivo_config and existe_archivo:
    parametro = c.leer_configuracion()
else:
    parametro = None
"""
posibles valores para SALA1, 1, 3, True, False
con valor 1: salida para luz espectro completo
con valor 3: salidas para BLANCO, AZUL y ROJO
"""
SALA1 = 3 if parametro == None else int(parametro[0])
#valores True o False
SALA2 = False if parametro == None else bool(parametro[1])
SALA3 = False if parametro == None else bool(parametro[2])
SETAS_S1 = False if parametro == None else bool(parametro[3])
SETAS_S2 = False if parametro == None else bool(parametro[4])
SETAS_S3 = False if parametro == None else bool(parametro[5])
#PWM True o False salas 1,2,3
PWM_S1 = True if parametro == None else bool(parametro[6])
PWM_S2 = False if parametro == None else bool(parametro[7])
PWM_S3 = False if parametro == None else bool(parametro[8])
PASS_BT = 'cs2004'
conectado = False
pass_correcto = False
INTENTOS_PASS = 12
var_intentos = 0
t_desconexion = 10000
c_desconexion = 0
#referencia a método de módulo BLE
desconectar_x_tiempo = None
#visible o no al desconectar, no tocar
publicitar_bt = True
"""a los 2 minutos por defecto vuelve a estar visible,
se cambia por bluetooth con el comando tbtd2 (donde 2
son 2 horas"""
t_bt_d_publicidad = 60000
c_t_bt_d = 0
activar_publi_bt = None
"""temperatura máxima para cada 1 de las 3 salas
ya sea usando termistores o dht y de usar
ventiladores para regularlo """
TEMPERATURA_MAX = 25.0 if parametro == None else float(parametro[9])
TEMPERATURA2_MAX = 25.0 if parametro == None else float(parametro[10])
TEMPERATURA3_MAX = 25.0 if parametro == None else float(parametro[11])
"""intervalo en ºc para ventiladores, se detendrán
en 2ºC menos de la temperatura máxima para evitar
activación y desactivación continua"""
NO_PARPADEO = 2
"""intervalo en ºc para calefactores, se activarán
2ºC menos de la temperatura mínima para evitar
activación y desactivación continua, si son setas
se entiende que es resistencia eléctrica por lo que
no importa y además es importante mantener una
temperatura exacta"""
NO_PARPADEO_CALE = 0 if SETAS_S1 else 2
NO_PARPADEO_CALE2 = 0 if SETAS_S2 else 2
NO_PARPADEO_CALE3 = 0 if SETAS_S3 else 2
"""fase por defecto por sala,
True crecimiento, False floración"""
fase_s1 = False
fase_s2 = False
fase_s3 = False
"""humedades máximas para las distintas
salas en floración (53) y crecimiento (60)"""
hs1_fc = [53.0 if parametro == None else float(parametro[12]),
          60.0 if parametro == None else float(parametro[13])]
hs2_fc = [53.0 if parametro == None else float(parametro[14]),
          60.0 if parametro == None else float(parametro[15])]
hs3_fc = [53.0 if parametro == None else float(parametro[16]),
          60.0 if parametro == None else float(parametro[17])]
"""humedad máxima para cada 1 de las 3 salas en caso de
usar DHT y de usar ventiladores para regularlo """
humedad_s1 = hs1_fc[1] if fase_s1 else hs1_fc[0]
humedad_s2 = hs2_fc[1] if fase_s2 else hs2_fc[0]
humedad_s3 = hs3_fc[1] if fase_s3 else hs3_fc[0]
"""temperaturas mínimas por sala 1,2,3 y potencias
de cada calefactor para calcular gasto en wh"""
TEMPERATURA = 26.5 if parametro == None else float(parametro[18])
POTENCIA_CALEFACTOR = 1.44 if parametro == None else float(parametro[19])
TEMPERATURA2 = 22.5 if parametro == None else float(parametro[20])
POTENCIA_CALEFACTOR2 = 1.44 if parametro == None else float(parametro[21])
TEMPERATURA3 = 22.5 if parametro == None else float(parametro[22])
POTENCIA_CALEFACTOR3 = 1.44 if parametro == None else float(parametro[23])
"""salida pwm adicional para luz AUXILIAR
en modo ahorro"""
AUXILIAR_INSTALADO = True if parametro == None else bool(parametro[24])
#calefactores salas 1,2,3
CALEFACTOR_INSTALADO = True if parametro == None else bool(parametro[25])
CALEFACTOR2_INSTALADO = True if parametro == None else bool(parametro[26])
CALEFACTOR3_INSTALADO = True if parametro == None else bool(parametro[27])
#termistores salas 1,2,3
TERMISTOR_INSTALADO = False if parametro == None else bool(parametro[28])
TERMISTOR2_INSTALADO = False if parametro == None else bool(parametro[29])
TERMISTOR3_INSTALADO = False if parametro == None else bool(parametro[30])
#dht salas 1,2,3
DHT1_INSTALADO = True if parametro == None else bool(parametro[31])
DHT2_INSTALADO = False if parametro == None else bool(parametro[32])
DHT3_INSTALADO = False if parametro == None else bool(parametro[33])
#guarda temperatura, humedad, hora y sala en fichero
GUARDAR_VALORES = True if parametro == None else bool(parametro[34])
#guarda valores temp, humedad en fichero cada tiempo especificado
TIEMPO_VALORES = 900000 # cada 15 minutos
#no tocar
contador_valores = 0
#tamaño máximo fichero registro valores en bytes
BYTES_FICHERO = 700000
"""ventiladores salas 1,2,3, 0 regula mediante horas,
1 por termistores y 2 temperatura y humedad mediante dht"""
v_s1_reg_x = 0 if parametro == None else int(parametro[35])
v_s2_reg_x = 0 if parametro == None else int(parametro[36])
v_s3_reg_x = 1 if parametro == None else int(parametro[37])
#ventiladores instalados o no
VENTILADORES_S1 = False if parametro == None else bool(parametro[38])
VENTILADORES_S2 = True if parametro == None else bool(parametro[39])
VENTILADORES_S3 = True if parametro == None else bool(parametro[40])
#TIEMPO_V duración en min de ventiladores, max 60
TIEMPO_V = 3 if (VENTILADORES_S1 or VENTILADORES_S2 or VENTILADORES_S3) \
    and (v_s1_reg_x == 0 or v_s2_reg_x == 0 or v_s3_reg_x == 0) else 0
#en caso de no regular por temperatura ni humedad regulamos por horas
"""12.10 no son las 12.10, son las 12 + (10*60/100), 12:06.
Si lo quieres fácil pon horas exactas"""
HORAS_VS1 = (1.01,3.10,12.10,19.00,21.76) if ((
    SALA1 == 1 or SALA1 == 3) and VENTILADORES_S1 and v_s1_reg_x == 0) else 0
HORAS_VS2 = (2.01,4.10,14.10,15.85) if (
    SALA2 and VENTILADORES_S2 and v_s2_reg_x == 0) else 0
HORAS_VS3 = (2.01,4.10,14.10,16.95) if (
    SALA3 and VENTILADORES_S3 and v_s3_reg_x == 0) else 0
#no tocar
no_parpadeo = 0
no_parpadeo2 = 0
no_parpadeo3 = 0
no_parpadeo_cale = 0
no_parpadeo_cale2 = 0
no_parpadeo_cale3 = 0
#ventiladores regulados por PWM o no
PWM_VS1 = True if parametro == None else bool(parametro[41])
PWM_VS2 = False if parametro == None else bool(parametro[42])
PWM_VS3 = False if parametro == None else bool(parametro[43])
"""número de posiciones y posiciones
por defecto ventiladores si es PWM"""
NP_VS1 = 5 if PWM_VS1 else 1
pos_vs1 = 3 if PWM_VS1 else 1
NP_VS2 = 5 if PWM_VS2 else 1
pos_vs2 = 3 if PWM_VS2 else 1
NP_VS3 = 5 if PWM_VS3 else 1
pos_vs3 = 3 if PWM_VS3 else 1
"""almacena temperatura, y además humedad
si dht instalado"""
ts1 = [0,0]
ts2 = [0,0]
ts3 = [0,0]
"""indicar número de posiciones si PWM para
regular potencias por salas 1,2 y 3"""
NP_S1 = 20 if PWM_S1 else 1
NP_S2 = 10 if PWM_S2 else 1
NP_S3 = 10 if PWM_S3 else 1
"""posición potencia luz sala 1 , 2 y 3,
por defecto 1"""
pos_s1 = 1
pos_s2 = 1
pos_s3 = 1
"""watios máximos a utilizar por sala
en caso de usar PWM"""
WMAX_S1 = 6.0 if parametro == None else float(parametro[44]) #sala 1
WMAX_S2 = 10.0 if parametro == None else float(parametro[45]) #sala 2
WMAX_S3 = 4.0 if parametro == None else float(parametro[46]) #sala 3
"""indicar potencia total en watios
por led de cada color en caso de usar
3 leds en PWM en la sala 1 y/o auxiliar"""
PT_R = 3.6 if parametro == None else float(parametro[47])
PT_B = 3.6 if parametro == None else float(parametro[48])
PT_A = 1.4 if parametro == None else float(parametro[49])
PT_AUX = 1.8 if parametro == None else float(parametro[50])
"""indicar tiempo que durará el led
auxiliar en caso de instalarlo y activarlo"""
#15 segundos por ejemplo para probar
TIEMPO_AUXILIAR = 15000 
"""indicar potencia total en watios por sala
en caso de usar leds espectro completo"""
PT_ECS1 = 20.0 if parametro == None else float(parametro[51])
PT_ECS2 = 10.0 if parametro == None else float(parametro[52])
PT_ECS3 = 10.0 if parametro == None else float(parametro[53])

#valores para el archivo de configuración
if archivo_config and not existe_archivo:
    lista_config = c.variables_config()
    c.fichero_configuracion(lista_config)
"""apagamos éstos pines para evitar que queden
encendidos al inicio"""
pines = (26,27,18,19,21,23,22,13,14,25)
for pin in pines:
    Pin(pin,Pin.OUT).off()

blanco_activado = 1
azul_activado = 1
rojo_activado = 1
auxiliar_activado = 0
ecompletos1_activado = 1
contador_apagado = 0
tiempo_apagado = 0

if not PWM_S1 and SALA1 == 3:
    SALA1 = 1
if SALA3:
    if SALA1 == 3:
        SALA3 = False
            
#números pines a utilizar y variables
if ((TERMISTOR_INSTALADO or DHT1_INSTALADO) or
    (TERMISTOR2_INSTALADO or DHT2_INSTALADO) or
    (TERMISTOR3_INSTALADO or DHT3_INSTALADO)):
    contador_temperatura = 0
    t_comprobar_temperatura = 5000 #milisegundos
    contador_temperatura_inicio = False
else:
    GUARDAR_VALORES = False
if TERMISTOR_INSTALADO:
    N_PIN_TERMISTOR = 32
    PIN_TERMISTOR = Pin(N_PIN_TERMISTOR)
elif DHT1_INSTALADO:
    N_PIN_DHT1 = 32
    PIN_DHT1 = Pin(N_PIN_DHT1)
if SALA2 and TERMISTOR2_INSTALADO:
    N_PIN_TERMISTOR2 = 4
    PIN_TERMISTOR2 = Pin(N_PIN_TERMISTOR2)
elif SALA2 and DHT2_INSTALADO:
    N_PIN_DHT2 = 4
    PIN_DHT2 = Pin(N_PIN_DHT2)
if SALA3 and TERMISTOR3_INSTALADO:
    N_PIN_TERMISTOR3 = 33
    PIN_TERMISTOR3 = Pin(N_PIN_TERMISTOR3)
elif SALA3 and DHT3_INSTALADO:
    N_PIN_DHT3 = 33
    PIN_DHT3 = Pin(N_PIN_DHT3)
    
if CALEFACTOR_INSTALADO and (TERMISTOR_INSTALADO or DHT1_INSTALADO):
    N_PIN_CALEFACTOR = 26
    PIN_CALEFACTOR = Pin(N_PIN_CALEFACTOR,Pin.OUT)
    PIN_CALEFACTOR.off()
    calefactor = False
    contador_inicio_calefactor = 0
    contador_calefactor = 0
else:
    calefactor = False
if CALEFACTOR2_INSTALADO and (TERMISTOR2_INSTALADO or DHT2_INSTALADO):
    N_PIN_CALEFACTOR2 = 27
    PIN_CALEFACTOR2 = Pin(N_PIN_CALEFACTOR2,Pin.OUT)
    PIN_CALEFACTOR2.off()
    calefactor2 = False
    contador_inicio_calefactor2 = 0
    contador_calefactor2 = 0
else:
    calefactor2 = False
if CALEFACTOR3_INSTALADO and (TERMISTOR3_INSTALADO or DHT3_INSTALADO):
    N_PIN_CALEFACTOR3 = 25
    PIN_CALEFACTOR3 = Pin(N_PIN_CALEFACTOR3,Pin.OUT)
    PIN_CALEFACTOR3.off()
    calefactor3 = False
    contador_inicio_calefactor3 = 0
    contador_calefactor3 = 0
else:
    calefactor3 = False


if (SALA1 == 1 or SALA1 == 3) and (TERMISTOR_INSTALADO or DHT1_INSTALADO):
    PIN_TERMISTOR_DHT1 = PIN_TERMISTOR if TERMISTOR_INSTALADO else PIN_DHT1
if SALA1 == 3:
    N_PIN_ROJO = 18
    N_PIN_BLANCO = 19
    N_PIN_AZUL = 21
    #porcentaje luminosidad por color
    P_ROJO = 60
    P_BLANCO = 18
    P_AZUL = 22
    #indicar potencia total en watios por led de cada color
    PT_ROJO = PT_R
    PT_BLANCO = PT_B
    PT_AZUL = PT_A
    #indicar resolucion (10 bits o 16) pwm en bits
    RB_ROJO = 10
    RB_BLANCO = 10
    RB_AZUL = 10
    #indicar frecuencia pwm en hz por cada color
    fr_rojo = 20000
    fr_blanco = 20000
    fr_azul = 20000
elif SALA1 == 1:
    N_PIN_ECOMPLETOS1 = 18
    #indicar potencia total en watios espectro completo
    PT_ECOMPLETOS1 = PT_ECS1
    #indicar resolucion (10 bits o 16) pwm en bits
    RB_ECOMPLETOS1 = 10
    #indicar frecuencia pwm en hz
    fr_ecompletos1 = 20000
elif not SALA1:
    VENTILADORES_S1 = False
    DHT1_INSTALADO = False
    TERMISTOR_INSTALADO = False
    CALEFACTOR_INSTALADO = False
if SALA2:
    N_PIN_ECOMPLETOS2 = 23
    #indicar potencia total en watios espectro completo
    PT_ECOMPLETOS2 = PT_ECS2
    #indicar resolucion (10 bits o 16) pwm en bits
    RB_ECOMPLETOS2 = 10
    #indicar frecuencia pwm en hz
    fr_ecompletos2 = 500
    if TERMISTOR2_INSTALADO or DHT2_INSTALADO:
        PIN_TERMISTOR_DHT2 = PIN_TERMISTOR2 if TERMISTOR2_INSTALADO else PIN_DHT2
else:
    VENTILADORES_S2 = False
    DHT2_INSTALADO = False
    TERMISTOR2_INSTALADO = False
    CALEFACTOR2_INSTALADO = False
if SALA3:
    N_PIN_ECOMPLETOS3 = 19
    #indicar potencia total en watios espectro completo
    PT_ECOMPLETOS3 = PT_ECS3
    #indicar resolucion (10 bits o 16) pwm en bits
    RB_ECOMPLETOS3 = 10
    #indicar frecuencia pwm en hz
    fr_ecompletos3 = 20000
    if TERMISTOR3_INSTALADO or DHT3_INSTALADO:
        PIN_TERMISTOR_DHT3 = PIN_TERMISTOR3 if TERMISTOR3_INSTALADO else PIN_DHT3
else:
    VENTILADORES_S3 = False
    DHT3_INSTALADO = False
    TERMISTOR3_INSTALADO = False
    CALEFACTOR3_INSTALADO = False
if AUXILIAR_INSTALADO:
    N_PIN_AUXILIAR = 22
    usar_led_auxiliar = False
    contador_inicio_led_auxiliar = 0
    tiempo_led_auxiliar = TIEMPO_AUXILIAR
    #porcentaje luminosidad por color
    P_AUXILIAR = 60 #ROJO normalmente o espectro completo
    #leds que apagará en FALSE cuando esté encendida luz auxiliar
    s_rojo = False
    s_blanco = True
    s_azul = True
    #indicar potencia total en watios
    PT_AUXILIAR = PT_AUX
    #indicar resolucion (10 bits o 16) pwm en bits
    RB_AUXILIAR = 10
    #indicar frecuencia pwm en hz
    fr_auxiliar = 20000
if (SALA1 == 1 or SALA1 == 3) and VENTILADORES_S1:
    N_PIN_VENTILADORES_S1 = 13
    if PWM_VS1:
        FR_VS1 = 20000
        RB_VS1 = 10
        if RB_VS1 == 16:
            PIN_VS1 = PWM(
                Pin(N_PIN_VENTILADORES_S1),freq=FR_VS1,duty_16=(0)) 
        else:
            PIN_VS1 = PWM(
                Pin(N_PIN_VENTILADORES_S1),freq=FR_VS1,duty=(0)) 
    else:
        PIN_VS1 = Pin(N_PIN_VENTILADORES_S1,Pin.OUT)
        PIN_VS1.value(0)
        
if SALA2 and VENTILADORES_S2:
    N_PIN_VENTILADORES_S2 = 14
    if PWM_VS2:
        FR_VS2 = 20000
        RB_VS2 = 10
        if RB_VS2 == 16:
            PIN_VS2 = PWM(
                Pin(N_PIN_VENTILADORES_S2),freq=FR_VS2,duty_16=(0)) 
        else:
            PIN_VS2 = PWM(
                Pin(N_PIN_VENTILADORES_S2),freq=FR_VS2,duty=(0)) 
    else:
        PIN_VS2 = Pin(N_PIN_VENTILADORES_S2,Pin.OUT)
        PIN_VS2.value(0)
else:
    VENTILADORES_S2 = False
    PWM_VS2 = False
    
if SALA3 and VENTILADORES_S3:
    N_PIN_VENTILADORES_S3 = 21
    if PWM_VS3:
        FR_VS3 = 20000
        RB_VS3 = 10
        if RB_VS3 == 16:
            PIN_VS3 = PWM(
                Pin(N_PIN_VENTILADORES_S3),freq=FR_VS3,duty_16=(0)) 
        else:
            PIN_VS3 = PWM(
                Pin(N_PIN_VENTILADORES_S3),freq=FR_VS3,duty=(0)) 
    else:
        PIN_VS3 = Pin(N_PIN_VENTILADORES_S3,Pin.OUT)
        PIN_VS3.value(0)
else:
    VENTILADORES_S3 = False
    PWM_VS3 = False
        
"""
potencia total insuficiente de algún color led respecto de los
watios máximos a utilizar por sala """
pocaPotencia = False  

"""calculamos las distintas resoluciones según bits para las distintas
potencias a usar según los watios máximos definidos """
if SALA1 == 1:
    if PWM_S1:
        ECOMPLETOS1 = ((WMAX_S1 * 100 / 100) * 2 ** RB_ECOMPLETOS1 - 1) / PT_ECOMPLETOS1
        if RB_ECOMPLETOS1 == 16:
            PIN_ECOMPLETOS1 = PWM(
                Pin(N_PIN_ECOMPLETOS1),freq=fr_ecompletos1,duty_16=(0))
        else:
            PIN_ECOMPLETOS1 = PWM(
                Pin(N_PIN_ECOMPLETOS1),freq=fr_ecompletos1,duty=(0))
    else:
        PIN_ECOMPLETOS1 = Pin(N_PIN_ECOMPLETOS1,Pin.OUT)
        PIN_ECOMPLETOS1.value(0)     
#Si luz compuesta por 3 colores
elif SALA1 == 3:
    ROJO = ((WMAX_S1 * P_ROJO / 100) * 2 ** RB_ROJO -1) / PT_ROJO
    BLANCO = ((WMAX_S1 * P_BLANCO / 100) * 2 ** RB_BLANCO -1) / PT_BLANCO
    AZUL = ((WMAX_S1 * P_AZUL / 100) * 2 ** RB_AZUL -1) / PT_AZUL
    if RB_ROJO == 16:
        PIN_ROJO = PWM(Pin(N_PIN_ROJO),freq=fr_rojo,duty_16=(0))
    else:
        PIN_ROJO = PWM(Pin(N_PIN_ROJO),freq=fr_rojo,duty=(0))
    if RB_BLANCO == 16:
        PIN_BLANCO = PWM(Pin(N_PIN_BLANCO),freq=fr_blanco,duty_16=(0))
    else:
        PIN_BLANCO = PWM(Pin(N_PIN_BLANCO),freq=fr_blanco,duty=(0))
    if RB_AZUL == 16:
        PIN_AZUL = PWM(Pin(N_PIN_AZUL),freq=fr_azul,duty_16=(0))
    else:
        PIN_AZUL = PWM(Pin(N_PIN_AZUL),freq=fr_azul,duty=(0))
    print(str(int(ROJO))+' '+str(int(BLANCO))+' '+str(int(AZUL)))
    if ((2 ** RB_AZUL) < AZUL) or ((2 ** RB_ROJO) < ROJO) or (
        (2 ** RB_BLANCO) < BLANCO):
        pocaPotencia = True
        if RB_AZUL < AZUL:
            AZUL = 2 ** RB_AZUL -1
        if RB_ROJO < ROJO:
            ROJO = 2 ** RB_ROJO -1
        if RB_BLANCO < BLANCO:
            BLANCO = 2 ** RB_BLANCO -1
if SALA2:
    if PWM_S2:
        ECOMPLETOS2 = ((WMAX_S2 * 100 / 100) * 2 ** RB_ECOMPLETOS2 -1) / PT_ECOMPLETOS2
        if RB_ECOMPLETOS2 == 16:
            PIN_ECOMPLETOS2 = PWM(
                Pin(N_PIN_ECOMPLETOS2),freq=fr_ecompletos2,duty_16=(0)) #pin espectro completo sala2
        else:
            PIN_ECOMPLETOS2 = PWM(
                Pin(N_PIN_ECOMPLETOS2),freq=fr_ecompletos2,duty=(0)) #pin espectro completo sala2
    else:
        PIN_ECOMPLETOS2 = Pin(N_PIN_ECOMPLETOS2,Pin.OUT)
        PIN_ECOMPLETOS2.value(0)
        
if SALA3:
    if PWM_S3:
        ECOMPLETOS3 = ((WMAX_S3 * 100 / 100) * 2 ** RB_ECOMPLETOS3 -1) / PT_ECOMPLETOS3
        if RB_ECOMPLETOS3 == 16:
            PIN_ECOMPLETOS3 = PWM(
                Pin(N_PIN_ECOMPLETOS3),freq=fr_ecompletos3,duty_16=(0)) #pin espectro completo sala2
        else:
            PIN_ECOMPLETOS3 = PWM(
                Pin(N_PIN_ECOMPLETOS3),freq=fr_ecompletos3,duty=(0)) #pin espectro completo sala2
    else:
        PIN_ECOMPLETOS3 = Pin(N_PIN_ECOMPLETOS3,Pin.OUT)
        PIN_ECOMPLETOS3.value(0)

if AUXILIAR_INSTALADO:
    p_restar = 0
    if SALA1 == 3:
        if s_rojo:
            p_restar += WMAX_S1 * P_ROJO / 100
        if s_azul:
            p_restar += WMAX_S1 * P_AZUL / 100
        if s_blanco:
            p_restar += WMAX_S1 * P_BLANCO / 100
    AUXILIAR = ((WMAX_S1 * (P_AUXILIAR - p_restar) / 100) * 2 ** RB_AUXILIAR -1) / PT_AUXILIAR
    if RB_AUXILIAR == 16:
        PIN_AUXILIAR = PWM(
            Pin(N_PIN_AUXILIAR),freq=fr_auxiliar,duty_16=(0)) #pin led auxiliar rojo o espectro completo normalmente
    else:
        PIN_AUXILIAR = PWM(Pin(N_PIN_AUXILIAR),freq=fr_auxiliar,duty=(0))
    if ((2 ** RB_AUXILIAR) < AUXILIAR):
        AUXILIAR = 2 ** RB_AUXILIAR -1
        pocaPotencia = True
        
