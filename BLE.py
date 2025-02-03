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
import struct
import time
import variables as v
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

class BLEUART:
    def __init__(self, ble, name, rxbuf=100):
        self._ble = ble
        #activa el bluetooth
        self._ble.active(True)
        #al método irq de la clase BLE de bluetooth se le pasa el método _irq de ésta clase
        self._ble.irq(self._irq)
        """se pasan uart_uuid,uart_tx y uart_rx a través de uart_service que tiene 2 tuplas
        y la función con [0] devuelve 2 valores"""
        self._tx_handle, self._rx_handle = self._ble.gatts_register_services((_UART_SERVICE,))[0]
        #tamaño máximo en bytes que puede recibir esp32 por parte del cliente
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        #set() es parecido a una lista [] 
        self._connections = set()
        #a self._handler se asignará una referencia de la función rx del módulo mensajes
        self._handler = None
        #publicita para que los dispositivos encuentren esp32 al escanear
        self._advertise(name)
        self.refdata = None
        v.activar_publi_bt = self._advertise
    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            #data[0] contiene conn_handle
            self.refdata = data[0]
            self._connections.add(data[0])
            v.conectado = True
            v.desconectar_x_tiempo = self.desconectar_por_tiempo
        elif event == _IRQ_CENTRAL_DISCONNECT:
            v.pass_correcto = False
            v.conectado = False
            self._connections.remove(data[0])
            #publicita esp32 para que los dispositivos se enteren de la desconexión
            if v.publicitar_bt:
                self._advertise(self._name)
        #si se reciben datos del dispositivo conectado y hay handle en el set ("lista")
        elif event == _IRQ_GATTS_WRITE and data[0] in self._connections:
            """si se le ha asignado a _handler la referencia a la función rx del módulo mensajes
            (en la llamada uart.irq(rx), sino es None"""
            if self._handler:
                """ejecuta la función rx() del modulo mensajes mediante la referencia
                que tiene a dicha función"""
                self._handler() 
    """éste método irq no tiene nada que ver con irq de la clase BLE() de bluetooth
    aquí se asigna una referencia del método rx (del modulo mensajes) a self._handler"""
    def irq(self, handler):
        self._handler = handler
    #lee los datos recibidos del cliente
    def read(self):
        return self._ble.gatts_read(self._rx_handle)
    #envía al cliente conectado la respuesta
    def write(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)
    def _advertise(self, name):
        self._name = name
        """\x02 2 bytes, \x01 Flags, \x06 flags especificos + longitud name + 1 byte, 0x09
        tipo campo Complete Local Name"""
        adv_data = bytearray(b'\x02\x01\x06') + bytearray((len(name) + 1, 0x09)) + bytearray(name, 'utf-8')
        """indica que esp32 se publicitara cada 0.5 seg para que sea escaneado y visto, más tiempo
        menos consumo de energía, lo inverso más consumo"""
        if not v.publicitar_bt:
            print('desactivado')
        self._ble.gap_advertise(500000, adv_data)
    def desconectar_por_tiempo(self):
        #primer_elemento = list(self._connections)[0]
        #if refdata in self._connections:
        v.pass_correcto = False
        v.conectado = False
        self._ble.gap_disconnect(self.refdata)
    
