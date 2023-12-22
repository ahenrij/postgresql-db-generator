"""Entry point."""
import os
import csv
import string
import secrets
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


load_dotenv(dotenv_path=".env")

GROUPS = int(os.getenv("GROUPS"))
TEAMS = int(os.getenv("TEAMS"))
OUTPUT_FILE = os.getenv("OUTPUT_FILE")


def generate_pwd(length: int):
    """Generate password of length."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def save_to_file(data: list[dict], filepath: str):
    """Save list of dict into csv filepath."""
    headers = data[0].keys()
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, headers)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def create_db_and_user(group: int, team: int, cursor):
    dbname = f"db0{group}eq{team}"
    usrrole = f"role0{group}eq{team}"
    usrname = f"user0{group}eq{team}"
    usrpwd = generate_pwd(16)

    # remove any previous execution data
    cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
    cursor.execute(f"DROP USER IF EXISTS {usrname}")
    cursor.execute(f"DROP ROLE IF EXISTS {usrrole}")

    # create database and associate user
    cursor.execute(f"CREATE DATABASE {dbname}")
    cursor.execute(f"CREATE ROLE {usrrole}")
    cursor.execute(f"REVOKE CONNECT ON DATABASE {dbname} FROM PUBLIC")
    cursor.execute(f"GRANT CONNECT ON DATABASE {dbname} TO {usrrole}")
    cursor.execute(f"CREATE USER {usrname} WITH PASSWORD '{usrpwd}'")
    cursor.execute(f"GRANT {usrrole} TO {usrname}")

    return {"username": usrname, "password": usrpwd, "database": dbname}


if __name__ == "__main__":
    try:
        ## create db connection
        db = psycopg2.connect(
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT"),
        )
        db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # init db cursor
        cursor = db.cursor()

        # remove connect privileges from existing databases
        for dbname in ["demo", "postgres"]:
            cursor.execute(f"REVOKE CONNECT ON DATABASE {dbname} FROM PUBLIC")

        # create user accounts and associated databases
        credentials = []
        for i in range(1, GROUPS + 1):
            for j in range(1, TEAMS + 1):
                credentials.append(create_db_and_user(i, j, cursor))

        save_to_file(credentials, OUTPUT_FILE)
        print("Credentials created successfully in PostgreSQL")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if db:
            cursor.close()
            db.close()
            print("PostgreSQL connection is closed")
