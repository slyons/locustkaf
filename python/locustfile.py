import os, signal, json, time
from locust import web, Locust, TaskSet, task, events
from faker import Faker
from datetime import datetime
from confluent_kafka import Producer

from locustfile_conf import *

def generate_data(fake):
    data = {
        "username": fake.user_name(),
        "ip": fake.ipv4_public(),
        "uri": fake.uri(),
        "user_agent": fake.user_agent(),
        "method": fake.random_element(elements=["POST", "GET", "HEAD", "PUT"]),
        "status_code": fake.random_element(elements=[200,201, 202, 301, 303, 400, 401, 403, 404, 500]),
        "ts": datetime.now().isoformat()
    }
    return data

producer_config = {"bootstrap.servers": BROKER_HOST}
if len(KAFKA_USERNAME):
    producer_config.update({
        'sasl.mechanisms': 'PLAIN',
        'security.protocol': 'SASL_SSL',
        "sasl.username": KAFKA_USERNAME,
        "sasl.password": KAFKA_PASSWORD
    })

producer = Producer(producer_config)
faker = Faker()
single_message = generate_data()

class KafkaTaskSet(TaskSet):
    min_wait = MIN_WAIT
    max_wait = MAX_WAIT

    @task
    def send_message(self):
        for i in range(MSGS_PER_BATCH):
            start_time = time.time()
            try:
                data = single_message
                if KEY_FIELD_NAME:
                    producer.produce(KAFKA_TOPIC, json.dumps(data), data[KEY_FIELD_NAME])
                else:
                    producer.produce(KAFKA_TOPIC, json.dumps(data))
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                events.request_failure.fire(request_type="kafka", name=KAFKA_TOPIC, response_time=total_time, exception=e)
            else:
                total_time = int((time.time() - start_time) * 1000)
                events.request_success.fire(request_type="kafka", name=KAFKA_TOPIC, response_time=total_time, response_length=0)

class KafkaLocust(Locust):
    task_set = KafkaTaskSet
    host = BROKER_HOST
