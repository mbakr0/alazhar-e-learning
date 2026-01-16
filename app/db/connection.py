import psycopg2
from psycopg2 import pool
from app.core.config import USER, PASSWORD, HOST, PORT, DBNAME

db_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=50,
    host=HOST,
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    port=PORT
)