# Skirmish Server

![Skirmish Logo - Showing the Text Skirmish and a phaser](https://raw.githubusercontent.com/skrmsh/skirmish-assets/main/logo/Logo_TextUnderlinedNoBackground.svg)

## Setup

Install requirements using `pip install -r requirements.txt`

### Dev Server

To run the dev server execute the following in the base directory of this git:

```
env DB_TYPE=sqlite DB_LOCATION=db_dev.sqlite3 LOGGING_LEVEL=DEBUG python3 -m skirmserv
```

### Gunicorn

To run the server using gunicorn, execute the following:

```
gunicorn -c gunicorn_conf.py --worker-class eventlet  skirmserv:app
```

### Config

Following config variables may be set via environment variables:

- `SECRET_KEY` - Secret key for flask
- `LOGGING_LEVEL` - One of DEBUG, INFO, WARNING, ERROR, CRITICAL
- `DB_TYPE` - One of sqlite, mysql or postgresql
- `DB_LOCATION` - sqlite db path
- `DB_HOST` - mysql/postgres host
- `DB_PORT` - mysql/postgres port
- `DB_DATABASE` - mysql/postgres database
- `DB_USER` - mysql/postgres user
- `DB_PASS` - mysql/postgres password

## Copyright Notice

(C) 2022-2023 Ole Lange
