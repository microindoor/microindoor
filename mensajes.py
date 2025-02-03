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
import bluetooth
import machine
import time
import variables as v
import funciones as f
from BLE import BLEUART
name = 'PHILIPS AV'
ble = bluetooth.BLE()
uart = BLEUART(ble,name)
rtc = machine.RTC()

def rx():
    cadena = ''
    rx_buffer = uart.read().decode().strip()
    if v.pass_correcto:
        uart.write('esp32 says:'+ str(rx_buffer) +'\n')
        if rx_buffer == 'temp':
            import esp32
            uart.write('Temperatura ' + str( ( (esp32.raw_temperature()-32)*5/9) )+ "\n")
        elif rx_buffer == 'publicitar_bt':
            if v.publicitar_bt:
                v.publicitar_bt = False
                uart.write('publicidad desactivada' + "\n")
            else:
                v.publicitar_bt = True
                uart.write('publicidad activada' + "\n")
        elif rx_buffer == 'cambiar_pass':
            v.PASS_BT = f.cambiar_pass()
            uart.write('pass nuevo: ' + str(v.PASS_BT) + "\n")
        elif rx_buffer == 'memoria':
            import gc
            uart.write(str(gc.mem_free()) + 'B' + "\n")
        elif rx_buffer.startswith('config_'):
            import struct,archivo_config as c
            que_mostrar = rx_buffer.replace('config_',"")
            if que_mostrar.startswith('salas_pwm'): 
                lista = c.cadena_a_lista(
                    que_mostrar.replace('salas_pwm(',""),1)
                if not lista:
                    uart.write(str('mala sintaxis ') + str(lista) + "\n")
                else:
                    lista_config = c.variables_config()
                    lista_config[:9] = lista[:]
                    c.fichero_configuracion(lista_config)
                    uart.write(str(len(lista_config)) + "\n")
                    uart.write('configuración guardada' + "\n")
            elif que_mostrar.startswith('aux_cal_term_dht_gval'):
                lista = c.cadena_a_lista(
                    que_mostrar.replace('aux_cal_term_dht_gval(',""),4)
                if not lista:
                    uart.write(str('mala sintaxis ') + str(lista) + "\n")
                else:
                    lista_config = c.variables_config()
                    lista_config[24:35] = lista[:]
                    c.fichero_configuracion(lista_config)
                    uart.write(str(len(lista_config)) + "\n")
                    uart.write('configuración guardada' + "\n")
        elif rx_buffer.startswith('leerbinario'):
            #import archivo_config as c
            #if c.archivo_existe('datos.bin'):
            try:
                que_mostrar = rx_buffer.replace('leerbinario',"")
                import struct,uos
                contador = 0
                archivo = 'datos.bin'
                tamaño_archivo = uos.stat(archivo)[6]
                tamaño_lectura = 2000 if tamaño_archivo >= 2000 else tamaño_archivo
                bloque_size = 16  # Tamaño del bloque a leer y procesar en cada iteración
                imprimir = ''
                with open(archivo, 'rb') as file:
                    # Mover el puntero del archivo a `tamaño_lectura` bytes desde el final
                    file.seek(-tamaño_lectura, 2)  # 2 significa desde el final del archivo
                    # Leer y procesar en bloques pequeños
                    bytes_leidos = 0
                    while bytes_leidos < tamaño_lectura:
                        # Leer el siguiente bloque
                        bloque = file.read(bloque_size)
                        if not bloque:
                            break
                        # Procesar el bloque si es de tamaño suficiente
                        if len(bloque) >= 12:
                            # Leer 12 bytes para tres floats
                            float_data = bloque[:12]
                            valores_float = struct.unpack('fff', float_data)
                            val_ft = [f'{val:.1f}' for val in valores_float]
                            # Leer 4 bytes para un entero si hay suficientes bytes restantes
                            if len(bloque) >= 16:
                                int_data = bloque[12:16]
                                entero = struct.unpack('i', int_data)[0]
                                if que_mostrar == 't':
                                    imprimir += str(val_ft[0]) + "\n"
                                elif que_mostrar == 'h':
                                    imprimir += str(val_ft[1]) + "\n"
                                elif que_mostrar == 'ts':
                                    imprimir += str(val_ft[0]) + ',' + str(entero) + "\n"
                                elif que_mostrar == 'hs':
                                    imprimir += str(val_ft[1]) + ',' + str(entero) + "\n"
                                else:
                                    imprimir += str(val_ft[0]) + ',' + str(val_ft[1]) \
                                    + ',' + str(val_ft[2]) + ',' + str(entero) + "\n"
                        # Actualizar el contador de bytes leídos
                        bytes_leidos += len(bloque)
                        contador+=1
                        if contador == 12:
                            uart.write(imprimir)
                            imprimir = ''
                            contador = 0
            except:
                uart.write('Parece no haber datos' + "\n")
        elif rx_buffer == 'ds1' and not v.SALA1 == False:
            f.regularSala(False,True,1,False)
            uart.write('Posicion sala1: ' + str(v.pos_s1) + "\n")
        elif rx_buffer == 'is1' and not v.SALA1 == False:
            f.regularSala(True,False,1,False)
            uart.write('Posicion: ' + str(v.pos_s1) + "\n")
        elif rx_buffer == 'ds2' and v.SALA2:
            f.regularSala(False,True,2,False)
            uart.write('Posicion sala2: ' + str(v.pos_s2) + "\n")
        elif rx_buffer == 'is2' and v.SALA2:
            f.regularSala(True,False,2,False)
            uart.write('Posicion: ' + str(v.pos_s2) + "\n")
        elif rx_buffer == 'ds3' and v.SALA3:
            f.regularSala(False,True,3,False)
            uart.write('Posicion sala3: ' + str(v.pos_s3) + "\n")
        elif rx_buffer == 'is3' and v.SALA3:
            f.regularSala(True,False,3,False)
            uart.write('Posicion: ' + str(v.pos_s3) + "\n")
        elif rx_buffer == 'ivs1':
            f.regular_ventiladores(True,1)
            uart.write('Posicion: ' + str(v.pos_vs1) + "\n")
        elif rx_buffer == 'dvs1':
            f.regular_ventiladores(False,1)
            uart.write('Posicion: ' + str(v.pos_vs1) + "\n")
        elif rx_buffer == 'ivs2':
            f.regular_ventiladores(True,2)
            uart.write('Posicion: ' + str(v.pos_vs2) + "\n")
        elif rx_buffer == 'dvs2':
            f.regular_ventiladores(False,2)
            uart.write('Posicion: ' + str(v.pos_vs2) + "\n")
        elif rx_buffer == 'ivs3':
            f.regular_ventiladores(True,3)
            uart.write('Posicion: ' + str(v.pos_vs3) + "\n")
        elif rx_buffer == 'dvs3':
            f.regular_ventiladores(False,3)
            uart.write('Posicion: ' + str(v.pos_vs3) + "\n")
        elif rx_buffer == 'fs1':
            if v.fase_s1:
                v.fase_s1 = False
                v.humedad_s1 = v.hs1_fc[0]
            else:
                v.fase_s1 = True
                v.humedad_s1 = v.hs1_fc[1]
            uart.write('Sala1: ' + str(v.fase_s1) + "\n")
        elif rx_buffer == 'fs2' and v.SALA2:
            if v.fase_s2:
                v.fase_s2 = False
                v.humedad_s2 = v.hs2_fc[0]
            else:
                v.fase_s2 = True
                v.humedad_s2 = v.hs2_fc[1]
            uart.write('Sala2: ' + str(v.fase_s2) + "\n")
        elif rx_buffer == 'fs3' and v.SALA3:
            if v.fase_s3:
                v.fase_s3 = False
                v.humedad_s3 = v.hs3_fc[0]
            else:
                v.fase_s3 = True
                v.humedad_s3 = v.hs3_fc[1]
            uart.write('Sala3: ' + str(v.fase_s3) + "\n")
        elif rx_buffer == 'freq':
            uart.write('Frecuencia: ' + str(machine.freq()/1000000) + ' Mhz' "\n")
        elif rx_buffer == 'aux' and v.AUXILIAR_INSTALADO:
            v.usar_led_auxiliar = True
            uart.write('Activado led auxiliar' "\n")
        elif rx_buffer == 'daux' and v.AUXILIAR_INSTALADO:
            f.leds_y_led_auxiliar()
            uart.write('Desactivado led auxiliar' "\n")
        elif rx_buffer == 'calefactor' and v.CALEFACTOR_INSTALADO:
            if v.calefactor:
                v.calefactor = False
                v.PIN_CALEFACTOR.off()
                uart.write('Calefactor desactivado' "\n")
            else:
                v.calefactor = True
                uart.write('Calefactor activado' "\n")
        elif rx_buffer == 'calefactor2' and v.CALEFACTOR2_INSTALADO:
            if v.calefactor2:
                v.calefactor2 = False
                v.PIN_CALEFACTOR2.off()
                uart.write('Calefactor2 desactivado' "\n")
            else:
                v.calefactor2 = True
                uart.write('Calefactor2 activado' "\n")
        elif rx_buffer == 'calefactor3' and v.CALEFACTOR3_INSTALADO:
            if v.calefactor3:
                v.calefactor3 = False
                v.PIN_CALEFACTOR3.off()
                uart.write('Calefactor3 desactivado' "\n")
            else:
                v.calefactor3 = True
                uart.write('Calefactor3 activado' "\n")
        elif rx_buffer == 'rcalefactor':
            if v.CALEFACTOR_INSTALADO and v.calefactor:
                if v.contador_calefactor != 0:
                    uart.write('Gasto calefactor: ' +
                    str(v.contador_calefactor/1000/3600*v.POTENCIA_CALEFACTOR) + 'wh' + "\n")
                    v.contador_calefactor = 0
                    uart.write('Gasto reseteado' + "\n")
                else:
                    uart.write('Ningún gasto que resetear' + "\n")
        elif rx_buffer == 'gcalefactor':
            if v.CALEFACTOR_INSTALADO and v.calefactor:
                if v.contador_calefactor != 0:
                    uart.write('Gasto calefactor: ' +
                    str(v.contador_calefactor/1000/3600*v.POTENCIA_CALEFACTOR) + 'wh' + "\n")
                else:
                    uart.write('Ningún gasto' + "\n")
        elif rx_buffer.startswith('freq'):
            frecuencia = rx_buffer.replace('freq',"")
            if frecuencia.isdigit():
                frecuencia_ = int(frecuencia) * 1000000
                if (frecuencia_ != (80 * 1000000) and frecuencia_ != (160 * 1000000) and
                frecuencia_ != (240 * 1000000)):
                    uart.write('Frecuencia fuera de rango, 80, 160 o 240 Mhz' + "\n")
                else:
                    machine.freq(frecuencia_)
                    uart.write('Cambiada la frecuencia a ' + frecuencia + ' Mhz' "\n")
        elif rx_buffer.startswith('tbtd'):
            tbtd = rx_buffer.replace('tbtd',"")
            if tbtd.isdigit():
                tbtd_ = int(tbtd)
                if tbtd_ <= 168:
                    v.t_bt_d_publicidad = tbtd_ * 3600 * 1000
                    uart.write('Publicidad bt en ' + str(tbtd_) + ' Horas' "\n")
        elif rx_buffer.startswith('ponerhora'):
            hora = str(rx_buffer.replace('ponerhora',""))
            try:
                tupla_real = tuple(hora.split(':'))
                if isinstance(tupla_real,tuple):
                    año = rtc.datetime()[0]
                    mes = rtc.datetime()[1]
                    dia = rtc.datetime()[2]
                    x = rtc.datetime()[3]
                    hour = int(tupla_real[0])
                    minuto = int(tupla_real[1])
                    segundo = rtc.datetime()[6]
                    milisegundos = rtc.datetime()[7]
                    rtc.datetime([año,mes,dia,x,hour,minuto,segundo,milisegundos])
                else:
                    uart.write('El string '+
                    hora+' no representa una tupla válida, ejemplo: ponerhora17:23' + "\n")
                    uart.write(tupla_real[0])
            except:
                uart.write('formato incorrecto, ejemplo ponerhora17:35 hora, minuto '+ "\n")
                uart.write(tupla_real[0])
        elif rx_buffer.startswith('calcularcaja'):
            medidas = str(rx_buffer.replace('calcularcaja',""))
            try:
                tupla_real = tuple(medidas.split(':'))
                if isinstance(tupla_real,tuple):
                    anchura = float(tupla_real[0])
                    profundidad = float(tupla_real[1])
                    altura = float(tupla_real[2])
                    grosor = float(tupla_real[3])
                    uart.write(f.calcular_caja(anchura,profundidad,altura,grosor) + "\n")
                else:
                    uart.write('Error' + "\n")
            except:
                uart.write('formato incorrecto'+ "\n")
        elif rx_buffer == 'tauxiliar':
            uart.write(str(v.tiempo_led_auxiliar / 60 / 60 / 1000) + ' horas'+ "\n")
        elif rx_buffer.startswith('tauxiliar') and not rx_buffer == 'tauxiliar':
            horas = str(rx_buffer.replace('tauxiliar',""))
            if horas.isdigit():
               v.tiempo_led_auxiliar = int(horas) * 60 * 60 * 1000
        elif rx_buffer.startswith('ledfreq'):
            fled = str(rx_buffer.replace('ledfreq',""))
            try:
                tupla_real = tuple(fled.split(':'))
                if isinstance(tupla_real,tuple):
                    color = str(tupla_real[0])
                    frecuencia = int(tupla_real[1])
                    if v.SALA1 == 3 and v.PWM_S1 and (color == 'ROJO' or
                    color == 'BLANCO' or color == 'AZUL'):
                        if color == 'ROJO':
                            v.PIN_ROJO.freq(frecuencia)
                            v.fr_rojo = frecuencia
                        elif color == 'AZUL':
                            v.PIN_AZUL.freq(frecuencia)
                            v.fr_azul = frecuencia
                        elif color == 'BLANCO':
                            v.PIN_BLANCO.freq(frecuencia)
                            v.fr_blanco = frecuencia
                    elif SALA1 == 1 and v.PWM_S1 and color == 'ECOMPLETOS1':
                        v.PIN_ECOMPLETOS1.freq(frecuencia)
                        v.fr_ecompletos1 = frecuencia
                    elif SALA2 and v.PWM_S2 and color == 'ECOMPLETOS2':
                        v.PIN_ECOMPLETOS2.freq(frecuencia)
                        v.fr_ecompletos2 = frecuencia
                    elif SALA3 and v.PWM_S3 and color == 'ECOMPLETOS3':
                        v.PIN_ECOMPLETOS3.freq(frecuencia)
                        v.fr_ecompletos3 = frecuencia
                    elif v.PWM_S1 and color == 'AUXILIAR':
                        v.PIN_AUXILIAR.freq(frecuencia)
                        v.fr_auxiliar = frecuencia
                else:
                    uart.write('El string '+fled+
                    ' no representa una tupla válida, ejemplo: ledfreqROJO:15000' + "\n")
            except:
                uart.write('formato incorrecto, ejemplo ledfreqROJO:15000'+ "\n")
        elif rx_buffer.startswith('hora'):
             uart.write(str(rtc.datetime()[4])+':'+str(rtc.datetime()[5]) + "\n")
        elif rx_buffer == 'help':
            cadena+='is1 o is2' +"\n"
            cadena+='ds1 o ds2' +"\n"
            cadena+='fs1 o fs2' +"\n"
            cadena+='aux / daux' +"\n"
            cadena+='hora' +"\n"
            cadena+='ponerhora17:13' +"\n"
            cadena+='freq' +"\n"
            cadena+='freq80' +"\n"
            cadena+='calefactor' +"\n"
            uart.write(cadena)
            cadena = ''
            cadena+='tauxiliar9' +"\n"
            cadena+='tbtd3' +"\n"
            cadena+='tauxiliar' +"\n"
            cadena+='gcalefactor' +"\n"
            cadena+='rcalefactor' +"\n"
            cadena+='calcularcaja35:20:29:0.3' +"\n"
            cadena+='cambiar_pass' +"\n"
            cadena+='publicitar_bt' +"\n"
            cadena+='leerbinario[t|h|ts|hs]' +"\n"
            uart.write(cadena)
        elif rx_buffer == 'info':
            cadena = ''
            cadena+=('pos_s1: ' + str(v.pos_s1) + ', pos_s2: '
            + str(v.pos_s2) + ', pos_s3: ' + str(v.pos_s3) + "\n")
            vfs1 = 18 if v.fase_s1 else 12
            vfs2 = 18 if v.fase_s2 else 12
            vfs3 = 18 if v.fase_s3 else 12
            cadena+='fs1: ' + str(vfs1) + ', fs2: ' + str(vfs2) + ', fs3: ' + str(vfs3)+ "\n"
            if v.AUXILIAR_INSTALADO:
                cadena+=('Luz_aux: ' + str(v.usar_led_auxiliar) + ' R' + str(v.s_rojo)
                + ', A' + str(v.s_azul) + ', B' + str(v.s_blanco) + "\n")
            cadena+=(str(machine.freq()/1000000)) + 'Mhz' + "\n"
            cadena+=str(rtc.datetime()[4]) + ':' + str(rtc.datetime()[5]) + "\n"
            if v.CALEFACTOR_INSTALADO and v.TERMISTOR_INSTALADO:
                cadena+='Cale: ' + str(v.calefactor)  + "\n"
            if v.CALEFACTOR2_INSTALADO and v.TERMISTOR2_INSTALADO:
                cadena+='Cale2: ' + str(v.calefactor2)  + "\n"
            if v.CALEFACTOR3_INSTALADO and v.TERMISTOR3_INSTALADO:
                cadena+='Cale3: ' + str(v.calefactor3)  + "\n"
            cadena+=('s1: ' + str(v.SALA1) + ', s2: ' + str(v.SALA2) + ', s3: '
            + str(v.SALA3) +  "\n")
            cadena+=('wmax_s1: ' + str(v.WMAX_S1) + ', s2: ' + str(v.WMAX_S2) + ', s3: '
            + str(v.WMAX_S3) +  "\n")
            if v.PWM_S1 and v.SALA1 == 1:
                cadena+='ES1: ' + str(v.fr_ecompletos1) +  "\n"
            elif v.PWM_S1 and v.SALA1 == 3:
                cadena+=('R:' + str(v.fr_rojo) + ',A:' + str(v.fr_azul) + ' ,B:'
                + str(v.fr_blanco) +  "\n")
            else:
                cadena+='NoPWM_S1' + "\n"
            uart.write(cadena)
            cadena = ''
            if v.PWM_S2 and v.SALA2:
                cadena+='ES2:' + str(v.fr_ecompletos2) +  "\n"
            else:
                cadena+='NoPWM_S2' + "\n"
            if v.PWM_S3 and v.SALA3:
                cadena+='ES3:' + str(v.fr_ecompletos3) +  "\n"
            else:
                cadena+='NoPWM_S3' + "\n"
            if v.PWM_S1 and v.AUXILIAR_INSTALADO:
                cadena+='AUX:' + str(v.fr_auxiliar) +  "\n"
                cadena+='t_Aux: ' + str(v.tiempo_led_auxiliar / 1000 / 60 / 60) + "\n"
            if v.pocaPotencia:
                cadena+='R,B,A - w en relación PT' + "\n"
            uart.write(cadena)
            cadena = ''
            if v.CALEFACTOR_INSTALADO and v.calefactor:
                if v.calefactor:
                    cadena+=('Gcale: '
                    + str(v.contador_calefactor/1000/3600*v.POTENCIA_CALEFACTOR)
                    + 'wh' + "\n")
            if v.CALEFACTOR2_INSTALADO and v.calefactor2:
                if v.calefactor2:
                    cadena+=('Gcale2: '
                    + str(v.contador_calefactor2/1000/3600*v.POTENCIA_CALEFACTOR2)
                    + 'wh' + "\n")
            if v.CALEFACTOR3_INSTALADO and v.calefactor3:
                if v.calefactor3:
                    cadena+=('Gcale3: '
                    + str(v.contador_calefactor3/1000/3600*v.POTENCIA_CALEFACTOR3)
                    + 'wh' + "\n")
            if v.SALA1 == 3:
                cadena+=('R:' + str(v.N_PIN_ROJO) + ' A:' + str(v.N_PIN_AZUL)
                + ' B:' + str(v.N_PIN_BLANCO) + "\n")
            if v.AUXILIAR_INSTALADO:
                cadena+='AUX: '+ str(v.N_PIN_AUXILIAR) + "\n"
            if v.SALA1 == 1:
                cadena+='ES1: ' + str(v.N_PIN_ECOMPLETOS1) + "\n"
            if v.SALA2:
                cadena+='ES2: ' + str(v.N_PIN_ECOMPLETOS2) + "\n"
            if v.SALA3:
                cadena+='ES3: ' + str(v.N_PIN_ECOMPLETOS3) + "\n"
            if (v.TERMISTOR_INSTALADO or v.DHT1_INSTALADO):
                if v.TERMISTOR_INSTALADO:
                    cadena+='TERM: ' + str(v.N_PIN_TERMISTOR) + "\n"
                else:
                    cadena+='DHT1: ' + str(v.N_PIN_DHT1) + "\n"
            if v.SALA2 and (v.TERMISTOR2_INSTALADO or v.DHT2_INSTALADO):
                if v.TERMISTOR2_INSTALADO:
                    cadena+='TERM2: ' + str(v.N_PIN_TERMISTOR2) + "\n"
                else:
                    cadena+='DHT2: ' + str(v.N_PIN_DHT2) + "\n"
            uart.write(cadena)
            cadena = ''
            if v.SALA3 and (v.TERMISTOR3_INSTALADO or v.DHT3_INSTALADO):
                if v.TERMISTOR3_INSTALADO:
                    cadena+='TERM3: ' + str(v.N_PIN_TERMISTOR3) + "\n"
                else:
                    cadena+='DHT3: ' + str(v.N_PIN_DHT3) + "\n"
            if v.CALEFACTOR_INSTALADO and v.TERMISTOR_INSTALADO:
                cadena+='CALE: ' + str(v.N_PIN_CALEFACTOR) + "\n"
            if v.CALEFACTOR2_INSTALADO and v.TERMISTOR2_INSTALADO:
                cadena+='CALE2: ' + str(v.N_PIN_CALEFACTOR2) + "\n"
            uart.write(cadena)
            cadena = ''
            if v.CALEFACTOR3_INSTALADO and v.TERMISTOR3_INSTALADO:
                cadena+='CALE3: ' + str(v.N_PIN_CALEFACTOR3) + "\n"
            if v.VENTILADORES_S1:
                cadena+='V_S1: ' + str(v.N_PIN_VENTILADORES_S1) + "\n"
            if v.VENTILADORES_S2:
                cadena+='V_S2: ' + str(v.N_PIN_VENTILADORES_S2) + "\n"
            if v.VENTILADORES_S3:
                cadena+='V_S3: ' + str(v.N_PIN_VENTILADORES_S3) + "\n"
            if (v.TERMISTOR_INSTALADO or v.DHT1_INSTALADO):
                cadena+='S1:'+str(v.ts1[0]) + 'º'
                cadena+=(','+str(v.ts1[1]) + '%HR' + "\n") if v.DHT1_INSTALADO else "\n"
            if (v.TERMISTOR2_INSTALADO or v.DHT2_INSTALADO):
                cadena+='S2:'+str(v.ts2[0]) + 'º'
                cadena+=(','+str(v.ts2[1]) + '%HR' + "\n") if v.DHT2_INSTALADO else "\n"
            if (v.TERMISTOR3_INSTALADO or v.DHT3_INSTALADO):
                cadena+='S3:'+str(v.ts3[0]) + 'º'
                cadena+=(','+str(v.ts3[1]) + '%HR' + "\n") if v.DHT3_INSTALADO else "\n"
            cadena+=('tbtd: ' + str(v.t_bt_d_publicidad/(3600 * 1000)) + 'h' + "\n")
            cadena+=('publi_bt: ' + str(v.publicitar_bt) + "\n")
            import uos
            try:
                uos.stat('datos.bin')
                cadena+='datos.bin ' + str(uos.stat('datos.bin')[6]) + 'B' + "\n"
            except:
                0
            uart.write(cadena)
    elif rx_buffer == v.PASS_BT and rx_buffer != ''\
        and v.var_intentos < v.INTENTOS_PASS:
        v.pass_correcto = True
        v.var_intentos = 0
        uart.write('Desbloqueado')
    else:
        v.var_intentos+=1
uart.irq(rx)

