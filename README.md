# Skirmish Server

## Setup
Install requirements using `pip install -r requirements.txt`

### Dev Server
To run the dev server execute the following in the base directory of this git:
```
env SKIRMSERV_CFG=default.cfg python3 -m skirmserv
```

### Gunicorn
To run the server using gunicorn, execute the following:
```
gunicorn -c gunicorn_conf.py --worker-class eventlet  skirmserv:app
```

## Copyright Notice
(C) 2022-2023 Ole Lange