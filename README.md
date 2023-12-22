# postgresql-db-generator

Generate multiple PostgreSQL databases and users with restricted privileges

## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/)

## Usage

Install dependencies

```sh
poetry install
```

Define .env variables

```sh
cp .env.example .env
```

For testing purpose, run local docker image. Omit this step as you need.

```sh
./scripts/start.sh
```

Run script 🚀

```sh
poetry run python src/main.py
```

By default, generated credentials are available in `credentials.csv` file.
