"""Entry point."""
import os
import string
import secrets
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


load_dotenv(dotenv_path=".env")

GROUPS = int(os.getenv("GROUPS"))
TEAMS = int(os.getenv("TEAMS"))
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

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


def generate_pwd(length: int):
    """Generate password of length."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def save_to_file(lines, filepath):
    """Save list of text into filepath."""
    with open(filepath, mode="wt", encoding="utf-8") as f:
        f.write("\n".join(str(line) for line in lines))
        f.write("\n")


def create_db_and_user(group: int, team: int):
    dbname = f"db{group}eq{team}"
    usrrole = f"role{group}eq{team}"
    usrname = f"user{group}eq{team}"
    usrpwd = generate_pwd(10)

    cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
    cursor.execute(f"DROP USER IF EXISTS {usrname}")
    cursor.execute(f"DROP ROLE IF EXISTS {usrrole}")

    cursor.execute(f"CREATE DATABASE {dbname}")
    cursor.execute(f"CREATE ROLE {usrrole}")
    cursor.execute(f"REVOKE CONNECT ON DATABASE {dbname} FROM PUBLIC")
    cursor.execute(f"GRANT CONNECT ON DATABASE {dbname} TO {usrrole}")
    cursor.execute(f"CREATE USER {usrname} WITH PASSWORD '{usrpwd}'")
    cursor.execute(f"GRANT {usrrole} TO {usrname}")
    return f"{usrname}  {usrpwd}    {dbname}"


if __name__ == "__main__":
    # remove connect privileges from existing databases
    for db in ["demo", "postgres"]:
        cursor.execute(f"REVOKE CONNECT ON DATABASE {db} FROM PUBLIC")

    # create user accounts and associated databases
    credentials = []
    for i in range(1, GROUPS + 1):
        for j in range(1, TEAMS + 1):
            credentials.append(create_db_and_user(i, j))

    save_to_file(credentials, OUTPUT_FILE)