"""Publishes a food/ride request every 2 seconds to the topic exchange 'rapido-dispatch'.

Routing key = city.zone.type      e.g.  bangalore.koramangala.food

Usage:
    python stream/dispatcher.py                  # D3: every 10th message is bad (no 'zone' field)
    python stream/dispatcher.py --bad-every 0    # D2: only good messages
    python stream/dispatcher.py --count 60       # stop after 60 messages (about 2 minutes)
"""
import argparse
import json
import random
import time
import uuid
from datetime import datetime, timezone

import pika

from common import EXCHANGE, RABBITMQ_URL

ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai":   ["tnagar", "whitefield", "adyar"],
}
TYPES = ["ride", "food"]


def build_message(bad: bool = False):
    """Return (routing_key, body_dict). A 'bad' message has no 'zone' field."""
    city = random.choice(list(ZONES))
    zone = random.choice(ZONES[city])
    kind = random.choice(TYPES)
    body = {
        "id": str(uuid.uuid4())[:8],
        "city": city,
        "zone": zone,
        "type": kind,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if bad:
        del body["zone"]                   # D3: the driver must reject this one
    return f"{city}.{zone}.{kind}", body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=2.0, help="seconds between messages")
    ap.add_argument("--bad-every", type=int, default=10, help="every Nth message is bad (0 = never)")
    ap.add_argument("--count", type=int, default=0, help="stop after N messages (0 = run forever)")
    args = ap.parse_args()

    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    n = 0
    try:
        while args.count == 0 or n < args.count:
            n += 1
            bad = args.bad_every > 0 and n % args.bad_every == 0
            key, body = build_message(bad)
            ch.basic_publish(exchange=EXCHANGE, routing_key=key,
                             body=json.dumps(body),
                             properties=pika.BasicProperties(content_type="application/json"))
            print(f"[dispatcher] #{n:03d} key={key:32s} id={body['id']}{'  <-- BAD (no zone)' if bad else ''}",
                  flush=True)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()


if __name__ == "__main__":
    main()
