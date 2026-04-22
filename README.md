### Hexlet tests and linter status:
[![Actions Status](https://github.com/DonDetta/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/DonDetta/python-project-83/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=DonDetta_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=DonDetta_python-project-83)

### Demo:
https://python-project-83-render.onrender.com

---

## Анализатор страниц

Веб-приложение для SEO-анализа сайтов. Позволяет добавлять URL-адреса и проверять их на доступность, извлекая мета-информацию: заголовок страницы, тег h1 и описание (meta description).

## Требования

- Python >= 3.10
- PostgreSQL
- uv

## Установка

```bash
git clone https://github.com/DonDetta/python-project-83.git
cd python-project-83
make install
```

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните переменные окружения:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://localhost/page_analyzer
```

Создайте базу данных и примените схему:

```bash
createdb page_analyzer
psql -d page_analyzer -f database.sql
```

## Запуск

Режим разработки:

```bash
make dev
```

Продакшен:

```bash
make start
```

## Использование

1. Откройте приложение в браузере
2. Введите URL сайта в поле на главной странице и нажмите «Проверить»
3. После добавления сайта нажмите «Запустить проверку» — приложение выполнит запрос к сайту и сохранит код ответа, h1, title и description
4. Все добавленные сайты и результаты проверок доступны на странице «Сайты»