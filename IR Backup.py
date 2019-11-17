import time
import board
import pulseio
import adafruit_irremote
from digitalio import DigitalInOut, Direction

import adafruit_dotstar
import board
led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
led.brightness=0.0

IRPin = board.D2 #Pin connected to IR receiver.

lightOnMotor = DigitalInOut(board.D0) #Pin connected to light on motor.
lightOnMotor.direction = Direction.OUTPUT
lightOnMotor.value = False

lightOffMotor = DigitalInOut(board.D1) #Pin connected to light off motor.
lightOffMotor.direction = Direction.OUTPUT
lightOffMotor.value = False

fanMotor = DigitalInOut(board.D3) #Pin connected to fan motor.
fanMotor.direction = Direction.OUTPUT
fanMotor.value = False

doorMotor = DigitalInOut(board.D4) #Pin connected to door motor.
doorMotor.direction = Direction.OUTPUT
doorMotor.value = False

#Expected pulse, pasted in from previous recording REPL session:
button1=9130, 4513, 598, 543, 601, 540, 604, 538, 606, 538, 595, 543, 601, 541, 603, 538, 606, 535, 599, 1655, 602, 1653, 604, 1651, 605, 1649, 598, 1657, 600, 1654, 603, 538, 606, 1659, 587, 543, 601, 539, 605, 536, 597, 544, 600, 1654, 603, 537, 606, 535, 599, 541, 603, 1651, 605, 1650, 597, 1667, 589, 1655, 602, 539, 615, 1639, 597, 1658, 599, 1655, 602
button2=9126, 4510, 600, 541, 603, 538, 606, 535, 598, 543, 601, 567, 576, 565, 579, 561, 573, 569, 575, 1652, 608, 1646, 607, 1648, 599, 1655, 601, 1654, 603, 1651, 605, 563, 581, 1647, 599, 1655, 602, 566, 578, 563, 581, 560, 573, 1654, 603, 565, 579, 562, 571, 570, 574, 567, 577, 1650, 607, 1647, 600, 1654, 603, 566, 577, 1650, 607, 1653, 593, 1656, 601
button3=9121, 4515, 606, 535, 599, 541, 603, 538, 605, 535, 599, 541, 603, 537, 606, 535, 598, 542, 602, 1651, 606, 1648, 598, 1656, 600, 1654, 603, 1651, 605, 1649, 597, 544, 600, 1653, 604, 538, 606, 1648, 598, 543, 601, 539, 605, 1648, 598, 544, 600, 540, 607, 534, 596, 1657, 600, 541, 602, 1652, 605, 1649, 597, 545, 599, 1654, 603, 1651, 605, 1649, 607
button4=9124, 4511, 600, 541, 603, 538, 606, 535, 598, 569, 575, 565, 579, 535, 598, 543, 601, 566, 578, 1648, 598, 1656, 601, 1653, 603, 1651, 606, 1648, 598, 1656, 601, 540, 604, 1650, 607, 534, 599, 542, 602, 1651, 605, 537, 597, 1656, 600, 541, 603, 538, 606, 562, 571, 1655, 602, 1652, 605, 536, 598, 1656, 600, 541, 603, 1651, 606, 1648, 598, 1656, 601
button5=9136, 4511, 601, 540, 603, 539, 605, 563, 571, 543, 601, 567, 577, 565, 579, 536, 598, 543, 601, 1653, 604, 1650, 607, 1648, 598, 1657, 600, 1655, 602, 1653, 604, 538, 606, 1648, 598, 1657, 601, 569, 575, 1652, 604, 538, 606, 1648, 609, 560, 573, 542, 602, 539, 605, 536, 608, 1647, 599, 542, 602, 1654, 602, 539, 605, 1650, 607, 1648, 598, 1658, 599
button6=9119, 4519, 603, 537, 606, 535, 599, 541, 603, 537, 606, 535, 599, 541, 603, 538, 606, 534, 599, 1655, 602, 1652, 604, 1650, 597, 1658, 598, 1656, 601, 1653, 603, 538, 606, 1648, 598, 542, 602, 1653, 604, 1650, 596, 544, 600, 1655, 602, 538, 606, 535, 598, 542, 602, 1652, 604, 537, 596, 544, 600, 1654, 603, 537, 597, 1657, 599, 1655, 602, 1652, 604
buttonSave=9217, 4493, 633, 514, 631, 515, 630, 516, 629, 517, 639, 507, 646, 500, 636, 510, 635, 511, 635, 1625, 634, 1626, 633, 1626, 633, 1627, 632, 1628, 631, 1628, 610, 536, 629, 1630, 608, 1652, 607, 539, 606, 539, 606, 1654, 605, 541, 604, 541, 604, 542, 603, 543, 602, 544, 601, 1659, 600, 1659, 610, 536, 609, 1651, 608, 1652, 607, 1652, 606, 1656, 603

print('IR listener test')
#Fuzzy pulse comparison function:
def fuzzy_pulse_compare(pulse1, pulse2, fuzzyness=0.2):
    if len(pulse1) != len(pulse2):
        return False
    for i in range(len(pulse1)):
        threshold = int(pulse1[i] * fuzzyness)
        if abs(pulse1[i] - pulse2[i]) > threshold:
            return False
    return True

#Create pulse input and IR decoder.
pulses = pulseio.PulseIn(IRPin, maxlen=200, idle_state=True)
decoder = adafruit_irremote.GenericDecode()
pulses.clear()
pulses.resume()
#Loop waiting to receive pulses.

while True:
    # Wait for a pulse to be detected.
    detected = decoder.read_pulses(pulses)
    print('got a pulse...')
    print(detected)
    if fuzzy_pulse_compare(button1, detected):#Door close
        print('Button 1!')
        doorMotor.value = not doorMotor.value
        last=1
    if fuzzy_pulse_compare(button2, detected):#Light on
        print('Button 2!')
        lightOnMotor.value = True
        time.sleep(1.5)
        lightOnMotor.value = False
        last=2
    if fuzzy_pulse_compare(button3, detected):#Fan on
        print('Button 3!')
        fanMotor.value = True
        time.sleep(1.5)
        fanMotor.value = False
        last=3
    if fuzzy_pulse_compare(button4, detected):
        print('Button 4!')
    if fuzzy_pulse_compare(button5, detected):#Light off
        print('Button 5!')
        lightOffMotor.value = True
        time.sleep(1.5)
        lightOffMotor.value = False
        last=5
    if fuzzy_pulse_compare(button6, detected):
        print('Button 6!')
    if fuzzy_pulse_compare(buttonSave, detected):
        if(last==1):
            print('Button 1!')
            doorMotor.value = not doorMotor.value
        if(last==2):
            print('Button 2!')
            lightOnMotor.value = True
            time.sleep(0.4)
            lightOnMotor.value = False
            last=2
        if(last==3):
            print('Button 3!')
            fanMotor.value = True
            time.sleep(0.4)
            fanMotor.value = False
            last=3
        if(last==5):
            print('Button 5!')
            lightOffMotor.value = True
            time.sleep(0.4)
            lightOffMotor.value = False
            last=5
        print('Button Save')
