"""Pure-Python copy of RabbitMQ's topic matching rule, used for the D1 table and the tests.

Words are separated by dots.
  *  matches exactly one word
  #  matches zero or more words
"""


def matches(pattern: str, key: str) -> bool:
    return _match(pattern.split("."), key.split("."))


def _match(p, k):
    if not p:
        return not k                      # pattern used up: key must be used up too
    head, rest = p[0], p[1:]
    if head == "#":
        # '#' can swallow 0, 1, 2 ... words
        return any(_match(rest, k[i:]) for i in range(len(k) + 1))
    if not k:
        return False                      # key used up but pattern still needs a word
    if head == "*" or head == k[0]:
        return _match(rest, k[1:])
    return False


DRIVERS = {
    "Ravi":     "bangalore.koramangala.*",
    "Priya":    "bangalore.indiranagar.*",
    "Arjun":    "bangalore.*.ride",
    "Meena":    "bangalore.*.food",
    "Karthik":  "chennai.tnagar.food",
    "Control":  "bangalore.#",
}


def receivers(key: str):
    return [name for name, pat in DRIVERS.items() if matches(pat, key)] or ["dropped"]


if __name__ == "__main__":
    for i, key in enumerate([
        "bangalore.koramangala.food",
        "bangalore.indiranagar.ride",
        "bangalore.whitefield.ride",
        "chennai.tnagar.food",
        "chennai.whitefield.ride",
        "bangalore.koramangala",
    ], 1):
        print(i, key, "->", ", ".join(receivers(key)))
