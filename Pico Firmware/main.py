from machine import Pin, UART
import utime
# import umqtt.simple import MQTTClient # type: ignore
#import network
import os
import json

#wlan = network.WLAN(network.STA_IF)
#wlan.active(True)
#ssid = "AccessOU"
#password = ""
uart = UART(0, 115200)

#mqtt_server = ""
#mqtt_port = 1883
#mqtt_client = MQTTClient(b"LightTask", mqtt_server, port=0) # type: ignore

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

check_char = [int('10001', 2), int('01010', 2), int('01010', 2), int('00100', 2), int('00100', 2), int('01010', 2), int('01010', 2), int('10001', 2)]
uncheck_char = [int('11111', 2), int('10001', 2), int('10001', 2), int('10001', 2), int('10001', 2), int('10001', 2), int('10001', 2), int('11111', 2)]

current_pos = 0

irq_flag = 0
cat_flag = 0
left_flag = 0
center_flag = 0
right_flag = 0

current_category = 0 # 0 for todo, 1 for notif
todo_list = [{"title": "Task 1", "completed": False}, {"title": "Task 2", "completed": False}, {"title": "Really Really Long Task 3", "completed": False}]
notif_list = []
    
def pulse_en(delay=1e-3):
    utime.sleep(delay)
    En.value(1)
    utime.sleep(delay)
    En.value(0)
    utime.sleep(delay)

def write_lcd_data(cmd, rs_value):
    RS.value(rs_value) #Set command vs character mode (0 for command, 1 for character)
    
    utime.sleep(1e-3)
    
    D0.value((cmd >> 0) & 1) # Write to D0, and so on
    D1.value((cmd >> 1) & 1)
    D2.value((cmd >> 2) & 1)
    D3.value((cmd >> 3) & 1)
    D4.value((cmd >> 4) & 1)
    D5.value((cmd >> 5) & 1)
    D6.value((cmd >> 6) & 1)
    D7.value((cmd >> 7) & 1)
    
    pulse_en(delay=2e-3)

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
    write_lcd_data(int("00001100",2),0)
    
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
    
    write_lcd_data(int('00000010',2), 0)
    for i in range(0, pos):
        write_lcd_data(int('00010100',2), 0)
    current_pos = pos

def row_col_to_pos(row, col):
    return (row * 40) + col

def init_lcd():
    init_8bitmode()
    define_custom_char(check_char, 0)
    define_custom_char(uncheck_char, 1)

def scroll_message(msg, msg_length, delay=0.1, start_pos=(0, 0), spacing=1):
    global irq_flag

    row, col = start_pos
    msg += " " * spacing
    msg = list(msg)
    goto_position(row_col_to_pos(row, col))
    for i in range(0, len(msg) + 1):
        if irq_flag == 1:
            irq_flag = 0
            break
        printmsg(msg[0:msg_length])
        msg.append(msg.pop(0))
        goto_position(row_col_to_pos(row, col))
        utime.sleep(delay)

def define_custom_char(data, char_num):
    for i in range(0, 8):
        write_lcd_data(int("01000000",2) + (char_num << 3) + i, 0)
        write_lcd_data(data[i], 1)
    write_lcd_data(1, 0) #Reset cursor to 0 position

def get_next_todo_list_value(r_l):
    global todo_list
    if r_l == 0:
        todo_list.append(todo_list.pop(0))
        return todo_list[0]
    else:
        todo_list.insert(0, todo_list.pop())
        return todo_list[0]
    
def cat_irq_handler(pin):
    global irq_flag
    global cat_flag
    irq_flag = 1
    cat_flag = 1
    print('test')

def left_irq_handler(pin):
    global irq_flag
    global left_flag
    irq_flag = 1
    left_flag = 1
    print('test')

def center_irq_handler(pin):    
    global irq_flag
    global center_flag
    irq_flag = 1
    center_flag = 1

def right_irq_handler(pin):
    global irq_flag
    global right_flag
    irq_flag = 1
    right_flag = 1
    print('test2')

def init_interrupts():
    category_sw.irq(trigger=Pin.IRQ_RISING, handler=cat_irq_handler)
    left_sw.irq(trigger=Pin.IRQ_RISING, handler=left_irq_handler)
    center_sw.irq(trigger=Pin.IRQ_RISING, handler=center_irq_handler)
    right_sw.irq(trigger=Pin.IRQ_RISING, handler=right_irq_handler)

def update_lists():
    pass

def redraw_lcd():
    write_lcd_data(1, 0)
    if current_category == 0:
        goto_position(row_col_to_pos(0, 0))
        printmsg("TO-DO:")
    else:
        goto_position(row_col_to_pos(0, 0))
        printmsg("NOTIF:")

def initital_lcd_state():
    goto_position(row_col_to_pos(1, 0))
    item = todo_list[0]
    if item["completed"]:
        write_lcd_data(0, 1)
    else:
        write_lcd_data(1, 1)
    goto_position(row_col_to_pos(1, 1))
    printmsg(item["title"])

# def update_list_from_pi():
#     global todo_list

#     uart.write("get_list".encode('utf-8'))
#     while uart.any() == 0:
#         pass
#     data = uart.read()
#     data = list(eval(data.decode('utf-8')))
#     print(data)
#     todo_list = []
#     for i in range(0, len(data)):
#         todo_list.append(json.loads(data[i]))

# def init_network():
#     goto_position(row_col_to_pos(0, 0))
#     printmsg("Connecting to")
#     goto_position(row_col_to_pos(1, 0))
#     printmsg("Wi-Fi...")
#     utime.sleep(0.5)
#     wlan.connect(ssid, password)
#     while not wlan.isconnected():
#         utime.sleep(1)
#     goto_position(row_col_to_pos(0, 0))
#     printmsg("Connected")

def main():
    init_interrupts()
    init_lcd()
    #init_network()
    redraw_lcd()
    initital_lcd_state()

    while(1):
        global cat_flag
        global left_flag
        global center_flag
        global right_flag

        current_item = todo_list[0]

        if cat_flag == 1:
            # utime.sleep(0.1)
            # cat_flag = 0
            # update_list_from_pi()
            # utime.sleep(0.5)
            pass
        elif left_flag == 1:
            redraw_lcd()
            left_flag = 0
            item = get_next_todo_list_value(1)
            goto_position(row_col_to_pos(1, 0))
            if item["completed"]:
                write_lcd_data(0, 1)
            else:
                write_lcd_data(1, 1)
            goto_position(row_col_to_pos(1, 1))
            printmsg(item["title"])
        elif center_flag == 1:
            if current_category == 0:
                current_item['completed'] = not current_item['completed']
                goto_position(row_col_to_pos(1, 0))
                if current_item['completed']:
                    write_lcd_data(0, 1)
                else:
                    write_lcd_data(1, 1)
            center_flag = 0
        elif right_flag == 1:
            redraw_lcd()
            right_flag = 0
            item = get_next_todo_list_value(0)
            goto_position(row_col_to_pos(1, 0))
            if item["completed"]:
                write_lcd_data(0, 1)
            else:
                write_lcd_data(1, 1)
            goto_position(row_col_to_pos(1, 1))
            printmsg(item["title"])
        else:
            if len(current_item["title"]) > 15:
                scroll_message(current_item["title"], 15, 0.3, (1, 1), spacing = 3)
            for i in range(0, 15):
                if irq_flag == 1:
                    break
                utime.sleep(0.1)

if __name__ == "__main__":
    main()