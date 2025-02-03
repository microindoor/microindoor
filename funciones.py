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
import variables as v
import array
import time
from machine import ADC,Pin
if v.TERMISTOR_INSTALADO or v.TERMISTOR2_INSTALADO or v.TERMISTOR3_INSTALADO:
    from math import log
if (v.DHT1_INSTALADO or v.DHT2_INSTALADO or v.DHT3_INSTALADO):
    import dht
if v.GUARDAR_VALORES:
    import struct,uos
    
def leds_y_led_auxiliar():
    if v.SALA1 == 3:
        if not v.s_rojo:
            v.rojo_activado = 1
        if not v.s_blanco:
            v.blanco_activado = 1
        if not v.s_azul:
            v.azul_activado = 1
    elif v.SALA1 == 1:
        v.ecompletos1_activado = 1
    v.auxiliar_activado = 0
    v.usar_led_auxiliar = False
    v.contador_inicio_led_auxiliar = 0
    v.contador_apagado = 0
    v.tiempo_apagado = 0
    
def regular_ventiladores(incrementar=True,sala=1):
    if v.VENTILADORES_S1 and sala == 1\
    and incrementar and v.pos_vs1 < v.NP_VS1:
        v.pos_vs1+=1
    elif v.VENTILADORES_S1 and sala == 1\
    and not incrementar and not v.pos_vs1 == 0:
        v.pos_vs1-=1
    if v.VENTILADORES_S2 and sala == 2\
    and incrementar and v.pos_vs2 < v.NP_VS2:
        v.pos_vs2+=1
    elif v.VENTILADORES_S2 and sala == 2\
    and not incrementar and not v.pos_vs2 == 0:
        v.pos_vs2-=1
    if v.VENTILADORES_S3 and sala == 3\
    and incrementar and v.pos_vs3 < v.NP_VS3:
        v.pos_vs3+=1
    elif v.VENTILADORES_S3 and sala == 3\
    and not incrementar and not v.pos_vs3 == 0:
        v.pos_vs3-=1
    
