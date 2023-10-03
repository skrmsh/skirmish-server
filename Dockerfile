FROM python:3.8.10-slim-buster
COPY ./skirmserv /app/skirmserv
COPY ./gunicorn_conf.py /app/gunicorn_conf.py
WORKDIR /app/
RUN apt update
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
CMD ["gunicorn","-c","gunicorn_conf.py","--worker-class","geventwebsocket.gunicorn.workers.GeventWebSocketWorker","skirmserv:app","-b","0.0.0.0:8081"]
