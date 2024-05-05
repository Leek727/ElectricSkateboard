import network
import socket
import time
from machine import Pin, ADC
import uasyncio as asyncio
import socket
import random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send data to the server
addr = ('192.168.4.17', 10000)

# send data through udp to the server
def udp_send(data):
    # create a socket object
    
    s.sendto(str(data).encode(), addr)

    #print('Data sent to {}:{}'.format(addr[0], addr[1]))


led = Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT, value=0)

joystick = ADC(Pin(26))


# power cycle if ap not changing
def ap_mode(ssid, password):
    """
        creates wireless ap
    """
    global test_setpoint
    
    # Just making our internet connection
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    
    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])
    



async def main():
    print('Connecting to Network...')
    ap_mode("pi", "sdjfoisjdfoijsdfdf")

    print('Setting up webserver...')
    #asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))


    while True:
        await asyncio.sleep(.1)
        
        
        
        joystickY = joystick.read_u16()-32768
        joystickY /= 32768
        udp_send(joystickY)


# main init
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()