def regularSala(incre=False,decre=False,sala=1,apagar=False):
    incrementar = (incre == True and decre == False)
    decrementar = (incre == False and decre == True)
    iod = incre or decre
    if v.AUXILIAR_INSTALADO and v.usar_led_auxiliar \
        and apagar and v.contador_apagado == 0:
        v.contador_apagado = time.ticks_ms()
    elif v.AUXILIAR_INSTALADO and v.usar_led_auxiliar \
        and apagar and v.contador_apagado != 0:
        v.tiempo_apagado = time.ticks_ms() - v.contador_apagado
    elif not apagar:
        v.contador_apagado = 0
    v_pos_s1, vpos_s2 =0,0
    if incrementar and sala == 1 and v.pos_s1 < v.NP_S1:
        v.pos_s1+=1
    elif decrementar and sala == 1 and v.pos_s1 > 0:
        v.pos_s1-=1
    if incrementar and sala == 2 and v.pos_s2 < v.NP_S2:
        v.pos_s2+=1
    elif decrementar and sala == 2 and v.pos_s2 > 0:
        v.pos_s2-=1
    if incrementar and sala == 3 and v.pos_s3 < v.NP_S3:
        v.pos_s3+=1
    elif decrementar and sala == 3 and v.pos_s3 > 0:
        v.pos_s3-=1
    if not iod:
        if apagar and (sala == 1):
            v_pos_s1 = 0
        elif not apagar and sala == 1:
            v_pos_s1 = v.pos_s1
        if apagar and sala == 2:
            v_pos_s2 = 0
        elif not apagar and sala == 2:
            v_pos_s2 = v.pos_s2
        if apagar and sala == 3:
            v_pos_s3 = 0
        elif not apagar and sala == 3:
            v_pos_s3 = v.pos_s3
        if v.AUXILIAR_INSTALADO and v.usar_led_auxiliar \
           and v.contador_inicio_led_auxiliar == 0:
            v.contador_inicio_led_auxiliar = time.ticks_ms()
            if v.SALA1 == 3:
                if not v.s_rojo:
                    v.rojo_activado = 0
                if not v.s_blanco:
                    v.blanco_activado = 0
                if not v.s_azul:
                    v.azul_activado = 0
            elif v.SALA1 == 1:
                v.ecompletos1_activado = 0
            v.auxiliar_activado = 1
        elif (v.AUXILIAR_INSTALADO and v.usar_led_auxiliar and
        ((time.ticks_ms()-v.tiempo_apagado-v.contador_inicio_led_auxiliar)
        >= v.tiempo_led_auxiliar)
        and v.auxiliar_activado == 1):
            leds_y_led_auxiliar()
    if v.SALA1 == 3 and sala == 1 and not iod:
        if v.RB_BLANCO == 16:
            v.PIN_BLANCO.duty_16(int(v.BLANCO/v.NP_S1*v_pos_s1*v.blanco_activado))
        elif v.RB_BLANCO == 10:
            v.PIN_BLANCO.duty(int(v.BLANCO/v.NP_S1*v_pos_s1*v.blanco_activado))
        if v.RB_ROJO == 16:
            v.PIN_ROJO.duty_16(int(v.ROJO/v.NP_S1*v_pos_s1*v.rojo_activado))
        elif v.RB_ROJO == 10:
            v.PIN_ROJO.duty(int(v.ROJO/v.NP_S1*v_pos_s1*v.rojo_activado))
        if v.RB_AZUL == 16:
            v.PIN_AZUL.duty_16(int(v.AZUL/v.NP_S1*v_pos_s1*v.azul_activado))
        elif v.RB_AZUL == 10:
            v.PIN_AZUL.duty(int(v.AZUL/v.NP_S1*v_pos_s1*v.azul_activado))
    elif v.SALA1 == 1 and sala == 1 and not iod:
        if v.PWM_S1:
            if v.RB_ECOMPLETOS1 == 16:
                v.PIN_ECOMPLETOS1.duty_16(
                    int(v.ECOMPLETOS1/v.NP_S1*v_pos_s1*v.ecompletos1_activado))
            elif v.RB_ECOMPLETOS1 == 10:
                v.PIN_ECOMPLETOS1.duty(
                    int(v.ECOMPLETOS1/v.NP_S1*v_pos_s1*v.ecompletos1_activado))
        else:
            if apagar or v.pos_s1 == 0:
                v.PIN_ECOMPLETOS1.value(0)
            else:
                v.PIN_ECOMPLETOS1.value(1)
    if v.SALA2 and sala == 2 and not iod:
        if v.PWM_S2:
            if v.RB_ECOMPLETOS2 == 16:
                v.PIN_ECOMPLETOS2.duty_16(int(v.ECOMPLETOS2/v.NP_S2*v_pos_s2))
            elif v.RB_ECOMPLETOS2 == 10:
                v.PIN_ECOMPLETOS2.duty(int(v.ECOMPLETOS2/v.NP_S2*v_pos_s2))
        else:
            if apagar or v.pos_s2 == 0:
                v.PIN_ECOMPLETOS2.value(0)
            else:
                v.PIN_ECOMPLETOS2.value(1)
    if v.SALA3 and sala == 3 and not iod:
        if v.PWM_S3:
            if v.RB_ECOMPLETOS3 == 16:
                v.PIN_ECOMPLETOS3.duty_16(int(v.ECOMPLETOS3/v.NP_S3*v_pos_s3))
            elif v.RB_ECOMPLETOS3 == 10:
                v.PIN_ECOMPLETOS3.duty(int(v.ECOMPLETOS3/v.NP_S3*v_pos_s3))
        else:
            if apagar or v.pos_s3 == 0:
                v.PIN_ECOMPLETOS3.value(0)
            else:
                v.PIN_ECOMPLETOS3.value(1)
    if (v.SALA1 == 3 or v.SALA1 == 1) and sala == 1 \
        and not iod and v.AUXILIAR_INSTALADO:
        if v.RB_AUXILIAR == 16:
            v.PIN_AUXILIAR.duty_16(
                int(v.AUXILIAR/v.NP_S1*v_pos_s1*v.auxiliar_activado))
        elif v.RB_AUXILIAR == 10:
            v.PIN_AUXILIAR.duty(
                int(v.AUXILIAR/v.NP_S1*v_pos_s1*v.auxiliar_activado))
       
#funcion que devuelve True o False si debe haber luz según fase crecimiento o floración              
def luz_fase(a):
    hours = v.rtc.datetime()[4] + v.rtc.datetime()[5] / 60.0
    #De 00:00 a 18:00
    crecimiento = ( (hours >= 23.00 and hours <= 23.99) \
                or (hours >= 00.00 and hours <= 17.00) ) and a
    #De 00:00 a 12:00
    floracion = ( (hours >= 23.00 and hours <= 23.99) \
                or (hours >= 00.00 and hours <= 11.00) ) and not a
    if crecimiento:
        return True
    elif floracion:
        return True
    return False

