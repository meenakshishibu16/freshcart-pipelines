"""Checks the console logs of one dispatcher run against the routing rules (D2 / D3 proof).

Usage:  python stream/verify_logs.py LOG_DIR
LOG_DIR holds dispatcher.log and one <DriverName>.log per driver.
For every message the dispatcher sent it works out WHO SHOULD receive it (topic_match.receivers)
and compares that with who actually printed it.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_match import DRIVERS, receivers  # noqa: E402

SENT = re.compile(r"\[dispatcher\] #(\d+) key=(\S+)\s+id=(\w+)(\s+<-- BAD)?")
GOT = re.compile(r"\] got key=(\S+)\s+id=(\w+)")
REJ = re.compile(r"\] REJECTED \(no zone\) key=(\S+) body=.*?\"id\": \"(\w+)\"")


def verify(log_dir):
    log_dir = Path(log_dir)
    sent = {}                                           # id -> (key, is_bad)
    for line in (log_dir / "dispatcher.log").read_text().splitlines():
        m = SENT.search(line)
        if m:
            sent[m.group(3)] = (m.group(2), bool(m.group(4)))

    got, rejected = defaultdict(set), defaultdict(set)  # id -> {driver names}
    for name in DRIVERS:
        f = log_dir / f"{name}.log"
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            m = GOT.search(line)
            if m:
                got[m.group(2)].add(name)
            m = REJ.search(line)
            if m:
                rejected[m.group(2)].add(name)

    problems, per_key = [], defaultdict(lambda: [0, set()])
    for mid, (key, bad) in sent.items():
        expected = set(receivers(key)) - {"dropped"}
        actual = got[mid] | rejected[mid]
        per_key[key][0] += 1
        per_key[key][1] = expected
        if actual != expected:
            problems.append(f"{mid} key={key}: expected {sorted(expected)} but got {sorted(actual)}")
        if bad and got[mid]:
            problems.append(f"{mid} is BAD but was processed by {sorted(got[mid])}")
        if not bad and rejected[mid]:
            problems.append(f"{mid} is good but was rejected by {sorted(rejected[mid])}")

    bad_ids = [i for i, (_, b) in sent.items() if b]
    print(f"messages sent: {len(sent)}   bad messages: {len(bad_ids)}")
    print(f"{'routing key':32s} {'sent':>4s}  receivers (expected = actual)")
    for key in sorted(per_key):
        n, exp = per_key[key]
        print(f"{key:32s} {n:4d}  {', '.join(sorted(exp)) or 'dropped'}")
    reached = [i for i in bad_ids if receivers(sent[i][0]) != ["dropped"]]
    print("bad messages that reached a driver and were rejected (nack, requeue=False):",
          sum(1 for i in reached if rejected[i]), "of", len(reached),
          f"({len(bad_ids) - len(reached)} bad ones had no matching queue and were dropped by the exchange)")
    print("RESULT:", "OK - every message reached exactly the predicted queues" if not problems
          else f"{len(problems)} PROBLEM(S)")
    for p in problems:
        print("  -", p)
    return not problems


if __name__ == "__main__":
    sys.exit(0 if verify(sys.argv[1]) else 1)
