import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client()
mqtt_port = 1883
mqtt_broker = "broker.hivemq.com"
mqtt_listen_topic = "TaskLight/RemoteUpdateResponse"
mqtt_publish_topic = "TaskLight/RemoteUpdateCall"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_listen_topic)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    
def main():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.publish(mqtt_publish_topic, "GetTasks")
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("Exiting")
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()