def ventiladores(minut = 0.0):
    encendido = False
    encendido_pwm = 0
    if v.v_s1_reg_x == 0:
        horaI = v.rtc.datetime()[4] + v.rtc.datetime()[5] / 60.0
        horaF = v.rtc.datetime()[4] + v.rtc.datetime()[5] / 60.0 + minut / 60.0
        if horaF == 24:
            horaF = 0
        if horaI == 24:
            horaI = 0
    if v.VENTILADORES_S1 and (v.SALA1 == 1 or v.SALA1 == 3):
        if v.v_s1_reg_x == 0:
            for a in v.HORAS_VS1:
                if a >= horaI and a <= horaF:
                    encendido = True
                    encendido_pwm = 1
        elif v.v_s1_reg_x == 1:
            if v.ts1[0] > (v.TEMPERATURA_MAX-v.no_parpadeo):
                encendido = True
                encendido_pwm = 1
                v.no_parpadeo = v.NO_PARPADEO
            else:
                v.no_parpadeo = 0
        elif v.v_s1_reg_x == 2:
            if (v.ts1[0] > (v.TEMPERATURA_MAX-v.no_parpadeo) \
                or v.ts1[1] > (v.humedad_s1-v.no_parpadeo)):
                encendido = True
                encendido_pwm = 1
                v.no_parpadeo = v.NO_PARPADEO
            else:
                v.no_parpadeo = 0
        if not v.PWM_VS1:
            if not encendido or v.pos_vs1 == 0:
                v.PIN_VS1.value(0)
            else:
                v.PIN_VS1.value(1)
        else:
            if v.RB_VS1 == 16:
                v.PIN_VS1.duty16(
                    int((2 ** v.RB_VS1 -1)/v.NP_VS1*v.pos_vs1*encendido_pwm)) 
            elif v.RB_VS1 == 10:
                v.PIN_VS1.duty(
                    int((2 ** v.RB_VS1 -1)/v.NP_VS1*v.pos_vs1*encendido_pwm))
        encendido = False
        encendido_pwm = 0
    if v.VENTILADORES_S2 and v.SALA2:
        if v.v_s2_reg_x == 0:
            for b in v.HORAS_VS2:
                if b >= horaI and b <= horaF:
                    encendido = True
                    encendido_pwm = 1
        elif v.v_s2_reg_x == 1:
            if v.ts2[0] > (v.TEMPERATURA2_MAX-v.no_parpadeo2):
                encendido = True
                encendido_pwm = 1
                v.no_parpadeo2 = v.NO_PARPADEO
            else:
                v.no_parpadeo2 = 0
        elif v.v_s2_reg_x == 2:
            if v.ts2[0] > (v.TEMPERATURA2_MAX-v.no_parpadeo2) \
                or v.ts2[1] > (v.humedad_s2-v.no_parpadeo2):
                encendido = True
                encendido_pwm = 1
                v.no_parpadeo2 = v.NO_PARPADEO
            else:
                v.no_parpadeo2 = 0
        if not v.PWM_VS2:
            if not encendido or v.pos_vs2 == 0:
                v.PIN_VS2.value(0)
            else:
                v.PIN_VS2.value(1)
        else:
            if v.RB_VS2 == 16:
                v.PIN_VS2.duty16(
                    int((2 ** v.RB_VS2 -1)/v.NP_VS2*v.pos_vs2*encendido_pwm)) 
            elif v.RB_VS2 == 10:
                v.PIN_VS2.duty(
                    int((2 ** v.RB_VS2 -1)/v.NP_VS2*v.pos_vs2*encendido_pwm))
        encendido = False
        encendido_pwm = 0
    if v.VENTILADORES_S3 and v.SALA3:
        if v.v_s3_reg_x == 0:
            for b in v.HORAS_VS3:
                if b >= horaI and b <= horaF:
                    encendido = True
                    encendido_pwm = 1
        elif v.v_s3_reg_x == 1:
            if v.ts3[0] > (v.TEMPERATURA3_MAX-v.no_parpadeo3):
                encendido = True
                encendido_pwm = 1
                v.no_parpadeo3 = v.NO_PARPADEO
            else:
                v.no_parpadeo3 = 0
        elif v.v_s3_reg_x == 2:
            if v.ts3[0] > (v.TEMPERATURA2_MAX-v.no_parpadeo3) \
                or v.ts3[1] > (v.humedad_s2-v.no_parpadeo3):
                encendido = True
                encendido_pwm = 1
                v.no_parpadeo3 = v.NO_PARPADEO
            else:
                no_parpadeo3 = 0
        if not v.PWM_VS3:
            if not encendido or v.pos_vs3 == 0:
                v.PIN_VS3.value(0)
            else:
                v.PIN_VS3.value(1)
        else:
            if v.RB_VS3 == 16:
                v.PIN_VS3.duty16(
                    int((2 ** v.RB_VS3 -1)/v.NP_VS3*v.pos_vs3*encendido_pwm)) 
            elif v.RB_VS3 == 10:
                v.PIN_VS3.duty(
                    int((2 ** v.RB_VS3 -1)/v.NP_VS3*v.pos_vs3*encendido_pwm))
        encendido = False
        encendido_pwm = 0
        
