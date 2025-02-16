from machine import Pin
from utime import sleep
import network

RS = Pin(16, Pin.OUT)
En = Pin(17, Pin.OUT)
D0 = Pin(15, Pin.OUT)
D1 = Pin(14, Pin.OUT)
D2 = Pin(13, Pin.OUT)
D3 = Pin(12, Pin.OUT)
D4 = Pin(11, Pin.OUT)
D5 = Pin(10, Pin.OUT)
D6 = Pin(9, Pin.OUT)
D7 = Pin(8, Pin.OUT)

category_sw = Pin(18, Pin.IN, Pin.PULL_DOWN)
left_sw = Pin(19, Pin.IN, Pin.PULL_DOWN)
center_sw = Pin(20, Pin.IN, Pin.PULL_DOWN)
right_sw = Pin(21, Pin.IN, Pin.PULL_DOWN)

current_pos = 0
    
def pulse_en(delay=1e-3):
    sleep(delay)
    En.value(1)
    sleep(delay)
    En.value(0)
    sleep(delay)

def write_lcd_data(cmd, rs_value):
    RS.value(rs_value) #Set command vs character mode (0 for command, 1 for character)
    
    sleep(1e-3)
    
    D0.value((cmd >> 0) & 1) # Write to D0, and so on
    D1.value((cmd >> 1) & 1)
    D2.value((cmd >> 2) & 1)
    D3.value((cmd >> 3) & 1)
    D4.value((cmd >> 4) & 1)
    D5.value((cmd >> 5) & 1)
    D6.value((cmd >> 6) & 1)
    D7.value((cmd >> 7) & 1)
    
    pulse_en(delay=3e-3)

def init_8bitmode():
    global current_pos
    current_pos = 0
    
    #Initialize LCD to 8 bit mode
    write_lcd_data(int("00110000",2), 0)
    write_lcd_data(int("00110000",2), 0)
    write_lcd_data(int("00110000",2), 0)
    
    #Function set command
    #Format: 001abc--, where:
    #a is 1 for 8 bit mode, 0 for 4 bit mode
    #b is 1 for two line display, 0 for one line display
    #c is 1 for 5x10 dots, 0 for 5x8 dots
    write_lcd_data(int("00111000",2),0)
    
    #Display control command
    #Format: 00001abc
    #a is display on/off
    #b is cursor display on/off
    #c is cursor blink on/off
    write_lcd_data(int("00001111",2),0)
    
    #Clear Display
    #Clear characters and reset position to 0
    write_lcd_data(int("00000001",2),0)
    
def printmsg(msg):
    global current_pos
    
    for c in msg:
        write_lcd_data(ord(c), 1)
        current_pos += 1
        if current_pos == 16:
            goto_position(41)
        
def goto_position(pos):
    global current_pos
    
    write_lcd_data(pos + 127, 0)
    current_pos = pos

def goto_character(row, col):
    if row == 1:
        goto_position(col)
    elif row == 2:
        goto_position(col + 40)
    else:
        raise ValueError("Invalid row number")



def main():
    init_8bitmode()

    goto_character(2, 2)
    printmsg("Hello, World!")
    

if __name__ == "__main__":
    main()