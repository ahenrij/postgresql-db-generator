"""Entry point."""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

GROUPS = os.getenv('GROUPS')
TEAMS = os.getenv('TEAMS')

con = psycopg2.connect(
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('DATABASE_HOST'),
    port=os.getenv('DATABASE_PORT'),
)

cursor_obj = con.cursor()


def create_db_and_user(group: int, team: int):
    cursor_obj.execute("CREATE DATABASE :dbname")
    cursor_obj.execute("CREATE ROLE :new_role")
    cursor_obj.execute("GRANT CONNECT ON DATABASE :dbname TO :new_role")
    cursor_obj.execute("CREATE USER :username WITH PASSWORD '${userpwd}'")
    cursor_obj.execute("CREATE DATABASE :dbname")
    cursor_obj.execute("GRANT :new_role TO :username")


if __name__ == "__main__":
    for i in range(1, GROUPS + 1):
        for j in range(1, TEAMS + 1):
            create_db_and_user(i, j)
