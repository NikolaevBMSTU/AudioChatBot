FROM python:3.12.11-slim

RUN groupadd python && useradd -m -g python python
USER python:python

RUN pip install --no-cache-dir LangGraph LangChain


WORKDIR /app

COPY server.py /app
COPY agent.py /app
COPY chat_bot/ /app/chat_bot

ENTRYPOINT ["python3","server.py"]
