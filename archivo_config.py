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
import struct,uos
def fichero_configuracion(lista):
    archivo = 'config.bin'
    salas_y_pwm = lista[:9] #booleanos
    temp_y_hum_max = lista[9:18] #floats
    temp_min_y_pot_cale = lista[18:24] #floats
    aux_cal_term_dht_gval = lista[24:35] #booleanos
    v_rel_x = lista[35:38] #enteros
    venti_y_pwm = lista[38:44] #booleanos
    w_max_salas_pot = lista[44:] #floats
    #try:
    empaquetado = struct.pack(
    'BBBBBBBBBfffffffffffffffBBBBBBBBBBBiiiBBBBBBffffffffff',
    *salas_y_pwm,*temp_y_hum_max,*temp_min_y_pot_cale,
    *aux_cal_term_dht_gval,*v_rel_x,*venti_y_pwm,
    *w_max_salas_pot)
    #except TypeError as e:
    #print(f"Error al empaquetar: {e}")
    with open(archivo, 'wb') as file:
        file.write(empaquetado)
        
def leer_configuracion():
    archivo = 'config.bin'
    datos_unpack = None
    with open(archivo, 'rb') as file:
        datos = file.read(uos.stat(archivo)[6])
        #desempaqueta los datos
        datos_unpack = struct.unpack(
        'BBBBBBBBBfffffffffffffffBBBBBBBBBBBiiiBBBBBBffffffffff',datos)
    return datos_unpack
   
def archivo_existe(nombre_archivo):
    import uos
    try:
        uos.stat(nombre_archivo)
    except: #antes except OSError:
        return False
    return True
    
def variables_config():
    import variables as v
    return [v.SALA1,v.SALA2,v.SALA3,v.SETAS_S1,v.SETAS_S2,v.SETAS_S3,
                v.PWM_S1,v.PWM_S2,v.PWM_S3,v.TEMPERATURA_MAX,
                v.TEMPERATURA2_MAX,v.TEMPERATURA3_MAX,
                v.hs1_fc[0],v.hs1_fc[1],v.hs2_fc[0],v.hs2_fc[1],
                v.hs3_fc[0],v.hs3_fc[1],
                v.TEMPERATURA,v.POTENCIA_CALEFACTOR,
                v.TEMPERATURA2,v.POTENCIA_CALEFACTOR2,
                v.TEMPERATURA3,v.POTENCIA_CALEFACTOR3,
                v.AUXILIAR_INSTALADO,
                v.CALEFACTOR_INSTALADO,v.CALEFACTOR2_INSTALADO,
                v.CALEFACTOR3_INSTALADO,
                v.TERMISTOR_INSTALADO,v.TERMISTOR2_INSTALADO,
                v.TERMISTOR3_INSTALADO,
                v.DHT1_INSTALADO,v.DHT2_INSTALADO,v.DHT3_INSTALADO,
                v.GUARDAR_VALORES,
                v.v_s1_reg_x,v.v_s2_reg_x,v.v_s3_reg_x,
                v.VENTILADORES_S1,v.VENTILADORES_S2,v.VENTILADORES_S3,
                v.PWM_VS1,v.PWM_VS2,v.PWM_VS3,
                v.WMAX_S1,v.WMAX_S2,v.WMAX_S3,
                v.PT_R,v.PT_B,v.PT_A,v.PT_AUX,
                v.PT_ECS1,v.PT_ECS2,v.PT_ECS3]

def cadena_a_lista(cadena,validar):
    try:
        return lista_sin_str(cadena.replace(')','').split(','),validar)
    except OSError:
        return False
    
def lista_sin_str(lista,validar):
    for a in range(len(lista)):
        if isinstance(lista[a], str):
            if lista[a].lower() == 'true':
                lista[a] = 1
            elif lista[a].lower() == 'false':
                lista[a] = 0
            elif '.' in lista[a]:
                lista[a] = float(lista[a])
            elif lista[a].isdigit():
                lista[a] = int(lista[a])
    if validar == 1 and len(lista) == 9:
        if lista[0] in (1,3,0) \
            and any(x in lista[1:] for x in (0,1)):
            return lista
    elif validar == 4 and len(lista) == 11:
        if any(x in lista[:] for x in (0,1)):
            return lista
    elif validar == 6 and len(lista) == 6:
        if any(x in lista[:] for x in (0,1)):
            return lista
    elif validar == 2 and len(lista) == 9:
        return lista
    elif validar == 3 and len(lista) == 6:
        return lista
    elif validar == 5 and len(lista) == 3:
        return lista
    elif validar == 7 and len(lista) == 10:
        return lista
    else:
        return False
