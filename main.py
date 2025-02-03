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
if __name__== "__main__":
    import time
    import variables as v
    import funciones as f
    import mensajes
    
    while True:
        if f.luz_fase(v.fase_s1):
            f.regularSala(False,False,1,False)
        else:
            f.regularSala(False,False,1,True)
        if v.SALA2:
            if f.luz_fase(v.fase_s2):
                f.regularSala(False,False,2,False)
            else:
                f.regularSala(False,False,2,True)
        if v.SALA3:
            if f.luz_fase(v.fase_s3):
                f.regularSala(False,False,3,False)
            else:
                f.regularSala(False,False,3,True)
        if v.conectado and not v.pass_correcto:
            if v.c_desconexion != 0:
                if time.ticks_ms() > (v.c_desconexion + v.t_desconexion):
                    v.c_desconexion = 0
                    if v.desconectar_x_tiempo:
                        v.desconectar_x_tiempo()
            else:
                v.c_desconexion = time.ticks_ms()
        
        if not v.publicitar_bt:
            if v.c_t_bt_d != 0:
                if time.ticks_ms() > (v.c_t_bt_d + v.t_bt_d_publicidad):
                    v.c_t_bt_d = 0
                    v.publicitar_bt = True
                    v.activar_publi_bt('PHILIPS TV')
            else:
                v.c_t_bt_d = time.ticks_ms()
        
        
        if v.GUARDAR_VALORES:
            f.registrar_valores()
        if v.VENTILADORES_S1 or v.VENTILADORES_S2 or v.VENTILADORES_S3:
            f.ventiladores(v.TIEMPO_V)     
        if ((v.TERMISTOR_INSTALADO or v.DHT1_INSTALADO)
            or (v.TERMISTOR2_INSTALADO or v.DHT2_INSTALADO)
            or (v.TERMISTOR3_INSTALADO or v.DHT3_INSTALADO)):
            if not v.contador_temperatura_inicio:
                v.contador_temperatura_inicio = True
                v.contador_temperatura = time.ticks_ms()
            else:
                if time.ticks_ms() > (v.contador_temperatura + v.t_comprobar_temperatura):
                    v.ts1 = (f.temperatura(v.PIN_TERMISTOR_DHT1,v.TERMISTOR_INSTALADO) if
                            (v.SALA1 == 1 or v.SALA1 == 3) and
                            (v.TERMISTOR_INSTALADO or v.DHT1_INSTALADO) else [0,0])
                    v.ts2 = (f.temperatura(v.PIN_TERMISTOR_DHT2,v.TERMISTOR2_INSTALADO) if
                            v.SALA2 and (v.TERMISTOR2_INSTALADO or v.DHT2_INSTALADO) else [0,0])
                    v.ts3 = (f.temperatura(v.PIN_TERMISTOR_DHT3,v.TERMISTOR3_INSTALADO) if
                            v.SALA3 and (v.TERMISTOR3_INSTALADO or v.DHT3_INSTALADO) else [0,0])
                    if v.calefactor:
                        if v.contador_inicio_calefactor != 0:
                            v.contador_calefactor += time.ticks_ms() - v.contador_inicio_calefactor
                            v.contador_inicio_calefactor = 0
                        if f.temperatura(v.PIN_TERMISTOR_DHT1,v.TERMISTOR_INSTALADO)[0] < (v.TEMPERATURA + v.no_parpadeo_cale):
                            if v.contador_inicio_calefactor == 0:
                                v.contador_inicio_calefactor = time.ticks_ms()
                            v.PIN_CALEFACTOR.on()
                            v.no_parpadeo_cale = v.NO_PARPADEO_CALE
                        else:
                            v.PIN_CALEFACTOR.off()
                            v.no_parpadeo_cale = 0
                    if v.calefactor2:
                        if v.contador_inicio_calefactor2 != 0:
                            v.contador_calefactor2 += time.ticks_ms() - v.contador_inicio_calefactor2
                            v.contador_inicio_calefactor2 = 0
                        if f.temperatura(v.PIN_TERMISTOR_DHT2,v.TERMISTOR2_INSTALADO)[0] < (v.TEMPERATURA2 + v.no_parpadeo_cale2):
                            if v.contador_inicio_calefactor2 == 0:
                                v.contador_inicio_calefactor2 = time.ticks_ms()
                            v.PIN_CALEFACTOR2.on()
                            v.no_parpadeo_cale2 = v.NO_PARPADEO_CALE2
                        else:
                            v.PIN_CALEFACTOR2.off()
                            v.no_parpadeo_cale2 = 0
                    if v.calefactor3:
                        if v.contador_inicio_calefactor3 != 0:
                            v.contador_calefactor3 += time.ticks_ms() - v.contador_inicio_calefactor3
                            v.contador_inicio_calefactor3 = 0
                        if f.temperatura(v.PIN_TERMISTOR_DHT3,v.TERMISTOR3_INSTALADO)[0] < (v.TEMPERATURA3 + v.no_parpadeo_cale3):
                            if v.contador_inicio_calefactor3 == 0:
                                v.contador_inicio_calefactor3 = time.ticks_ms()
                            v.PIN_CALEFACTOR3.on()
                            v.no_parpadeo_cale3 = v.NO_PARPADEO_CALE3
                        else:
                            v.PIN_CALEFACTOR3.off()
                            v.no_parpadeo_cale3 = 0
                    v.contador_temperatura_inicio = False
        
