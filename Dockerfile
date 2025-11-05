FROM python:3.13-slim

RUN groupadd python && useradd -m -g python python

RUN mkdir /var/log/bot && chown python. /var/log/bot

ENV LOG_DIR=/log

USER python:python

COPY requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app

COPY src/. /app/

ENTRYPOINT ["python3","bot.py"]
