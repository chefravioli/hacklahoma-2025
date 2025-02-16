from machine import Pin
from utime import sleep
import network
from liquid_crystal_pico import LiquidCrystalPico

RS = Pin(16, Pin.OUT)
En = Pin(17, Pin.OUT)
D4 = Pin(11, Pin.OUT)
D5 = Pin(10, Pin.OUT)
D6 = Pin(9, Pin.OUT)
D7 = Pin(8, Pin.OUT)

category_sw = Pin(18, Pin.IN, Pin.PULL_DOWN)
left_sw = Pin(19, Pin.IN, Pin.PULL_DOWN)
center_sw = Pin(20, Pin.IN, Pin.PULL_DOWN)
right_sw = Pin(21, Pin.IN, Pin.PULL_DOWN)

lcd = LiquidCrystalPico(RS, En, D4, D5, D6, D7)
lcd.move_to(0, 3)
lcd.write("Hello!")