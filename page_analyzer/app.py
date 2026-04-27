import os

import requests
import validators
from dotenv import load_dotenv
from flask import (Flask, flash, redirect,
                   render_template, request, url_for)

from page_analyzer.database import (
    add_url, add_url_check, get_all_urls,
    get_conn, get_url_by_id, get_url_by_name, get_url_checks,
)
from page_analyzer.parser import parse_page
from page_analyzer.url_normalizer import normalize_url

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


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
        existing = get_url_by_name(conn, normalized)
        if existing:
            flash('Страница уже существует', 'info')
            return redirect(url_for('urls_show', id=existing[0]))

        new_id = add_url(conn, normalized)
    finally:
        conn.close()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_show', id=new_id))


@app.get('/urls')
def urls_index():
    conn = get_conn()
    try:
        urls = get_all_urls(conn)
    finally:
        conn.close()
    return render_template('urls/index.html', urls=urls)


@app.get('/urls/<int:id>')
def urls_show(id):
    conn = get_conn()
    try:
        url = get_url_by_id(conn, id)
        checks = get_url_checks(conn, id)
    finally:
        conn.close()
    if not url:
        return render_template('404.html'), 404
    return render_template('urls/show.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def url_checks_post(id):
    conn = get_conn()
    try:
        url = get_url_by_id(conn, id)
        if not url:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('urls_show', id=id))

        response = requests.get(url[1], timeout=10)
        response.raise_for_status()

        parsed = parse_page(response.text)
        add_url_check(
            conn, id, response.status_code,
            parsed['h1'], parsed['title'], parsed['description']
        )
        flash('Страница успешно проверена', 'success')
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
    finally:
        conn.close()
    return redirect(url_for('urls_show', id=id))