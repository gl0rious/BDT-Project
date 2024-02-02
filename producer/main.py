from confluent_kafka import Producer
import socket
import time
import random
import json
import time

conf = {'bootstrap.servers': 'kafka:9092',
        'client.id': socket.gethostname()}

producer = Producer(conf)

for i in range(10000):
    id = random.randint(1, 50)
    product = {
        'id': id,
        'name':'product ' + str(id),
        'quantity': random.randint(1, 10),
        'timestamp': int(time.time() * 1000)
    }
    producer.produce("products-sold", value=json.dumps(product))
    producer.flush()
    print(json.dumps(product))
    time.sleep(0.01)