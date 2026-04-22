import os
from datetime import date
from urllib.parse import urlparse

import psycopg2
import requests
import validators
from dotenv import load_dotenv
from flask import (Flask, flash, redirect,
                   render_template, request, url_for)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_post():
    url = request.form.get('url', '').strip()

    errors = []
    if not url:
        errors.append('URL обязателен')
    elif len(url) > 255:
        errors.append('URL превышает 255 символов')
    elif not validators.url(url):
        errors.append('Некорректный URL')

    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('index.html', url=url), 422

    normalized = normalize_url(url)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name = %s', (normalized,))
            existing = cur.fetchone()
            if existing:
                flash('Страница уже существует', 'info')
                return redirect(url_for('urls_show', id=existing[0]))

            cur.execute(
                'INSERT INTO urls (name, created_at) '
                'VALUES (%s, %s) RETURNING id',
                (normalized, date.today())
            )
            new_id = cur.fetchone()[0]
            conn.commit()
    finally:
        conn.close()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_show', id=new_id))


@app.get('/urls')
def urls_index():
    conn = get_conn()
    try:
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
            urls = cur.fetchall()
    finally:
        conn.close()
    return render_template('urls/index.html', urls=urls)


@app.get('/urls/<int:id>')
def urls_show(id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, name, created_at FROM urls WHERE id = %s', (id,)
            )
            url = cur.fetchone()
            cur.execute('''
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks WHERE url_id = %s ORDER BY id DESC
            ''', (id,))
            checks = cur.fetchall()
    finally:
        conn.close()
    if not url:
        return render_template('404.html'), 404
    return render_template('urls/show.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def url_checks_post(id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT name FROM urls WHERE id = %s', (id,))
            row = cur.fetchone()
        if not row:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('urls_show', id=id))

        response = requests.get(row[0], timeout=10)
        response.raise_for_status()

        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO url_checks (url_id, status_code, created_at) '
                'VALUES (%s, %s, %s)',
                (id, response.status_code, date.today())
            )
            conn.commit()
        flash('Страница успешно проверена', 'success')
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
    finally:
        conn.close()
    return redirect(url_for('urls_show', id=id))
