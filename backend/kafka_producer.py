import os
import json
from confluent_kafka import Producer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        producer = Producer({
            'bootstrap.servers': KAFKA_BROKER,
            'client.id': 'fastapi-producer'
        })
    return producer

def produce_message(topic: str, key: str, value: dict):
    prod = get_kafka_producer()
    prod.produce(topic, key=key.encode('utf-8'), value=json.dumps(value).encode('utf-8'))
    prod.flush()
