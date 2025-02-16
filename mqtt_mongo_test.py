from pymongo import MongoClient
import paho.mqtt.client as mqtt
import json
import os

mongo_uri = os.environ.get('MONGO_URI')
mongo_client = MongoClient(mongo_uri)
database = mongo_client['Messages']
mdb_collection = database['Tasks']

mqtt_broker = "broker.hivemq.com"
mqtt_listen_topic = "TaskLight/RemoteUpdateCall"
mqtt_publish_topic = "TaskLight/RemoteUpdateResponse"
mqtt_client = mqtt.Client()
mqtt_port = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_listen_topic)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if msg.payload.decode() == "GetTasks":
        tasks = mdb_collection.find({})
        task_list = list(tasks)

        for i in range(0, len(task_list)):
            task_list[i].pop('_id')

        client.publish(mqtt_publish_topic, json.dumps(task_list))

def main():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("Exiting")
        mqtt_client.disconnect()
        mongo_client.close()

if __name__ == "__main__":  
    main()