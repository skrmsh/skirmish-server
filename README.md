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

## Copyright Notice

(C) 2022-2023 Ole Lange
