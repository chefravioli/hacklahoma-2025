import network
import time

ssid = "AccessOU"
password = ""

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

for _ in range(10):
    if wlan.isconnected():
        break
    print("Connecting...")
    time.sleep(1)

if wlan.isconnected():
    print("Connected, IP address:", wlan.ifconfig()[0])
else:
    print("Failed to connect")
