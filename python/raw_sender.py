import os, signal, json, time, logging, secrets
from faker import Faker
from datetime import datetime
from confluent_kafka import Producer
from metrology import Metrology
from metrology.reporter import LoggerReporter
from producer_conf import *

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

meter = Metrology.meter("messages")
successful = Metrology.counter("success")
errors = Metrology.counter("errors")
logging.basicConfig(level=logging.DEBUG)
reporter = LoggerReporter(level=logging.INFO, interval=10)


def delivery_report(err, msg):
    if err is not None:
        errors.increment()
    else:
        successful.increment()
    meter.mark()

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

utimer = Metrology.utilization_timer("overall")
messages = (secrets.token_bytes(1024) for x in range(100000))
reporter.start()
logging.info("Producer started")
with utimer:
    for m in messages:
        producer.poll(0)
        producer.produce("eventstream4", m, callback=delivery_report)

    producer.flush()