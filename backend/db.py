import psycopg2


def get_connection():
    return psycopg2.connect(
        dbname="agriprice",
        user="rehanirani",
        host="localhost",
        port="5432"
    )