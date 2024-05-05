#!/usr/bin/python
from subprocess import check_output
import socket
import RPi.GPIO as GPIO
import time
import threading
import os
from datetime import datetime

# pwm setup
pwm_pin = 32

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pwm_pin,GPIO.OUT)
pi_pwm = GPIO.PWM(pwm_pin,1000) # pin, 1khz
pi_pwm.start(0)

# watchdog stuff
heartbeat = time.time()
log_file = "logs/watchlog.log"

def get_temp():
    output = check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
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
        data += 1 # scale -1 to 1 to 0 to 2
        data /= 2
        data *= 100 # scale to pwm percent
        data = int(data)
        #data = 50
        pi_pwm.ChangeDutyCycle(data)
        #print(f"duty cycle: {data}")

        heartbeat = time.time()
        #time.sleep(10)

def watchdog():
    # definitely not safe TODO better solution
    print("Watchdog thread started")
    while True:
        #print(time.time()-heartbeat)
        # 50ms watchdog
        if time.time()-heartbeat > .3:
            print("Watchdog timeout")
            log("Watchdog timeout")
            log(get_temp())
            break

    while True:
        # set pwm always to 50%
        #pi_pwm.ChangeDutyCycle(50)
        os._exit(1)


while True:
    if (b"192.168.4.17" in check_output(['/sbin/ifconfig', 'wlan0'], shell=True)):
        break
    time.sleep(1)
    print("waiting for link")



t1 = threading.Thread(target=udp_server, args=())
t2 = threading.Thread(target=watchdog, args=())

t1.start()
t2.start()

t1.join()
t2.join()
