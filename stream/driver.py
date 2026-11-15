"""A driver listens for requests whose routing key matches its binding pattern.

Usage:
    python stream/driver.py Ravi "bangalore.koramangala.*"
    python stream/driver.py Control "bangalore.#"

Each driver gets its own PRIVATE queue (server-named, exclusive, deleted when the driver stops),
bound to the exchange with the given pattern.
  *  matches exactly one word      #  matches zero or more words

D2: print each request and send an ACK.
D3: a message with no 'zone' field is rejected with basic_nack(requeue=False); every other
    message is acknowledged with basic_ack.
"""
import json
import sys

import pika

from common import EXCHANGE, RABBITMQ_URL


def handle_message(ch, method, body, name):
    """Process one delivery. Returns 'ack' or 'nack' (also performs it on the channel)."""
    try:
        msg = json.loads(body)
    except (ValueError, TypeError):
        msg = {}
    if not msg.get("zone"):                                   # bad message: zone is missing
        print(f"[{name}] REJECTED (no zone) key={method.routing_key} body={body.decode()}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)   # discard, do NOT retry
        return "nack"
    print(f"[{name}] got key={method.routing_key:30s} id={msg['id']} {msg['type']} in {msg['zone']}",
          flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)            # tell the broker: done, forget it
    return "ack"


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: python stream/driver.py NAME "PATTERN"')
    name, pattern = sys.argv[1], sys.argv[2]

    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    queue = ch.queue_declare(queue="", exclusive=True).method.queue      # private queue
    ch.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=pattern)
    ch.basic_qos(prefetch_count=1)

    def on_message(channel, method, properties, body):
        handle_message(channel, method, body, name)

    ch.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=False)
    print(f"[{name}] waiting on queue {queue} with pattern '{pattern}'  (Ctrl+C to stop)", flush=True)
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()


if __name__ == "__main__":
    main()
