#!/usr/bin/python
from subprocess import check_output
import socket
import time
import threading
import os
from datetime import datetime
from pyvesc import VESC
import time
import sys

# uart setup
serial_port = '/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_304-if00'


# watchdog stuff
heartbeat = time.time()
log_file = "/home/niko/logs/watchlog.log"


# setup connections
# connect to pi pico wifi
while True:
    if (b"192.168.4.17" in check_output(['/sbin/ifconfig', 'wlan0'], shell=True)):
        break
    time.sleep(1)
    print("waiting for link")

# connect to vesc
while True:
    try:
        motor = VESC(serial_port=serial_port)
        break
    except:
        time.sleep(.1)


# logging functions
def get_temp():
    output = check_output(["/bin/cat", "/sys/class/thermal/thermal_zone0/temp"])
    temp = int(output.decode())/1000
    return temp

def get_timestamp():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def log(data):
    with open(log_file, "a") as f:
        f.write(get_timestamp() + " " + str(data) + "\n")

log("init log")
log(get_temp())



# comms functions
# host udp server and printout all the data received
def udp_server():
    global heartbeat
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to the address and port
    addr = ('192.168.4.17', 10000)
    s.bind(addr)

    print('UDP Server is listening on {}:{}'.format(addr[0], addr[1]))

    while True:
        # receive data from client
        data, addr = s.recvfrom(1024)
        #print('Received from {}:{}'.format(addr[0], addr[1]))
        data = float(data.decode())


        # ensure that its within 0 to 1
        if data < 0:
            data = 0
        if data > 1:
            data = 1

        if abs(data) < .1:
            data = 0

        #data *= 10000
        #data = int(data)
        #print(data)
        motor.set_duty_cycle(data)

        # allows motor to coast when not accelerating
        if data == 0:
            motor.set_current(0)
        heartbeat = time.time()

def watchdog():
    # restarts program when watchdog timeout
    print("Watchdog thread started")
    while True:
        if time.time()-heartbeat > .3:
            print("Watchdog timeout")
            log("Watchdog timeout")
            log(get_temp())
            log(check_output(['/sbin/ifconfig', 'wlan0'], shell=True).decode())
            motor.set_current(0)
            motor.stop_heartbeat()

            time.sleep(1)
            #break
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    """
    motor.set_rpm(0)
    motor.stop_heartbeat()
    os._exit(1)
    """



t1 = threading.Thread(target=udp_server, args=())
t2 = threading.Thread(target=watchdog, args=())

t1.start()
t2.start()

t1.join()
t2.join()
