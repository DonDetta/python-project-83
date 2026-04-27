import os
from datetime import date

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def get_url_by_name(conn, name):
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM urls WHERE name = %s', (name,))
        return cur.fetchone()


def add_url(conn, name):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
            (name, date.today())
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    return new_id


def get_all_urls(conn):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT u.id, u.name, uc.created_at, uc.status_code
            FROM urls u
            LEFT JOIN url_checks uc ON uc.id = (
                SELECT id FROM url_checks
                WHERE url_id = u.id
                ORDER BY id DESC LIMIT 1
            )
            ORDER BY u.id DESC
        ''')
        return cur.fetchall()


def get_url_by_id(conn, url_id):
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, name, created_at FROM urls WHERE id = %s', (url_id,)
        )
        return cur.fetchone()


def get_url_checks(conn, url_id):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks WHERE url_id = %s ORDER BY id DESC
        ''', (url_id,))
        return cur.fetchall()


def add_url_check(conn, url_id, status_code, h1, title, description):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO url_checks '
            '(url_id, status_code, h1, title, description, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (url_id, status_code, h1, title, description, date.today())
        )
    conn.commit()