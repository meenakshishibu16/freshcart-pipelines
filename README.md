# freshcart-pipelines

Data Engineering assignment **From Git to Gold**: version control + CI, an ELT pipeline on Snowflake, an ML pipeline in Mage, and an event stream on RabbitMQ.

![CI](https://github.com/meenakshishibu16/freshcart-pipelines/actions/workflows/ci.yml/badge.svg)

## Layout

| Folder | What is in it | Part |
|---|---|---|
| `elt/` | `freshcart_elt.ipynb`: raw files → bronze → silver / quarantine → gold on Snowflake, plus the B2–B5 changes and the bonus stream consumer | B, Bonus |
| `iris_project/` | Mage project: `load_iris → validate_iris → prepare_data → train_model → (save_results, evaluate_model)`, each block with a `@test`; `iris_mage_colab.ipynb` runs it | C |
| `stream/` | `dispatcher.py`, `driver.py` (RabbitMQ topic exchange `rapido-dispatch`), `verify_logs.py`, `stream_colab.ipynb` | D |
| `tests/` | pytest tests run by CI | A3, C4 |
| `.github/workflows/ci.yml` | on every push: checkout, Python 3.12, `pip install -r requirements.txt`, `pytest` | A3 |

## Run it

```bash
pip install -r requirements.txt
pytest                                   # the same thing CI runs
```

* **Mage (Part C)**: open `iris_project/iris_mage_colab.ipynb` in Colab. Locally: `pip install -r requirements-extra.txt` (Python 3.12) then
  `mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 3}'`.
* **ELT (Part B)**: open `elt/freshcart_elt.ipynb` in Colab; it asks for your Snowflake account, user and password.
* **Stream (Part D)**: open `stream/stream_colab.ipynb` in Colab (installs a local RabbitMQ), or set `RABBITMQ_URL` for a hosted broker.

## Secrets

Nothing secret is stored here. Snowflake credentials are typed into the notebook at run time, and the RabbitMQ URL is read from the `RABBITMQ_URL` environment variable. `.env`, `*.pkl`, `*.csv`, `mage.log` and `__pycache__/` are in `.gitignore`.
