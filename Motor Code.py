#Just used to test motors and DIO pins
import time
import board
import pulseio
import adafruit_irremote
from digitalio import DigitalInOut, Direction

motor = DigitalInOut(board.D2)
motor.direction = Direction.OUTPUT
motor.value = False

while(True):
    if(motor.value):
        motor.value = False
    else:
        motor.value = True
    time.sleep(0.5)