def temperatura(pinTermistor_DHT,termistor = False):
    try:
        if termistor:
            #constantes para calcular temperatura
            R1 = 9940.0   #valor en ohm resistencia
            BETA = 3950.0 #Beta value
            TO = 298.15   #Temperatura en Kelvin a 25 grados Celsius
            RO = 10000.0  #Resistencia termistor a 25 grados Celsius
            ADCMAX = 2 ** 12 #resolucion 12 bits
            VS = 3.3 #voltaje pines esp32
            Vout =0
            rt = 0.00
            t = 0.00
            tc = 0
            adc = 0
            import struct
            adc = ADC(pinTermistor_DHT)
            adc.atten(ADC.ATTN_11DB)
            adc.width(ADC.WIDTH_12BIT)
            line_number = int(adc.read())
            float_size = 4
            with open('tablalut.bin','rb') as file:
                file.seek((line_number -1) * float_size,0)
                float_bytes = file.read(float_size)
                adc = struct.unpack('f',float_bytes)[0]
            Vout = adc * VS/ADCMAX
            rt = R1 * Vout / (VS - Vout)
            t = 1/(1/TO + log(rt/RO)/BETA)    # Temperatura en Kelvin
            tc = t - 273.15                   # Temperatura en Celsius
            
            return [tc,0]
        else:
            d = dht.DHT22(pinTermistor_DHT)
            d.measure()
            return [d.temperature(),d.humidity()]
    except:
        return [0,0]

def calcular_caja(anchura,profundidad,altura,grosor):
    imprime = ''
    fondo = 'fondo '+str(anchura) + ' x ' + str(altura) + "\n"
    lat_izq = 'lat_izq '+str(profundidad-grosor) + ' x ' + str(altura) + "\n"
    lat_der = 'lat_der '+str(profundidad-grosor) + ' x ' + str(altura) + "\n"
    techo = 'techo '+str(profundidad-grosor*2) + ' x ' + str(anchura-grosor*2) + "\n"
    suelo = 'suelo '+str(profundidad-grosor*2) + ' x ' + str(anchura-grosor*2) + "\n"
    frontal = 'frontal '+str(anchura) + ' x ' + str(altura) + "\n"
    imprime = fondo + lat_izq + lat_der + techo + suelo + frontal
    anchura = anchura / 100
    profundidad = profundidad / 100
    altura = altura / 100
    grosor = grosor / 100
    area = (anchura * altura + (profundidad-grosor) * altura * 2 + (profundidad-grosor*2)
    * (anchura-grosor*2) * 2 + anchura * altura)
    imprime+=('watios '+str (
    f'{((anchura-grosor*2)*(profundidad-grosor*2)*(altura-grosor*2))*100:.2f}')
    + "\n" + 'area ' + str(f'{area}'))
    return imprime

def cambiar_pass(length=6):
    import urandom
    characters = 'abcdefghjkmnpqrstuvwxyz123456789'
    password = ''.join([characters[urandom.getrandbits(6)
    % len(characters)] for _ in range(length)])
    return password

def registrar_valores():
    if v.contador_valores == 0:
        v.contador_valores = time.ticks_ms()
    elif time.ticks_ms() >= (v.contador_valores + v.TIEMPO_VALORES):
        archivo = 'datos.bin'
        if archivo in uos.listdir()\
            and uos.stat(archivo)[6] <= v.BYTES_FICHERO\
            or (not archivo in uos.listdir()):
            with open(archivo,'ab') as file:
                valores_salas = [v.ts1 if v.ts1[0]!=0 else None,v.ts2 if
                                v.ts2[0]!=0 else None,v.ts3 if v.ts3[0]!=0 else None]
                for indice,valor in enumerate(valores_salas):
                    if valor:
                        valor.append(v.rtc.datetime()[4] + v.rtc.datetime()[5] / 60.0)
                        valor.append(indice)
                for valor in valores_salas:
                    if valor:
                        file.write(struct.pack('f',valor[0]))
                        file.write(struct.pack('f',valor[1]))
                        file.write(struct.pack('f',valor[2]))
                        file.write(struct.pack('i',valor[3]))
        v.contador_valores = 0


        
