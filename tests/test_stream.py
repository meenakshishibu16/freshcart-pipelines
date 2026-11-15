import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "stream"))

from topic_match import matches, receivers          # noqa: E402
import dispatcher                                     # noqa: E402
import driver                                         # noqa: E402


def test_d1_routing_table():
    assert receivers("bangalore.koramangala.food") == ["Ravi", "Meena", "Control"]
    assert receivers("bangalore.indiranagar.ride") == ["Priya", "Arjun", "Control"]
    assert receivers("bangalore.whitefield.ride") == ["Arjun", "Control"]
    assert receivers("chennai.tnagar.food") == ["Karthik"]
    assert receivers("chennai.whitefield.ride") == ["dropped"]
    assert receivers("bangalore.koramangala") == ["Control"]      # only '#' can match two words


def test_star_needs_exactly_one_word_and_hash_allows_zero():
    assert not matches("bangalore.koramangala.*", "bangalore.koramangala")
    assert matches("bangalore.#", "bangalore")                     # zero words after the dot-less prefix


def test_dispatcher_message_shape():
    key, body = dispatcher.build_message()
    assert set(body) == {"id", "city", "zone", "type", "ts"}
    assert key == f"{body['city']}.{body['zone']}.{body['type']}"


def test_bad_message_has_no_zone():
    _, body = dispatcher.build_message(bad=True)
    assert "zone" not in body


class FakeChannel:
    def __init__(self):
        self.calls = []

    def basic_ack(self, delivery_tag):
        self.calls.append(("ack", delivery_tag))

    def basic_nack(self, delivery_tag, requeue):
        self.calls.append(("nack", delivery_tag, requeue))


def test_driver_acks_good_and_nacks_bad_without_requeue():
    ch = FakeChannel()
    m = SimpleNamespace(delivery_tag=1, routing_key="bangalore.koramangala.food")
    good = json.dumps({"id": "a", "city": "bangalore", "zone": "koramangala", "type": "food", "ts": "x"}).encode()
    bad = json.dumps({"id": "b", "city": "bangalore", "type": "food", "ts": "x"}).encode()
    assert driver.handle_message(ch, m, good, "Ravi") == "ack"
    m.delivery_tag = 2
    assert driver.handle_message(ch, m, bad, "Ravi") == "nack"
    assert ch.calls == [("ack", 1), ("nack", 2, False)]
