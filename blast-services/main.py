import pika
import json
from utils import BlastService
from dotenv import load_dotenv
import os

load_dotenv()
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue="blast_service")


def on_request(ch, method, props, body):  # callback function
    blast_service = BlastService()
    response = blast_service.process_request(body)

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="blast_service", on_message_callback=on_request)
print(" [x] Awaiting RPC requests")
channel.start_consuming()
