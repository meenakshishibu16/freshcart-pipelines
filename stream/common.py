"""Shared settings for the dispatcher and the drivers."""
import os

EXCHANGE = "rapido-dispatch"

# The broker URL is read from the environment so it never ends up in Git.
#   local broker (Colab / laptop):  amqp://guest:guest@localhost:5672/%2F   (default)
#   CloudAMQP:                      export RABBITMQ_URL="amqps://user:pass@host/vhost"
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
