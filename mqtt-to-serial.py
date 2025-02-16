import time
import serial
import pymongo

ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
database = mongo_client['Messages']
collection = database['Tasks']

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print(line)
        if line == "get_list":
            tasks = collection.find({})
            task_list = list(tasks)
            for i in range(0, len(task_list)):
                task_list[i].pop('_id')
            ser.write(str(task_list).encode())
            print(task_list)
    time.sleep(1)